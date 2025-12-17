# Import required libraries / 导入所需的库
import asyncio  # Asynchronous operations / 异步操作
from aiogram import Bot  # Telegram bot library / Telegram机器人库
from aiogram.enums import ParseMode  # Message parsing modes / 消息解析模式
from src.utils.config import Config  # Configuration / 配置


async def send_telegram_message(config: Config, message: str) -> None:
    """
    Send a message to Telegram users using the bot token from config
    使用配置中的机器人令牌向Telegram用户发送消息
    
    Args / 参数:
        config: Configuration object containing bot token and user IDs / 包含机器人令牌和用户ID的配置对象
        message: Message text to send (supports HTML formatting) / 要发送的消息文本（支持HTML格式）
        
    Security Note / 安全提示:
    - Bot token should be kept secret / 机器人令牌应保密
    - Only sends to configured user IDs / 仅发送到配置的用户ID
    """
    # Create bot instance with token from config / 使用配置中的令牌创建机器人实例
    bot = Bot(token=config.SETTINGS.TELEGRAM_BOT_TOKEN)

    # Send message to each configured user / 向每个配置的用户发送消息
    for user_id in config.SETTINGS.TELEGRAM_USERS_IDS:
        await bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
        await asyncio.sleep(1)  # Rate limiting / 速率限制
        
    # Close bot session / 关闭机器人会话
    await bot.session.close()
