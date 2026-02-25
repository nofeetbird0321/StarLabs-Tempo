# Import required libraries / 导入所需的库
import asyncio  # Asynchronous programming support / 异步编程支持
import random  # Random number generation / 随机数生成
from loguru import logger  # Logging library / 日志库
from eth_account import Account  # Ethereum account management / 以太坊账户管理


import src.utils  # Utility functions / 工具函数
from src.utils.output import show_dev_info, show_logo  # Display utilities / 显示工具
from src.utils.proxy_parser import Proxy  # Proxy parsing / 代理解析
import src.model  # Data models / 数据模型
from src.utils.statistics import print_wallets_stats  # Statistics display / 统计显示
from src.utils.check_github_version import check_version  # Version check / 版本检查
from src.utils.logs import ProgressTracker, create_progress_tracker  # Progress tracking / 进度跟踪
from src.utils.config_browser import run  # Configuration browser / 配置浏览器
from src.utils.config import WalletInfo  # Wallet information / 钱包信息

async def start(auto_start: bool = False, selected_option: int = None):
    """
    Main process entry point - handles menu selection and account processing
    主流程入口点 - 处理菜单选择和账户处理

    Args:
        auto_start: Automatically start farming without menu / 自动开始farming无需菜单
        selected_option: Pre-selected menu option (1-4) / 预选菜单选项(1-4)

    Features / 功能:
    - Version checking / 版本检查
    - Menu-based operation / 基于菜单的操作
    - Multi-threaded account processing / 多线程账户处理
    - Progress tracking / 进度跟踪
    """
    async def launch_wrapper(index, proxy, private_key):
        """
        Wrapper function to launch account flow with semaphore control
        使用信号量控制启动账户流程的包装函数
        """
        async with semaphore:
            await account_flow(
                index,
                proxy,
                private_key,
                config,
                lock,
                progress_tracker,
            )

    # Check for latest version from GitHub / 从GitHub检查最新版本
    try:
        await check_version("0xStarLabs", "StarLabs-Tempo")
        pass
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Failed to check version: {e}")
        logger.info("Continue with current version\n")

    # Handle auto-start or direct option selection / 处理自动启动或直接选项选择
    if auto_start:
        choice = "1"
        logger.info("Auto-start enabled, beginning farming...")
    elif selected_option is not None:
        choice = str(selected_option)
        logger.info(f"Direct option selected: {choice}")
    else:
        # Display main menu / 显示主菜单
        print("\nAvailable options:\n")
        print("[1] ⭐️ Start farming")  # Begin automated tasks / 开始自动化任务
        print("[2] 🔧 Edit config")  # Modify configuration / 修改配置
        print("[3] 💾 Database actions")  # Manage database / 管理数据库
        print("[4] 👋 Exit")  # Close application / 关闭应用程序
        print()

        # Get user input with error handling / 获取用户输入并进行错误处理
        try:
            choice = input("Enter option (1-4): ").strip()
        except Exception as e:
            logger.error(f"Input error: {e}")
            return

    # Process menu selection / 处理菜单选择
    if choice == "4" or not choice:
        return  # Exit application / 退出应用程序
    elif choice == "2":
        run()  # Open config editor / 打开配置编辑器
        return
    elif choice == "1":
        pass  # Continue to farming / 继续进行farming
    elif choice == "3":
        from src.model.database.db_manager import show_database_menu

        await show_database_menu()  # Show database management menu / 显示数据库管理菜单
        await start()  # Return to main menu / 返回主菜单
    else:
        logger.error(f"Invalid choice: {choice}")
        return

    # Load configuration from config.yaml / 从config.yaml加载配置
    config = src.utils.get_config()

    # Load proxies using proxy parser / 使用代理解析器加载代理
    try:
        proxy_objects = Proxy.from_file("data/proxies.txt")  # Read proxy file / 读取代理文件
        proxies = [proxy.get_default_format() for proxy in proxy_objects]  # Format proxies / 格式化代理
        if len(proxies) == 0:
            logger.error("No proxies found in data/proxies.txt")
            return
    except Exception as e:
        logger.error(f"Failed to load proxies: {e}")
        return

    # Load private keys from file / 从文件加载私钥
    private_keys = src.utils.read_private_keys("data/private_keys.txt")

    # Determine account range to process / 确定要处理的账户范围
    # Define account range / 定义账户范围
    start_index = config.SETTINGS.ACCOUNTS_RANGE[0]
    end_index = config.SETTINGS.ACCOUNTS_RANGE[1]

    # If both are 0, check EXACT_ACCOUNTS_TO_USE / 如果两者都是0，检查EXACT_ACCOUNTS_TO_USE
    if start_index == 0 and end_index == 0:
        if config.SETTINGS.EXACT_ACCOUNTS_TO_USE:
            # Convert account numbers to indices (number - 1) / 将账户号转换为索引（号码-1）
            selected_indices = [i - 1 for i in config.SETTINGS.EXACT_ACCOUNTS_TO_USE]
            accounts_to_process = [private_keys[i] for i in selected_indices]
            logger.info(
                f"Using specific accounts: {config.SETTINGS.EXACT_ACCOUNTS_TO_USE}"
            )

            # For compatibility with rest of code / 为了与其余代码兼容
            start_index = min(config.SETTINGS.EXACT_ACCOUNTS_TO_USE)
            end_index = max(config.SETTINGS.EXACT_ACCOUNTS_TO_USE)
        else:
            # If list is empty, use all accounts as before / 如果列表为空，则像以前一样使用所有账户
            accounts_to_process = private_keys
            start_index = 1
            end_index = len(private_keys)
    else:
        # Python slice doesn't include last element, so +1 / Python切片不包括最后一个元素，所以+1
        accounts_to_process = private_keys[start_index - 1 : end_index]

    # Get number of concurrent threads / 获取并发线程数
    threads = config.SETTINGS.THREADS

    # Prepare proxies for selected accounts (cycle through proxy list) / 为选定的账户准备代理（循环使用代理列表）
    cycled_proxies = [
        proxies[i % len(proxies)] for i in range(len(accounts_to_process))
    ]

    # Create list of indices / 创建索引列表
    indices = list(range(len(accounts_to_process)))

    # Shuffle indices only if SHUFFLE_WALLETS is enabled / 仅当启用SHUFFLE_WALLETS时才打乱索引
    if config.SETTINGS.SHUFFLE_WALLETS:
        random.shuffle(indices)  # Randomize order / 随机顺序
        shuffle_status = "random"
    else:
        shuffle_status = "sequential"  # Keep sequential order / 保持顺序

    # Create string with account order / 创建账户顺序字符串
    if config.SETTINGS.EXACT_ACCOUNTS_TO_USE:
        # Create list of account numbers in required order / 按所需顺序创建账户号列表
        ordered_accounts = [config.SETTINGS.EXACT_ACCOUNTS_TO_USE[i] for i in indices]
        account_order = " ".join(map(str, ordered_accounts))
        logger.info(f"Starting with specific accounts in {shuffle_status} order...")
    else:
        account_order = " ".join(str(start_index + idx) for idx in indices)
        logger.info(
            f"Starting with accounts {start_index} to {end_index} in {shuffle_status} order..."
        )
    logger.info(f"Accounts order: {account_order}")

    # Populate wallets in config for token sender / 在配置中填充钱包信息以用于代币发送器
    for idx, pk in enumerate(accounts_to_process):
        account = Account.from_key(pk)  # Create account from private key / 从私钥创建账户
        # Calculate actual index / 计算实际索引
        actual_idx = (
            config.SETTINGS.EXACT_ACCOUNTS_TO_USE[idx]
            if config.SETTINGS.EXACT_ACCOUNTS_TO_USE
            else start_index + idx
        )
        # Create wallet info object / 创建钱包信息对象
        wallet_info = WalletInfo(
            account_index=actual_idx,
            private_key=pk,
            address=account.address,
            balance=0.0,
            transactions=0,
        )
        config.WALLETS.wallets.append(wallet_info)

    # Create async lock for thread-safe operations / 创建异步锁以进行线程安全操作
    lock = asyncio.Lock()
    # Create semaphore to limit concurrent tasks / 创建信号量以限制并发任务
    semaphore = asyncio.Semaphore(value=threads)
    tasks = []

    # Create progress tracker before creating tasks / 在创建任务之前创建进度跟踪器
    progress_tracker = await create_progress_tracker(
        total=len(accounts_to_process), description="Accounts completed"
    )

    # Use indices to create tasks / 使用索引创建任务
    for idx in indices:
        # Calculate actual account index / 计算实际账户索引
        actual_index = (
            config.SETTINGS.EXACT_ACCOUNTS_TO_USE[idx]
            if config.SETTINGS.EXACT_ACCOUNTS_TO_USE
            else start_index + idx
        )
        # Create async task for each account / 为每个账户创建异步任务
        tasks.append(
            asyncio.create_task(
                launch_wrapper(
                    actual_index,
                    cycled_proxies[idx],
                    accounts_to_process[idx],
                )
            )
        )

    # Wait for all tasks to complete / 等待所有任务完成
    await asyncio.gather(*tasks)

    # Log success message / 记录成功消息
    logger.success("Saved accounts and private keys to a file.")

    # Display wallet statistics / 显示钱包统计信息
    print_wallets_stats(config)

    # Wait for user input before closing / 关闭前等待用户输入
    input("Press Enter to continue...")


async def account_flow(
    account_index: int,
    proxy: str,
    private_key: str,
    config: src.utils.config.Config,
    lock: asyncio.Lock,
    progress_tracker: ProgressTracker,
):
    """
    Main flow for processing a single account
    处理单个账户的主流程
    
    Args / 参数:
        account_index: Account number / 账户编号
        proxy: Proxy connection string / 代理连接字符串
        private_key: Ethereum private key / 以太坊私钥
        config: Configuration object / 配置对象
        lock: Async lock for thread safety / 线程安全的异步锁
        progress_tracker: Progress tracking object / 进度跟踪对象
    """
    try:
        # Random pause before starting / 开始前的随机暂停
        pause = random.randint(
            config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[0],
            config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[1],
        )
        logger.info(f"[{account_index}] Sleeping for {pause} seconds before start...")
        await asyncio.sleep(pause)

        # Create instance for this account / 为此账户创建实例
        instance = src.model.Start(account_index, proxy, private_key, config)

        # Initialize the instance / 初始化实例
        result = await wrapper(instance.initialize, config)
        if not result:
            raise Exception("Failed to initialize")

        # Execute the flow / 执行流程
        result = await wrapper(instance.flow, config)
        if not result:
            report = True

        # Random pause before next account / 处理下一个账户前的随机暂停
        pause = random.randint(
            config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[0],
            config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[1],
        )
        logger.info(f"Sleeping for {pause} seconds before next account...")
        await asyncio.sleep(pause)

        # Update progress tracker / 更新进度跟踪器
        await progress_tracker.increment(1)

    except Exception as err:
        logger.error(f"{account_index} | Account flow failed: {err}")
        # Update progress even if there's an error / 即使出错也要更新进度
        await progress_tracker.increment(1)


async def wrapper(function, config: src.utils.config.Config, *args, **kwargs):
    """
    Wrapper function for retrying failed operations
    用于重试失败操作的包装函数
    
    Args / 参数:
        function: Function to execute / 要执行的函数
        config: Configuration object / 配置对象
        *args, **kwargs: Function arguments / 函数参数
        
    Returns / 返回:
        Result of the function / 函数的结果
    """
    # Get number of attempts from config / 从配置获取尝试次数
    attempts = config.SETTINGS.ATTEMPTS
    attempts = 1  # Override to 1 attempt / 覆盖为1次尝试
    
    # Try executing the function / 尝试执行函数
    for attempt in range(attempts):
        result = await function(*args, **kwargs)
        
        # Check if result is successful / 检查结果是否成功
        if isinstance(result, tuple) and result and isinstance(result[0], bool):
            if result[0]:
                return result
        elif isinstance(result, bool):
            if result:
                return True

        # Don't sleep after the last attempt / 最后一次尝试后不要休眠
        if attempt < attempts - 1:
            pause = random.randint(
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.info(
                f"Sleeping for {pause} seconds before next attempt {attempt+1}/{config.SETTINGS.ATTEMPTS}..."
            )
            await asyncio.sleep(pause)

    return result


def task_exists_in_config(task_name: str, tasks_list: list) -> bool:
    """
    Recursively checks if a task exists in the task list, including nested lists
    递归检查任务列表中是否存在任务，包括嵌套列表
    
    Args / 参数:
        task_name: Name of the task to find / 要查找的任务名称
        tasks_list: List of tasks to search / 要搜索的任务列表
        
    Returns / 返回:
        bool: True if task exists, False otherwise / 如果任务存在则为True，否则为False
    """
    for task in tasks_list:
        if isinstance(task, list):
            # Recursively check nested lists / 递归检查嵌套列表
            if task_exists_in_config(task_name, task):
                return True
        elif task == task_name:
            return True
    return False
