# StarLabs Tempo Bot 🚀

<div align="center">

[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram)](https://t.me/StarLabsTech)
[![Telegram Chat](https://img.shields.io/badge/Telegram-Chat-blue?style=for-the-badge&logo=telegram)](https://t.me/StarLabsChat)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/0xStarLabs)

</div>

A powerful automation tool for Tempo Network Testnet with faucet claiming and token transfers.

## 🌟 Features

### Core Functionality
- ✨ **Multi-threaded processing** - Run multiple accounts simultaneously
- 🔄 **Automatic retries** with configurable attempts
- 🔐 **Proxy support** for enhanced security
- 📊 **Account range selection** and exact account filtering
- 🎲 **Random pauses** between operations
- 🔔 **Telegram logging** integration
- 📝 **Database task tracking** with SQLite storage
- 🧩 **Modular task system** with flexible configurations

### Tempo Network Operations
- **Faucet Claiming**:
  - Automatic faucet claiming via WebSocket RPC
  - Receives AlphaUSD, BetaUSD, ThetaUSD tokens
  - Balance verification after claim

- **Token Sender**:
  - Random token selection (AlphaUSD, BetaUSD, ThetaUSD)
  - Send to random addresses or between your wallets
  - Configurable percentage of balance to send
  - Gas optimization and transaction tracking

- **DEX Swaps** (NEW! 🎉):
  - Utilize Tempo's built-in DEX (protocol-level AMM)
  - Swap between AlphaUSD, BetaUSD, and ThetaUSD
  - Smart slippage protection
  - Automatic price quoting before swap
  - Configurable swap amounts and frequency

- **Balance Monitoring**:
  - Check all token balances
  - Detailed logging of token amounts

## 🚀 Quick Start (Simplified!)

### The Easiest Way - One Script Does Everything! 🎯

**Linux/Mac:**
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
./start.sh --auto
```

**Windows:**
```cmd
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
start.bat --auto
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Create virtual environment automatically
- ✅ Install all dependencies
- ✅ Set up configuration files from examples
- ✅ Guide you through first-time setup
- ✅ Start the bot automatically

### Command-Line Options

**Start script with options:**
```bash
# Auto-start farming (skip menu)
./start.sh --auto

# Open config editor directly
./start.sh --option 2

# Interactive mode (default)
./start.sh

# Show help
./start.sh --help
```

**Direct Python execution with options:**
```bash
# Auto-start farming
python main.py --auto

# Select specific option
python main.py --option 1

# Show all options
python main.py --help
```

## 📋 Requirements

- Python 3.11.x
- Private keys for Ethereum wallets
- Proxies for enhanced security
- (Optional) Telegram bot token for logging

## 🚀 Installation

### Option 1: Quick Start Script (Recommended) ⚡

The start script handles everything automatically:

**Linux/Mac:**
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
start.bat
```

The script will guide you through:
1. Automatically creating virtual environment
2. Installing dependencies
3. Setting up configuration files
4. Prompting for your private keys and proxies
5. Starting the bot

### Option 2: Docker (For Auto-Execution) 🐳

1. Clone the repository:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
```

2. Prepare configuration files:
```bash
cp data/private_keys.txt.example data/private_keys.txt
cp data/proxies.txt.example data/proxies.txt
# Edit these files with your actual keys and proxies
```

3. Configure `config.yaml` with your settings

4. Build and run with Docker:
```bash
# Quick start (recommended)
./docker-start.sh

# Or manually
docker-compose up -d
```

📖 **Documentation:**
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Detailed Docker deployment guide (English)
- [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md) - Docker 部署指南（中文）

### Option 3: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config.yaml`
4. Add your private keys to `data/private_keys.txt`
5. Add proxies to `data/proxies.txt`

## 📁 Project Structure

```
StarLabs-Tempo/
├── data/
│   ├── accounts.db            # SQLite database for task tracking
│   ├── private_keys.txt       # Ethereum wallet private keys
│   └── proxies.txt            # Proxy addresses
├── src/
│   ├── model/
│   │   ├── database/          # Database management
│   │   ├── tempo/             # Tempo network integration
│   │   │   ├── instance.py    # Faucet & token operations
│   │   │   └── constants.py   # Token addresses & ABIs
│   │   ├── onchain/           # Blockchain operations
│   │   └── help/              # Helper modules (stats)
│   └── utils/                 # Utility functions and configurations
├── config.yaml                # Main configuration file
└── tasks.py                   # Task definitions
```

## 📝 Configuration

### 1. Data Files
- `private_keys.txt`: One private key per line
- `proxies.txt`: One proxy per line (format: `http://user:pass@ip:port`)

### 2. Main Settings (`config.yaml`)
```yaml
SETTINGS:
  THREADS: 1                      # Number of parallel threads
  ATTEMPTS: 5                     # Retry attempts for failed actions
  ACCOUNTS_RANGE: [0, 0]          # Wallet range to use (default: all)
  EXACT_ACCOUNTS_TO_USE: []       # Specific wallets to use (default: all)
  SHUFFLE_WALLETS: true           # Randomize wallet processing order
  PAUSE_BETWEEN_ATTEMPTS: [1, 1]  # Random pause between retries
  PAUSE_BETWEEN_SWAPS: [3, 10]    # Random pause between swaps
  RANDOM_PAUSE_BETWEEN_ACCOUNTS: [1, 1]  # Pause between accounts
  RANDOM_PAUSE_BETWEEN_ACTIONS: [1, 1]   # Pause between actions
  RANDOM_INITIALIZATION_PAUSE: [1, 1]    # Pause before account start

TOKEN_SENDER:
  SEND_TOKENS_TO_MY_WALLETS: false  # Send to own wallets or random addresses
  PERCENT_OF_BALANCE_TO_SEND: [5, 10]  # Percent of balance to send
  NUMBER_OF_TRANSACTIONS_TO_SEND: [1, 10]  # Number of transactions

DEX_SWAPS:
  NUMBER_OF_SWAPS_TO_PERFORM: [1, 3]  # Number of swaps per run
  PERCENT_OF_BALANCE_TO_SWAP: [10, 30]  # Percent of balance to swap
  SLIPPAGE_TOLERANCE: 1  # Slippage tolerance in percent

RPCS:
  TEMPO: ["https://rpc.testnet.tempo.xyz"]

OTHERS:
  SKIP_SSL_VERIFICATION: true
  USE_PROXY_FOR_RPC: true
```

### 3. Telegram Logging (Optional)
```yaml
SETTINGS:
  SEND_TELEGRAM_LOGS: false
  TELEGRAM_BOT_TOKEN: "your_bot_token"
  TELEGRAM_USERS_IDS: [your_user_id]
```

## 🎮 Usage

### Quick Start Commands

**Start farming immediately:**
```bash
./start.sh --auto          # Linux/Mac
start.bat --auto           # Windows
python main.py --auto      # Direct Python
```

**Interactive mode (shows menu):**
```bash
./start.sh                 # Linux/Mac
start.bat                  # Windows
python main.py             # Direct Python
```

**Direct menu selection:**
```bash
# Skip to config editor
./start.sh --option 2

# Skip to database actions
./start.sh --option 3
```

### Run the Bot
```bash
python main.py
```

### Menu Options
1. **⭐️ Start farming** - Run selected tasks
2. **🔧 Edit config** - Open configuration editor
3. **💾 Database actions** - Manage task database
4. **👋 Exit** - Close the bot

### Database Management
- **Create/Reset Database** - Initialize new database with tasks
- **Generate Tasks for Completed Wallets** - Add new tasks to finished wallets
- **Show Database Contents** - View current database status
- **Regenerate Tasks for All** - Reset all wallet tasks
- **Add New Wallets** - Import wallets from files

## 🔧 Available Tasks

### Faucet
- **`faucet`** - Claim tokens from Tempo faucet:
  - Connects via WebSocket to Tempo RPC
  - Claims AlphaUSD, BetaUSD, ThetaUSD tokens
  - Displays balances after claiming

### Token Sender
- **`token_sender`** - Send random tokens:
  - Randomly selects one of the available tokens
  - Sends configurable percentage of balance
  - Can send to random addresses or your own wallets

### DEX Swaps (NEW! 🎉)
- **`dex_swaps`** - Perform token swaps on Tempo DEX:
  - Swaps between AlphaUSD, BetaUSD, and ThetaUSD
  - Uses Tempo's built-in protocol-level DEX
  - Automatic approval and price quoting
  - Slippage protection
  - Configurable number of swaps and amounts

## 📝 Task Configuration

Edit `tasks.py` to select which modules to run:

```python
# Available task presets
TASKS = ["FAUCET", "DEX_SWAPS"]

FAUCET = ["faucet"]
TOKEN_SENDER = ["token_sender"]
DEX_SWAPS = ["dex_swaps"]
```

### Task Syntax

```python
# Sequential execution
TASKS = ["FAUCET", "TOKEN_SENDER"]

# Create custom task combinations
CUSTOM_TASK = [
    "faucet",
    ("faucet", "token_sender"),  # Both in random order
    ["faucet", "token_sender"],  # Choose one randomly
]
```

### Task Flow Examples

```python
# Simple faucet claim
TASKS = ["FAUCET"]

# Faucet + DEX swaps
TASKS = ["FAUCET", "DEX_SWAPS"]

# Faucet + Token sending + DEX swaps
TASKS = ["FAUCET", "TOKEN_SENDER", "DEX_SWAPS"]

# Custom flow with mixed operations
CUSTOM_FLOW = [
    "faucet",
    "dex_swaps",
    "token_sender",
]
```

## 💱 Supported Tokens

| Token | Address | Decimals |
|-------|---------|----------|
| AlphaUSD | `0x20c0000000000000000000000000000000000001` | 6 |
| BetaUSD | `0x20c0000000000000000000000000000000000002` | 6 |
| ThetaUSD | `0x20c0000000000000000000000000000000000003` | 6 |

## 🔐 Security Features

- **Proxy support** for all operations
- **SSL verification** control
- **Error handling** with retry mechanisms
- **Random address generation** for token transfers
- **Optional wallet linking** (send between own wallets)

## ⚠️ Important Notes

1. **Proxies Required**: All operations require proxies
2. **Rate Limits**: Respect network rate limits to avoid issues
3. **Token Sender**: By default sends to random addresses (safer for wallet isolation)
4. **Configuration**: Test with small account ranges first
5. **Gas**: Ensure sufficient native balance for transaction fees

## 🔗 Network Info

### Testnet (Default Configuration)
- **Network**: Tempo Testnet (Moderato)
- **Chain ID**: 42429
- **RPC**: `https://rpc.testnet.tempo.xyz`
- **Explorer**: `https://explore.tempo.xyz`
- **Status**: Active

### Mainnet (Production)
- **Network**: Tempo Mainnet
- **Chain ID**: 42431
- **RPC**: `https://rpc.tempo.xyz`
- **Explorer**: `https://explore.tempo.xyz`
- **Status**: Live since Jan 16, 2026

> **Note**: This bot is currently configured for **testnet** usage. For mainnet deployment, update the RPC URL in `config.yaml`.

## 📜 License
MIT License

## ⚠️ Disclaimer
This tool is for educational and research purposes only. Use at your own risk and in accordance with Tempo Network's terms of service.

## 🆘 Support
For support and updates, join our community:
- Telegram Channel: [@StarLabsTech](https://t.me/StarLabsTech)
- Telegram Chat: [@StarLabsChat](https://t.me/StarLabsChat)
- GitHub: [0xStarLabs](https://github.com/0xStarLabs)

---

<div align="center">
Made with ❤️ by StarLabs Team
</div>
