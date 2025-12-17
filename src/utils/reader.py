# Import required libraries / 导入所需的库
import json  # JSON handling / JSON处理
from loguru import logger  # Logging library / 日志库
from eth_account import Account  # Ethereum account management / 以太坊账户管理
from eth_account.hdaccount import generate_mnemonic  # HD wallet mnemonic generation / HD钱包助记词生成
from web3.auto import w3  # Web3 library / Web3库


def read_txt_file(file_name: str, file_path: str) -> list:
    """
    Read lines from a text file
    从文本文件中读取行
    
    Args / 参数:
        file_name: Name of the file for logging / 用于日志记录的文件名
        file_path: Path to the file / 文件路径
        
    Returns / 返回:
        list: List of stripped lines / 去除空白的行列表
    """
    with open(file_path, "r") as file:
        items = [line.strip() for line in file]

    logger.success(f"Successfully loaded {len(items)} {file_name}.")
    return items


def split_list(lst, chunk_size=90):
    """
    Split a list into chunks of specified size
    将列表拆分为指定大小的块
    
    Args / 参数:
        lst: List to split / 要拆分的列表
        chunk_size: Size of each chunk / 每个块的大小
        
    Returns / 返回:
        list: List of chunks / 块列表
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def read_abi(path) -> dict:
    """
    Read ABI from JSON file
    从JSON文件读取ABI
    
    Args / 参数:
        path: Path to ABI file / ABI文件路径
        
    Returns / 返回:
        dict: ABI dictionary / ABI字典
    """
    with open(path, "r") as f:
        return json.load(f)


class InvalidKeyError(Exception):
    """
    Exception raised for invalid private keys or mnemonic phrases
    当私钥或助记词无效时引发的异常
    """
    pass


def read_private_keys(file_path: str) -> list:
    """
    Read private keys or mnemonic phrases from a file and return a list of private keys
    从文件中读取私钥或助记词并返回私钥列表
    
    If a line contains a mnemonic phrase, it will be converted to a private key
    如果一行包含助记词，它将被转换为私钥
    
    Security Note / 安全提示:
    - Validates all keys before accepting them / 在接受之前验证所有密钥
    - Supports both private keys and mnemonic phrases / 支持私钥和助记词
    - Uses eth_account's validation / 使用eth_account的验证

    Args / 参数:
        file_path: Path to the file containing private keys or mnemonic phrases / 包含私钥或助记词的文件路径

    Returns / 返回:
        list: List of private keys in hex format (with '0x' prefix) / 十六进制格式的私钥列表（带'0x'前缀）

    Raises / 异常:
        InvalidKeyError: If any key or mnemonic phrase in the file is invalid / 如果文件中的任何密钥或助记词无效
    """
    private_keys = []

    with open(file_path, "r") as file:
        for line_number, line in enumerate(file, 1):
            key = line.strip()
            if not key:
                continue  # Skip empty lines / 跳过空行

            try:
                # Check if the line is a mnemonic phrase (12 or 24 words) / 检查该行是否为助记词（12或24个单词）
                words = key.split()
                if len(words) in [12, 24]:
                    # Enable HD wallet features and convert mnemonic to private key / 启用HD钱包功能并将助记词转换为私钥
                    Account.enable_unaudited_hdwallet_features()
                    account = Account.from_mnemonic(key)
                    private_key = account.key.hex()
                else:
                    # Try to process as a private key / 尝试作为私钥处理
                    if not key.startswith("0x"):
                        key = "0x" + key
                    # Verify that it's a valid private key / 验证这是一个有效的私钥
                    Account.from_key(key)
                    private_key = key

                private_keys.append(private_key)

            except Exception as e:
                # Raise error with partial key for security (don't log full key) / 为安全起见，引发包含部分密钥的错误（不记录完整密钥）
                raise InvalidKeyError(
                    f"Invalid key or mnemonic phrase at line {line_number}: {key[:10]}... Error: {str(e)}"
                )

    logger.success(f"Successfully loaded {len(private_keys)} private keys.")
    return private_keys
