# Import required libraries / 导入所需的库
import primp  # HTTP client library / HTTP客户端库
import secrets  # Cryptographically secure random numbers / 加密安全的随机数
from curl_cffi import AsyncSession  # Async HTTP session with curl_cffi / 使用curl_cffi的异步HTTP会话


async def create_client(proxy: str, skip_ssl_verification: bool = True) -> AsyncSession:
    """
    Create an async HTTP client session with proxy support
    创建支持代理的异步HTTP客户端会话
    
    Args / 参数:
        proxy: Proxy connection string (format: user:pass@host:port) / 代理连接字符串（格式：user:pass@host:port）
        skip_ssl_verification: Whether to skip SSL verification / 是否跳过SSL验证
        
    Returns / 返回:
        AsyncSession: Configured HTTP session / 配置的HTTP会话
        
    Security Note / 安全提示:
    - Uses impersonation to avoid detection / 使用伪装以避免检测
    - SSL verification can be disabled (use with caution) / 可以禁用SSL验证（谨慎使用）
    """
    # Create session with browser impersonation / 使用浏览器伪装创建会话
    session = AsyncSession(
        impersonate="chrome131",
        verify=not skip_ssl_verification,
        timeout=30,
    )
    
    # Configure proxy if provided / 如果提供则配置代理
    if proxy:
        session.proxies.update(
            {
                "http": "http://" + proxy,
                "https": "http://" + proxy,
            }
        )

    # Update headers / 更新请求头
    session.headers.update(HEADERS)

    return session


# Default HTTP headers for requests / 请求的默认HTTP标头
# These headers mimic a real browser to avoid detection / 这些标头模仿真实浏览器以避免检测
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-TW;q=0.6,zh;q=0.5",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

async def create_twitter_client(proxy: str, auth_token: str) -> primp.AsyncClient:
    """
    Create an async Twitter API client session
    创建异步Twitter API客户端会话
    
    Args / 参数:
        proxy: Proxy connection string / 代理连接字符串
        auth_token: Twitter authentication token / Twitter认证令牌
        
    Returns / 返回:
        primp.AsyncClient: Configured Twitter client / 配置的Twitter客户端
        
    Security Note / 安全提示:
    - Generates secure CSRF token / 生成安全的CSRF令牌
    - Requires valid auth_token (should be kept secret) / 需要有效的auth_token（应保密）
    """
    # Create session with browser impersonation / 使用浏览器伪装创建会话
    session = primp.AsyncClient(impersonate="chrome_133")

    # Configure proxy if provided / 如果提供则配置代理
    if proxy:
        session.proxies.update(
            {
                "http": "http://" + proxy,
                "https": "http://" + proxy,
            }
        )

    session.timeout_seconds = 30

    # Generate cryptographically secure CSRF token / 生成加密安全的CSRF令牌
    generated_csrf_token = secrets.token_hex(16)

    # Set cookies for authentication / 设置认证cookie
    cookies = {"ct0": generated_csrf_token, "auth_token": auth_token}
    headers = {"x-csrf-token": generated_csrf_token}

    session.headers.update(headers)
    session.cookies.update(cookies)

    session.headers["x-csrf-token"] = generated_csrf_token

    # Get and set Twitter-specific headers / 获取并设置Twitter特定的请求头
    session.headers = get_headers(session)

    return session


def get_headers(session: primp.AsyncClient, **kwargs) -> dict:
    """
    Get the headers required for authenticated Twitter API requests
    获取Twitter API认证请求所需的请求头
    
    Args / 参数:
        session: HTTP client session / HTTP客户端会话
        **kwargs: Additional headers / 额外的请求头
        
    Returns / 返回:
        dict: Dictionary of headers / 请求头字典
        
    Security Note / 安全提示:
    - Uses Twitter's public bearer token (not a secret) / 使用Twitter的公共bearer令牌（不是秘密）
    - CSRF token is dynamically generated / CSRF令牌是动态生成的
    """
    cookies = session.cookies

    # Build headers with Twitter API requirements / 使用Twitter API要求构建请求头
    headers = kwargs | {
        # This is Twitter's public API bearer token, not a secret / 这是Twitter的公共API bearer令牌，不是秘密
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        # "cookie": "; ".join(f"{k}={v}" for k, v in cookies.items()),
        "referer": "https://x.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-csrf-token": cookies.get("ct0", ""),
        # "x-guest-token": cookies.get("guest_token", ""),
        "x-twitter-auth-type": "OAuth2Session" if cookies.get("auth_token") else "",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
    }
    # Sort headers alphabetically / 按字母顺序排序请求头
    return dict(sorted({k.lower(): v for k, v in headers.items()}.items()))
