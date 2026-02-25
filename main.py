# Import required libraries / 导入所需的库
from loguru import logger  # Logging library / 日志库
import urllib3  # HTTP library for disabling SSL warnings / 用于禁用SSL警告的HTTP库
import sys  # System-specific parameters and functions / 系统特定参数和函数
import asyncio  # Asynchronous I/O library / 异步I/O库
import platform  # Access to underlying platform's identifying data / 访问底层平台的标识数据
import logging  # Python's built-in logging / Python内置日志
import argparse  # Command-line argument parsing / 命令行参数解析

from process import start  # Main process flow / 主流程
from src.utils.output import show_logo, show_dev_info  # Display utilities / 显示工具
from src.utils.check_github_version import check_version  # Version checking / 版本检查

# Windows-specific event loop policy for asyncio / Windows系统的asyncio事件循环策略
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    """
    Main entry point of the application
    应用程序的主入口点

    Displays logo and developer info, configures logging, then starts the bot
    显示logo和开发者信息，配置日志，然后启动机器人
    """
    # Parse command-line arguments / 解析命令行参数
    parser = argparse.ArgumentParser(
        description="StarLabs Tempo Bot - Automated Tempo Network Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--auto",
        "--start",
        action="store_true",
        help="Automatically start farming (bypass menu selection)",
    )
    parser.add_argument(
        "--option",
        "-o",
        type=int,
        choices=[1, 2, 3, 4],
        help="Select menu option directly (1: Start farming, 2: Edit config, 3: Database actions, 4: Exit)",
    )
    parser.add_argument(
        "--no-logo",
        action="store_true",
        help="Skip logo and dev info display",
    )

    args = parser.parse_args()

    # Display logo and info unless suppressed / 除非被抑制，否则显示logo和信息
    if not args.no_logo:
        show_logo()  # Display ASCII art logo / 显示ASCII艺术logo
        show_dev_info()  # Display developer information / 显示开发者信息

    configuration()  # Configure logging and warnings / 配置日志和警告

    # Pass command-line arguments to start function / 将命令行参数传递给start函数
    await start(auto_start=args.auto, selected_option=args.option)  # Start the main process / 启动主流程


# Log format with colors and timestamp / 带颜色和时间戳的日志格式
log_format = (
    "<light-blue>[</light-blue><yellow>{time:HH:mm:ss}</yellow><light-blue>]</light-blue> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file}:{line}</cyan> | "
    "<level>{message}</level>"
)


def configuration():
    """
    Configure logging and warnings for the application
    配置应用程序的日志和警告
    
    - Disables urllib3 SSL warnings / 禁用urllib3 SSL警告
    - Sets up loguru logger with custom format / 使用自定义格式设置loguru日志记录器
    - Configures log rotation and retention / 配置日志轮转和保留
    """
    # Disable SSL warnings to avoid cluttering logs / 禁用SSL警告以避免日志混乱
    urllib3.disable_warnings()
    
    # Remove default logger to add custom configuration / 删除默认日志记录器以添加自定义配置
    logger.remove()

    # Disable primp and web3 logging to reduce noise / 禁用primp和web3日志以减少噪音
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("web3").setLevel(logging.WARNING)
    
    # Suppress asyncio ConnectionResetError warnings on Windows / 在Windows上抑制asyncio连接重置错误警告
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    # Add console logger with colors / 添加带颜色的控制台日志记录器
    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
    )
    
    # Add file logger with rotation / 添加带轮转的文件日志记录器
    logger.add(
        "logs/app.log",
        rotation="10 MB",  # Rotate when file reaches 10 MB / 文件达到10 MB时轮转
        retention="1 month",  # Keep logs for 1 month / 保留1个月的日志
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} - {message}",
        level="INFO",
    )

if __name__ == "__main__":
    asyncio.run(main())
