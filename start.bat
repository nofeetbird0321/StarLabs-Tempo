@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo ================================================
echo   StarLabs Tempo Bot - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed!
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [+] Python detected
echo.

REM Setup virtual environment
if not exist venv (
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [X] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment exists
)

echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check and install dependencies
echo [*] Checking dependencies...
python -c "import loguru, web3, yaml" > nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies (this may take a few minutes)...
    python -m pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo [+] Dependencies installed
) else (
    echo [+] Dependencies already installed
)

echo.
echo [*] Checking configuration files...

REM Check private_keys.txt
set NEED_CONFIG=0
if not exist data\private_keys.txt (
    if exist data\private_keys.txt.example (
        copy data\private_keys.txt.example data\private_keys.txt > nul
        echo [!] Created data\private_keys.txt from example
        set NEED_CONFIG=1
    ) else (
        echo [X] data\private_keys.txt.example not found!
        pause
        exit /b 1
    )
) else (
    findstr /C:"your_private_key" data\private_keys.txt > nul 2>&1
    if not errorlevel 1 (
        echo [!] data\private_keys.txt contains example data
        set NEED_CONFIG=1
    ) else (
        echo [+] data\private_keys.txt configured
    )
)

REM Check proxies.txt
if not exist data\proxies.txt (
    if exist data\proxies.txt.example (
        copy data\proxies.txt.example data\proxies.txt > nul
        echo [!] Created data\proxies.txt from example
        set NEED_CONFIG=1
    ) else (
        echo [X] data\proxies.txt.example not found!
        pause
        exit /b 1
    )
) else (
    findstr /C:"user.*:pass.*@" data\proxies.txt > nul 2>&1
    if not errorlevel 1 (
        findstr /C:"example" data\proxies.txt > nul 2>&1
        if not errorlevel 1 (
            echo [!] data\proxies.txt contains example data
            set NEED_CONFIG=1
        ) else (
            echo [+] data\proxies.txt configured
        )
    ) else (
        echo [+] data\proxies.txt configured
    )
)

REM Check config.yaml
if not exist config.yaml (
    echo [X] config.yaml not found!
    pause
    exit /b 1
) else (
    echo [+] config.yaml exists
)

REM If configuration needed, prompt user
if !NEED_CONFIG! EQU 1 (
    echo.
    echo ================================================
    echo   Configuration Required
    echo ================================================
    echo.
    echo Please edit the following files with your actual data:
    echo   1. data\private_keys.txt - Add your wallet private keys
    echo   2. data\proxies.txt - Add your proxy addresses
    echo.
    echo Press any key after editing the files...
    pause > nul
    echo.
)

echo.
echo [+] Setup completed! Starting bot...
echo.

REM Parse command line arguments
if "%~1"=="--auto" (
    echo 1 | python main.py
) else if "%~1"=="--option" (
    echo %~2 | python main.py
) else (
    python main.py
)

pause
