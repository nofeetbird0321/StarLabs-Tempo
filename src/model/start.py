# Import required libraries / 导入所需的库
from eth_account import Account  # Ethereum account management / 以太坊账户管理
from loguru import logger  # Logging library / 日志库
import primp  # HTTP client library / HTTP客户端库
import random  # Random number generation / 随机数生成
import asyncio  # Asynchronous programming / 异步编程

# Import dapp modules / 导入dapp模块
from src.model.dapps import onchaingm_gm, onchaingm_deploy, infinityname_mint
from src.model.tempo.instance import Tempo  # Tempo network operations / Tempo网络操作
from src.model.help.stats import WalletStats  # Wallet statistics / 钱包统计
from src.model.onchain.web3_custom import Web3Custom  # Custom Web3 wrapper / 自定义Web3包装器
from src.utils.client import create_client  # HTTP client creation / HTTP客户端创建
from src.utils.config import Config  # Configuration management / 配置管理
from src.model.database.db_manager import Database  # Database operations / 数据库操作
from src.utils.telegram_logger import send_telegram_message  # Telegram notifications / Telegram通知


class Start:
    """
    Main class for handling account operations and task execution
    处理账户操作和任务执行的主类
    
    This class manages the initialization and execution of tasks for a single account
    此类管理单个账户的任务初始化和执行
    """
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        config: Config,
    ):
        """
        Initialize the Start instance / 初始化Start实例
        
        Args / 参数:
            account_index: Account number / 账户编号
            proxy: Proxy connection string / 代理连接字符串
            private_key: Ethereum private key / 以太坊私钥
            config: Configuration object / 配置对象
        """
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.config = config

        # Initialize instances as None / 将实例初始化为None
        self.session: primp.AsyncClient | None = None  # HTTP session / HTTP会话
        self.tempo_web3: Web3Custom | None = None  # Web3 instance / Web3实例
        self.tempo_instance: Tempo | None = None  # Tempo operations instance / Tempo操作实例

        # Create wallet from private key / 从私钥创建钱包
        self.wallet = Account.from_key(self.private_key)
        self.wallet_address = self.wallet.address

    async def initialize(self):
        """
        Initialize HTTP session, Web3 connection, and Tempo instance
        初始化HTTP会话、Web3连接和Tempo实例
        
        Returns / 返回:
            bool: True if successful, False otherwise / 成功则为True，否则为False
        """
        try:
            # Create HTTP client with proxy / 使用代理创建HTTP客户端
            self.session = await create_client(
                self.proxy, self.config.OTHERS.SKIP_SSL_VERIFICATION
            )
            
            # Create Web3 connection to Tempo network / 创建到Tempo网络的Web3连接
            self.tempo_web3 = await Web3Custom.create(
                self.account_index,
                self.config.RPCS.TEMPO,
                self.config.OTHERS.USE_PROXY_FOR_RPC,
                self.proxy,
                self.config.OTHERS.SKIP_SSL_VERIFICATION,
            )

            # Initialize Tempo instance for operations / 初始化Tempo实例以进行操作
            self.tempo_instance = Tempo(
                self.account_index,
                self.session,
                self.tempo_web3,
                self.config,
                self.wallet,
                self.proxy,
            )
            
            return True
        except Exception as e:
            logger.error(f"{self.account_index} | Error: {e}")
            return False

    async def flow(self):
        """
        Main execution flow for the account
        账户的主执行流程
        
        Retrieves wallet statistics, gets pending tasks from database, and executes them
        检索钱包统计信息，从数据库获取待处理任务并执行它们
        
        Returns / 返回:
            bool: True if all tasks completed successfully / 所有任务成功完成则为True
        """
        try:
            # Try to get wallet statistics / 尝试获取钱包统计信息
            try:
                wallet_stats = WalletStats(self.config, self.tempo_web3)
                await wallet_stats.get_wallet_stats(
                    self.private_key, self.account_index
                )
            except Exception as e:
                pass  # Continue even if stats fail / 即使统计失败也继续

            # Initialize database connection / 初始化数据库连接
            db = Database()
            try:
                # Get pending tasks for this wallet / 获取此钱包的待处理任务
                tasks = await db.get_wallet_pending_tasks(self.private_key)
            except Exception as e:
                # Check for database not initialized error / 检查数据库未初始化错误
                if "no such table: wallets" in str(e):
                    logger.error(
                        f"{self.account_index} | Database not created or wallets table not found"
                    )
                    # Send error notification to Telegram if enabled / 如果启用，发送错误通知到Telegram
                    if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                        error_message = (
                            f"⚠️ Database error\n\n"
                            f"Account #{self.account_index}\n"
                            f"Wallet: <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n"
                            f"Error: Database not created or wallets table not found"
                        )
                        await send_telegram_message(self.config, error_message)
                    return False
                else:
                    logger.error(
                        f"{self.account_index} | Error getting tasks from database: {e}"
                    )
                    raise

            # Check if there are any tasks to execute / 检查是否有任务要执行
            if not tasks:
                logger.warning(
                    f"{self.account_index} | No pending tasks found in database for this wallet. Exiting..."
                )
                if self.tempo_web3:
                    await self.tempo_web3.cleanup()  # Cleanup resources / 清理资源
                return True

            # Display task execution plan / 显示任务执行计划
            task_plan_msg = [f"{i+1}. {task['name']}" for i, task in enumerate(tasks)]
            logger.info(
                f"{self.account_index} | Task execution plan: {' | '.join(task_plan_msg)}"
            )

            # Initialize task tracking lists / 初始化任务跟踪列表
            completed_tasks = []
            failed_tasks = []

            # Execute tasks / 执行任务
            for task in tasks:
                task_name = task["name"]

                # Skip tasks marked as "skip" / 跳过标记为"skip"的任务
                if task_name == "skip":
                    logger.info(f"{self.account_index} | Skipping task: {task_name}")
                    continue

                logger.info(f"{self.account_index} | Executing task: {task_name}")

                # Execute the task / 执行任务
                success = await self.execute_task(task_name)

                if success:
                    # Mark task as completed in database / 在数据库中将任务标记为已完成
                    await db.update_task_status(
                        self.private_key, task_name, "completed"
                    )
                    completed_tasks.append(task_name)
                    await self.sleep(task_name)  # Sleep after task / 任务后休眠
                else:
                    failed_tasks.append(task_name)
                    # Check if we should stop on failure / 检查是否应在失败时停止
                    if not self.config.FLOW.SKIP_FAILED_TASKS:
                        logger.error(
                            f"{self.account_index} | Failed to complete task {task_name}. Stopping wallet execution."
                        )
                        break
                    else:
                        logger.warning(
                            f"{self.account_index} | Failed to complete task {task_name}. Skipping to next task."
                        )
                        await self.sleep(task_name)

            # Send summary message to Telegram at the end / 在结束时发送摘要消息到Telegram
            if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                # Build report message / 构建报告消息
                message = (
                    f"🐰 Tempo Bot Report\n\n"
                    f"💳 Wallet: {self.account_index} | <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n\n"
                )

                # Add completed tasks section / 添加已完成任务部分
                if completed_tasks:
                    message += f"✅ Completed Tasks:\n"
                    for i, task in enumerate(completed_tasks, 1):
                        message += f"{i}. {task}\n"
                    message += "\n"

                # Add failed tasks section / 添加失败任务部分
                if failed_tasks:
                    message += f"❌ Failed Tasks:\n"
                    for i, task in enumerate(failed_tasks, 1):
                        message += f"{i}. {task}\n"
                    message += "\n"

                # Add statistics / 添加统计信息
                total_tasks = len(tasks)
                completed_count = len(completed_tasks)
                message += (
                    f"📊 Statistics:\n"
                    f"Total Tasks: {total_tasks}\n"
                    f"Completed: {completed_count}\n"
                    f"Failed: {len(failed_tasks)}\n"
                    f"Success Rate: {(completed_count/total_tasks)*100:.1f}%\n\n"
                    f"⚙️ Settings:\n"
                    f"Skip Failed: {'Yes' if self.config.FLOW.SKIP_FAILED_TASKS else 'No'}\n"
                )

                await send_telegram_message(self.config, message)

            # Return True only if all tasks succeeded / 仅当所有任务成功时返回True
            return len(failed_tasks) == 0

        except Exception as e:
            logger.error(f"{self.account_index} | Error: {e}")

            # Send error notification if Telegram logging enabled / 如果启用Telegram日志，发送错误通知
            if self.config.SETTINGS.SEND_TELEGRAM_LOGS:
                error_message = (
                    f"⚠️ Error Report\n\n"
                    f"Account #{self.account_index}\n"
                    f"Wallet: <code>{self.private_key[:6]}...{self.private_key[-4:]}</code>\n"
                    f"Error: {str(e)}"
                )
                await send_telegram_message(self.config, error_message)

            return False
        finally:
            # Cleanup resources / 清理资源
            try:
                if self.tempo_web3:
                    await self.tempo_web3.cleanup()  # Close Web3 connections / 关闭Web3连接
                logger.info(f"{self.account_index} | All sessions closed successfully")
            except Exception as e:
                logger.error(f"{self.account_index} | Error during cleanup: {e}")

    async def execute_task(self, task):
        """
        Execute a single task by name
        按名称执行单个任务
        
        Args / 参数:
            task: Name of the task to execute / 要执行的任务名称
            
        Returns / 返回:
            bool: True if task completed successfully / 任务成功完成则为True
        """
        task = task.lower()  # Convert to lowercase / 转换为小写

        # Faucet task - claim tokens / 水龙头任务 - 领取代币
        if task == "faucet":
            return await self.tempo_instance.faucet()

        # Token sender task - send tokens / 代币发送任务 - 发送代币
        if task == "token_sender":
            return await self.tempo_instance.send_random_token()

        # DEX swap task - swap tokens / DEX交换任务 - 交换代币
        if task == "dex_swaps":
            return await self.tempo_instance.perform_random_swaps()

        # OnchainGM GM task / OnchainGM GM任务
        if task == "onchaingm_gm":
            return await onchaingm_gm(self.account_index, self.session, self.tempo_web3, self.config, self.wallet)

        # OnchainGM deploy task / OnchainGM部署任务
        if task == "onchaingm_deploy":
            return await onchaingm_deploy(self.account_index, self.session, self.tempo_web3, self.config, self.wallet)

        # InfinityName domain mint task / InfinityName域名铸造任务
        if task == "infinityname_domain":
            return await infinityname_mint(self.account_index, self.session, self.tempo_web3, self.config, self.wallet)

        # Task not found / 未找到任务
        logger.error(f"{self.account_index} | Task {task} not found")
        return False

    async def sleep(self, task_name: str):
        """
        Makes a random pause between actions
        在操作之间进行随机暂停
        
        Args / 参数:
            task_name: Name of the task that was completed / 已完成的任务名称
        """
        # Generate random pause duration / 生成随机暂停持续时间
        pause = random.randint(
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
        )
        logger.info(
            f"{self.account_index} | Sleeping {pause} seconds after {task_name}"
        )
        await asyncio.sleep(pause)  # Sleep for specified duration / 休眠指定的持续时间
