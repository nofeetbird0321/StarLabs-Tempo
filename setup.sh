#!/bin/bash

# StarLabs Tempo Bot - First-Time Setup Script
# This script helps you set up the bot for the first time with guided configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  StarLabs Tempo Bot - Setup Wizard${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${CYAN}This wizard will guide you through the initial setup.${NC}"
echo ""

# Function to print colored messages
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC}  $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_step() { echo -e "${CYAN}▶${NC} $1"; }

# Check Python
print_step "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python is not installed!"
    echo ""
    echo "Please install Python 3.11+ from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION detected"
echo ""

# Setup configuration files
print_step "Setting up configuration files..."
echo ""

# Private keys
if [ ! -f "data/private_keys.txt" ]; then
    if [ -f "data/private_keys.txt.example" ]; then
        cp data/private_keys.txt.example data/private_keys.txt
        print_success "Created data/private_keys.txt"
    fi
else
    print_success "data/private_keys.txt already exists"
fi

# Proxies
if [ ! -f "data/proxies.txt" ]; then
    if [ -f "data/proxies.txt.example" ]; then
        cp data/proxies.txt.example data/proxies.txt
        print_success "Created data/proxies.txt"
    fi
else
    print_success "data/proxies.txt already exists"
fi

echo ""
echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}  Configuration Required${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""
echo "Please prepare the following information:"
echo ""
echo -e "${CYAN}1. Private Keys${NC}"
echo "   - Your Ethereum wallet private keys"
echo "   - One private key per line"
echo "   - File: data/private_keys.txt"
echo ""
echo -e "${CYAN}2. Proxies${NC}"
echo "   - Proxy addresses for enhanced security"
echo "   - Format: http://user:pass@ip:port"
echo "   - One proxy per line"
echo "   - File: data/proxies.txt"
echo ""
echo -e "${CYAN}3. Configuration (Optional)${NC}"
echo "   - Edit config.yaml to customize settings"
echo "   - Adjust threads, retry attempts, pause times, etc."
echo ""

read -p "Press Enter to open the configuration files for editing..."

# Open files with default editor
echo ""
print_step "Opening configuration files..."

if command -v nano &> /dev/null; then
    EDITOR="nano"
elif command -v vim &> /dev/null; then
    EDITOR="vim"
elif command -v vi &> /dev/null; then
    EDITOR="vi"
else
    print_warning "No command-line editor found. Please edit files manually."
    EDITOR=""
fi

if [ -n "$EDITOR" ]; then
    echo ""
    echo -e "${CYAN}Opening data/private_keys.txt...${NC}"
    echo "Add your private keys (one per line), then save and exit."
    echo ""
    read -p "Press Enter to continue..."
    $EDITOR data/private_keys.txt

    echo ""
    echo -e "${CYAN}Opening data/proxies.txt...${NC}"
    echo "Add your proxies (format: http://user:pass@ip:port), then save and exit."
    echo ""
    read -p "Press Enter to continue..."
    $EDITOR data/proxies.txt
else
    echo ""
    echo "Please edit these files manually:"
    echo "  - data/private_keys.txt"
    echo "  - data/proxies.txt"
    echo ""
    read -p "Press Enter after you've edited the files..."
fi

# Validate files
echo ""
print_step "Validating configuration..."

VALID=true

# Check private keys
if [ ! -s "data/private_keys.txt" ] || grep -q "your_private_key" data/private_keys.txt 2>/dev/null; then
    print_error "data/private_keys.txt is empty or contains example data"
    VALID=false
else
    print_success "Private keys configured"
fi

# Check proxies
if [ ! -s "data/proxies.txt" ] || (grep -q "user.*:pass.*@" data/proxies.txt 2>/dev/null && grep -q "example" data/proxies.txt 2>/dev/null); then
    print_error "data/proxies.txt is empty or contains example data"
    VALID=false
else
    print_success "Proxies configured"
fi

if [ "$VALID" = false ]; then
    echo ""
    print_error "Configuration incomplete!"
    echo ""
    echo "Please edit the files manually and run this setup again."
    exit 1
fi

echo ""
print_step "Installing dependencies..."
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# Install dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Dependencies installed"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "You can now start the bot with:"
echo ""
echo -e "  ${CYAN}./start.sh --auto${NC}     # Auto-start farming"
echo -e "  ${CYAN}./start.sh${NC}            # Interactive mode"
echo ""
read -p "Press Enter to exit..."
