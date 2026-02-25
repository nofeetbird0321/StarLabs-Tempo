# StarLabs Tempo Bot - Startup Guide 🚀

This guide explains the improved startup process and all available options for running the bot.

## 📋 Table of Contents

- [Quick Start (Easiest Way)](#quick-start-easiest-way)
- [Detailed Setup Guide](#detailed-setup-guide)
- [Command-Line Options](#command-line-options)
- [Configuration Files](#configuration-files)
- [Troubleshooting](#troubleshooting)

## 🎯 Quick Start (Easiest Way)

### First-Time Setup

**Option 1: Guided Setup Wizard (Recommended for beginners)**

Linux/Mac:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
chmod +x setup.sh
./setup.sh
```

The setup wizard will:
- Check your Python installation
- Create configuration files
- Guide you through editing private keys and proxies
- Install all dependencies
- Validate your configuration

**Option 2: Automatic Setup with Start Script**

Linux/Mac:
```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
./start.sh
```

Windows:
```cmd
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
start.bat
```

The script automatically:
- Detects Python installation
- Creates virtual environment
- Installs dependencies
- Sets up configuration files from examples
- Prompts you to edit configuration if needed
- Starts the bot

## 📖 Detailed Setup Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
```

### Step 2: Prepare Configuration Files

The scripts will automatically create these files from examples, but you need to fill them with your data:

**data/private_keys.txt**
```
0xYourPrivateKey1Here
0xYourPrivateKey2Here
0xYourPrivateKey3Here
```

**data/proxies.txt**
```
http://user1:pass1@ip1:port1
http://user2:pass2@ip2:port2
http://user3:pass3@ip3:port3
```

### Step 3: Configure Settings (Optional)

Edit `config.yaml` to customize:
- Number of concurrent threads
- Retry attempts
- Pause intervals
- Token sender settings
- DEX swap settings
- Telegram logging (optional)

### Step 4: Run the Bot

**Interactive Mode (Shows Menu):**
```bash
./start.sh              # Linux/Mac
start.bat               # Windows
```

**Auto-Start Mode (Direct to Farming):**
```bash
./start.sh --auto       # Linux/Mac
start.bat --auto        # Windows
```

## ⚙️ Command-Line Options

### Start Script Options

**Linux/Mac (start.sh):**

```bash
# Interactive mode with menu
./start.sh

# Auto-start farming (skip menu)
./start.sh --auto
./start.sh --start
./start.sh -s

# Direct menu option selection
./start.sh --option 1    # Start farming
./start.sh --option 2    # Edit config
./start.sh --option 3    # Database actions
./start.sh --option 4    # Exit
./start.sh -o 1          # Short form

# Show help
./start.sh --help
./start.sh -h
```

**Windows (start.bat):**

```cmd
REM Interactive mode with menu
start.bat

REM Auto-start farming
start.bat --auto

REM Direct menu option selection
start.bat --option 1
start.bat --option 2
```

### Direct Python Execution

You can also run the bot directly with Python (after dependencies are installed):

```bash
# Interactive mode
python main.py

# Auto-start farming
python main.py --auto
python main.py --start

# Direct menu selection
python main.py --option 1
python main.py -o 2

# Skip logo display
python main.py --no-logo

# Show help
python main.py --help
python main.py -h
```

## 📝 Configuration Files

### data/private_keys.txt

Format: One private key per line

```text
0x1234567890abcdef...
0xabcdef1234567890...
```

**Security Notes:**
- Never share your private keys
- Keep this file secure
- Add it to `.gitignore` (already done)

### data/proxies.txt

Format: One proxy per line

Supported formats:
```text
http://user:pass@ip:port
http://ip:port
socks5://user:pass@ip:port
```

**Proxy Tips:**
- Use residential or datacenter proxies
- Ensure proxies are working before running
- One proxy per wallet is recommended

### config.yaml

Key settings to customize:

```yaml
SETTINGS:
  THREADS: 1                    # Concurrent accounts (1-10)
  ATTEMPTS: 5                   # Retry attempts
  SHUFFLE_WALLETS: true         # Randomize order

TOKEN_SENDER:
  SEND_TOKENS_TO_MY_WALLETS: false
  PERCENT_OF_BALANCE_TO_SEND: [5, 10]

DEX_SWAPS:
  NUMBER_OF_SWAPS_TO_PERFORM: [1, 3]
  PERCENT_OF_BALANCE_TO_SWAP: [10, 30]
  SLIPPAGE_TOLERANCE: 1
```

## 🎮 Usage Examples

### Example 1: First-Time User

```bash
# Clone and run setup wizard
git clone https://github.com/0xStarLabs/StarLabs-Tempo.git
cd StarLabs-Tempo
./setup.sh

# After setup completes, start farming
./start.sh --auto
```

### Example 2: Quick Daily Run

```bash
cd StarLabs-Tempo
./start.sh --auto
```

### Example 3: Edit Configuration

```bash
cd StarLabs-Tempo
./start.sh --option 2
```

### Example 4: Check Database Status

```bash
cd StarLabs-Tempo
./start.sh --option 3
```

## 🐳 Docker Usage

For automated, scheduled runs:

```bash
# Quick start
./docker-start.sh

# Or manual
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed Docker instructions.

## 🔧 Troubleshooting

### Issue: "Python is not installed"

**Solution:**
- Install Python 3.11+ from https://www.python.org/downloads/
- Ensure Python is in your system PATH
- Try `python3` instead of `python`

### Issue: "Failed to install dependencies"

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Install manually
pip install -r requirements.txt

# If still failing, try with verbose output
pip install -v -r requirements.txt
```

### Issue: "Configuration files contain example data"

**Solution:**
- Edit `data/private_keys.txt` and replace example keys with real ones
- Edit `data/proxies.txt` and replace example proxies with real ones
- Run the start script again

### Issue: "No proxies found"

**Solution:**
- Ensure `data/proxies.txt` exists and is not empty
- Check proxy format: `http://user:pass@ip:port`
- Verify at least one proxy per line

### Issue: "Permission denied" on Linux/Mac

**Solution:**
```bash
chmod +x start.sh
chmod +x setup.sh
chmod +x docker-start.sh
```

### Issue: Virtual environment activation fails

**Solution:**
```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows
```

## 📊 What Each Script Does

### start.sh / start.bat

**Purpose:** All-in-one startup script

**Features:**
- Checks Python installation
- Creates virtual environment automatically
- Installs dependencies if needed
- Validates configuration files
- Starts the bot with options

**When to use:** Every time you want to run the bot

### setup.sh

**Purpose:** Interactive first-time setup wizard

**Features:**
- Guided configuration file creation
- Opens files in editor for easy editing
- Validates configuration
- Installs dependencies
- Provides next steps

**When to use:** First time setup, or when you need guided help

### docker-start.sh

**Purpose:** Docker container startup

**Features:**
- Validates Docker installation
- Sets up configuration files
- Builds Docker image
- Starts container in foreground or background

**When to use:** For automated, scheduled, or isolated runs

## 🎯 Best Practices

1. **First Time:** Run `./setup.sh` for guided setup
2. **Daily Use:** Run `./start.sh --auto` for quick farming
3. **Testing:** Run `./start.sh` (interactive) to test new configurations
4. **Automation:** Use Docker with `./docker-start.sh` for scheduled runs
5. **Maintenance:** Keep your proxies and private keys updated in config files

## 📚 Additional Resources

- [README.md](README.md) - Main project documentation
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker deployment guide
- [DOCKER_DEPLOYMENT_CN.md](DOCKER_DEPLOYMENT_CN.md) - Docker部署指南（中文）
- [config.yaml](config.yaml) - Configuration reference

## 💡 Tips

1. **Save Time:** Use `--auto` flag to skip menu selection
2. **Test First:** Start with 1-2 wallets to test configuration
3. **Monitor Logs:** Check `logs/app.log` for detailed information
4. **Proxy Rotation:** Use different proxies for different accounts
5. **Keep Updated:** Check for updates regularly with `git pull`

## 🆘 Need Help?

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review error messages in terminal and logs
3. Ensure all configuration files are correct
4. Join our community:
   - Telegram Channel: [@StarLabsTech](https://t.me/StarLabsTech)
   - Telegram Chat: [@StarLabsChat](https://t.me/StarLabsChat)
   - GitHub Issues: [Report a bug](https://github.com/0xStarLabs/StarLabs-Tempo/issues)

---

**Made with ❤️ by StarLabs Team**
