# Import required libraries / 导入所需的库
import asyncio  # Asynchronous operations / 异步操作
import random  # Random number generation / 随机数生成
import secrets  # Cryptographically strong random numbers / 加密安全的随机数

import aiohttp  # Async HTTP client / 异步HTTP客户端
import primp  # HTTP client library / HTTP客户端库
from eth_account import Account  # Ethereum account management / 以太坊账户管理
from loguru import logger  # Logging library / 日志库

from src.model.onchain.web3_custom import Web3Custom  # Custom Web3 wrapper / 自定义Web3包装器
from src.model.tempo.constants import TEMPO_TOKENS, ERC20_TRANSFER_ABI  # Token constants / 代币常量
from src.utils.config import Config  # Configuration / 配置
from src.utils.constants import EXPLORER_URL_TEMPO, CHAIN_ID  # Chain constants / 链常量
from src.utils.decorators import retry_async  # Retry decorator / 重试装饰器


class Tempo:
    """
    Tempo network operations handler
    Tempo网络操作处理器
    
    Manages faucet claiming, token transfers, and balance checking on Tempo testnet
    管理Tempo测试网上的水龙头领取、代币转账和余额检查
    """
    def __init__(
        self,
        account_index: int,
        session: primp.AsyncClient,
        web3: Web3Custom,
        config: Config,
        wallet: Account,
        proxy: str,
    ):
        """
        Initialize Tempo instance / 初始化Tempo实例
        
        Args / 参数:
            account_index: Account number / 账户编号
            session: HTTP client session / HTTP客户端会话
            web3: Web3 instance / Web3实例
            config: Configuration object / 配置对象
            wallet: Ethereum wallet / 以太坊钱包
            proxy: Proxy connection string / 代理连接字符串
        """
        self.account_index = account_index
        self.session = session
        self.web3 = web3
        self.config = config
        self.wallet = wallet
        self.proxy = proxy

    async def _get_ws_connection(self):
        """
        Create WebSocket connection to Tempo RPC
        创建到Tempo RPC的WebSocket连接
        
        Returns / 返回:
            tuple: (session, websocket) - Session and WebSocket objects / 会话和WebSocket对象
        """
        # Format proxy URL / 格式化代理URL
        proxy_url = f"http://{self.proxy}"
        
        # Create aiohttp session / 创建aiohttp会话
        session = aiohttp.ClientSession()
        
        # Connect to Tempo WebSocket RPC / 连接到Tempo WebSocket RPC
        ws = await session.ws_connect(
            "wss://rpc.testnet.tempo.xyz/",
            proxy=proxy_url,
            headers={
                "Origin": "https://docs.tempo.xyz",
                "Cache-Control": "no-cache",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,zh-TW;q=0.7,zh;q=0.6,uk;q=0.5",
                "Pragma": "no-cache",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            },
        )
        return session, ws

    @retry_async(default_value=False)
    async def faucet(self) -> bool:
        """
        Claim tokens from Tempo testnet faucet
        从Tempo测试网水龙头领取代币
        
        Connects via WebSocket and calls tempo_fundAddress method
        通过WebSocket连接并调用tempo_fundAddress方法
        
        Returns / 返回:
            bool: True if successful, False otherwise / 成功则为True，否则为False
        """
        session = None
        ws = None
        try:
            # Establish WebSocket connection / 建立WebSocket连接
            session, ws = await self._get_ws_connection()

            # Generate random request ID / 生成随机请求ID
            request_id = random.randint(1, 1000)
            
            # Send faucet request / 发送水龙头请求
            await ws.send_json({
                "id": request_id,
                "jsonrpc": "2.0",
                "method": "tempo_fundAddress",
                "params": [self.wallet.address]
            })

            # Receive response / 接收响应
            response = await ws.receive_json()

            # Check if request was successful / 检查请求是否成功
            if "result" in response:
                tx_hashes = response["result"]
                # Log transaction hashes / 记录交易哈希
                for tx_hash in tx_hashes:
                    logger.success(
                        f"{self.account_index} | Faucet TX: {EXPLORER_URL_TEMPO}{tx_hash[2:]}"
                    )
                await asyncio.sleep(3)  # Wait for confirmations / 等待确认
                await self.check_balances()  # Check new balances / 检查新余额
                return True
            else:
                raise Exception(f"Faucet failed: {response}")

        except Exception as e:
            # Random pause before retry / 重试前的随机暂停
            random_pause = random.randint(
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(
                f"{self.account_index} | Faucet error: {e}"
            )
            await asyncio.sleep(random_pause)
            raise
        finally:
            # Always close connections / 始终关闭连接
            if ws:
                await ws.close()
            if session:
                await session.close()

    async def check_balances(self) -> dict:
        """
        Check and display token balances for the wallet
        检查并显示钱包的代币余额
        
        Returns / 返回:
            dict: Dictionary of token balances / 代币余额字典
        """
        balances = {}

        # Iterate through all Tempo tokens / 遍历所有Tempo代币
        for token in TEMPO_TOKENS:
            # Get token balance / 获取代币余额
            balance = await self.web3.get_token_balance(
                wallet_address=self.wallet.address,
                token_address=token["address"],
                decimals=token["decimals"],
                symbol=token["symbol"],
            )
            balances[token["symbol"]] = balance
            
            # Format and log balance / 格式化并记录余额
            amount = f"{balance.formatted:.6f}" if balance else "0"
            logger.info(f"{self.account_index} | {token['symbol']}: {amount}")

        return balances

    async def send_random_token(self) -> bool:
        """
        Send random tokens multiple times according to configuration
        根据配置多次发送随机代币
        
        Returns / 返回:
            bool: True if all transactions successful / 所有交易成功则为True
        """
        # Determine number of transactions to send / 确定要发送的交易数量
        num_transactions = random.randint(
            self.config.TOKEN_SENDER.NUMBER_OF_TRANSACTIONS_TO_SEND[0],
            self.config.TOKEN_SENDER.NUMBER_OF_TRANSACTIONS_TO_SEND[1],
        )
        logger.info(f"{self.account_index} | Will send {num_transactions} token transactions")
        
        # Send each transaction / 发送每笔交易
        for tx_num in range(1, num_transactions + 1):
            success = await self._send_single_token(tx_num, num_transactions)
            if not success:
                return False
            
            # Pause between transactions (except after last one) / 交易之间暂停（最后一笔除外）
            if tx_num < num_transactions:
                pause = random.randint(
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
                    self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
                )
                logger.info(f"{self.account_index} | Pausing {pause}s before next transaction")
                await asyncio.sleep(pause)
        
        return True

    @retry_async(default_value=False)
    async def _send_single_token(self, tx_num: int, total_txs: int) -> bool:
        """
        Send a single token transaction
        发送单个代币交易
        
        Args / 参数:
            tx_num: Current transaction number / 当前交易编号
            total_txs: Total number of transactions to send / 要发送的总交易数
            
        Returns / 返回:
            bool: True if successful / 成功则为True
        """
        try:
            # Randomly select a token to send / 随机选择要发送的代币
            token = random.choice(TEMPO_TOKENS)
            
            # Get current token balance / 获取当前代币余额
            balance = await self.web3.get_token_balance(
                wallet_address=self.wallet.address,
                token_address=token["address"],
                decimals=token["decimals"],
                symbol=token["symbol"],
            )
            
            # Check if we have balance to send / 检查是否有余额可发送
            if not balance or balance.wei == 0:
                logger.warning(f"{self.account_index} | No {token['symbol']} balance to send")
                return False
            
            # Calculate amount to send (random percentage of balance) / 计算要发送的金额（余额的随机百分比）
            send_percent = random.uniform(
                self.config.TOKEN_SENDER.PERCENT_OF_BALANCE_TO_SEND[0] / 100,
                self.config.TOKEN_SENDER.PERCENT_OF_BALANCE_TO_SEND[1] / 100,
            )
            token_unit = 10 ** token["decimals"]
            amount_to_send = int(balance.wei * send_percent)
            # Round down to token unit / 向下舍入到代币单位
            amount_to_send = (amount_to_send // token_unit) * token_unit
            
            # Verify amount is not too small / 验证金额不会太小
            if amount_to_send == 0:
                logger.warning(f"{self.account_index} | Amount to send is too small")
                return False
            
            # Determine recipient address / 确定收件人地址
            if self.config.TOKEN_SENDER.SEND_TOKENS_TO_MY_WALLETS:
                # Send to one of our own wallets / 发送到我们自己的钱包之一
                async with self.config.lock:
                    available_wallets = [
                        w for w in self.config.WALLETS.wallets 
                        if w.address.lower() != self.wallet.address.lower()
                    ]
                
                if not available_wallets:
                    logger.warning(f"{self.account_index} | No other wallets available to send to")
                    return False
                
                target_wallet = random.choice(available_wallets)
                to_address = target_wallet.address
                logger.info(f"{self.account_index} | [{tx_num}/{total_txs}] Sending to own wallet #{target_wallet.account_index}")
            else:
                # Generate a random address (using cryptographically secure random) / 生成随机地址（使用加密安全的随机）
                random_bytes = secrets.token_bytes(20)
                to_address = self.web3.web3.to_checksum_address("0x" + random_bytes.hex())
                logger.info(f"{self.account_index} | [{tx_num}/{total_txs}] Sending to random address: {to_address}")
            
            # Create token contract instance / 创建代币合约实例
            token_contract = self.web3.web3.eth.contract(
                address=self.web3.web3.to_checksum_address(token["address"]),
                abi=ERC20_TRANSFER_ABI
            )
            
            # Format amount for logging / 格式化金额以进行日志记录
            formatted_amount = amount_to_send // token_unit
            logger.info(f"{self.account_index} | [{tx_num}/{total_txs}] Sending {formatted_amount} {token['symbol']} to {to_address}")
            
            # Build transfer transaction / 构建转账交易
            tx = await token_contract.functions.transfer(
                self.web3.web3.to_checksum_address(to_address),
                amount_to_send
            ).build_transaction({
                'chainId': CHAIN_ID,
                'from': self.wallet.address,
                'nonce': await self.web3.web3.eth.get_transaction_count(self.wallet.address),
                'gasPrice': await self.web3.web3.eth.gas_price,
            })
            # Estimate gas and add to transaction / 估算gas并添加到交易
            tx['gas'] = await self.web3.web3.eth.estimate_gas(tx)
            
            # Sign transaction with private key / 使用私钥签名交易
            signed_tx = self.web3.web3.eth.account.sign_transaction(tx, self.wallet.key)
            
            # Send signed transaction / 发送签名的交易
            tx_hash = await self.web3.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for transaction receipt / 等待交易收据
            rcpt = await self.web3.web3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=2)
            
            # Check transaction status / 检查交易状态
            if rcpt['status'] != 1:
                raise Exception('Token transfer transaction failed')
            
            # Log successful transaction / 记录成功的交易
            logger.success(f"{self.account_index} | [{tx_num}/{total_txs}] Token sent! TX: {EXPLORER_URL_TEMPO}{rcpt['transactionHash'].hex()}")
            return True
            
        except Exception as e:
            # Random pause before retry / 重试前的随机暂停
            random_pause = random.randint(
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                self.config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.error(f"{self.account_index} | [{tx_num}/{total_txs}] Send token error: {e}")
            await asyncio.sleep(random_pause)
            raise
