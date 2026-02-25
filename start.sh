#!/bin/bash

# StarLabs Tempo Bot - Universal Startup Script
# Handles setup and launch with minimal user intervention

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  StarLabs Tempo Bot - Quick Start${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print colored messages
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC}  $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed!"
        echo "Please install Python 3.11+ from: https://www.python.org/downloads/"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 11 ]); then
        print_warning "Python $PYTHON_VERSION detected. Python 3.11+ is recommended."
    else
        print_success "Python $PYTHON_VERSION detected"
    fi
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment exists"
    fi

    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        print_error "Cannot activate virtual environment"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Checking dependencies..."

    # Check if requirements are already installed
    if $PYTHON_CMD -c "import loguru, web3, yaml" 2>/dev/null; then
        print_success "Dependencies already installed"
        return 0
    fi

    print_info "Installing dependencies (this may take a few minutes)..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Dependencies installed"
}

# Setup configuration files
setup_config_files() {
    local need_config=false

    print_info "Checking configuration files..."

    # Check private_keys.txt
    if [ ! -f "data/private_keys.txt" ]; then
        if [ -f "data/private_keys.txt.example" ]; then
            cp data/private_keys.txt.example data/private_keys.txt
            print_warning "Created data/private_keys.txt from example"
            need_config=true
        else
            print_error "data/private_keys.txt.example not found!"
            exit 1
        fi
    elif grep -q "your_private_key" data/private_keys.txt 2>/dev/null; then
        print_warning "data/private_keys.txt contains example data"
        need_config=true
    else
        print_success "data/private_keys.txt configured"
    fi

    # Check proxies.txt
    if [ ! -f "data/proxies.txt" ]; then
        if [ -f "data/proxies.txt.example" ]; then
            cp data/proxies.txt.example data/proxies.txt
            print_warning "Created data/proxies.txt from example"
            need_config=true
        else
            print_error "data/proxies.txt.example not found!"
            exit 1
        fi
    elif grep -q "user.*:pass.*@" data/proxies.txt 2>/dev/null && grep -q "example\|your_proxy" data/proxies.txt 2>/dev/null; then
        print_warning "data/proxies.txt contains example data"
        need_config=true
    else
        print_success "data/proxies.txt configured"
    fi

    # Check config.yaml
    if [ ! -f "config.yaml" ]; then
        print_error "config.yaml not found!"
        exit 1
    else
        print_success "config.yaml exists"
    fi

    # If configuration is needed, guide the user
    if [ "$need_config" = true ]; then
        echo ""
        echo -e "${YELLOW}================================================${NC}"
        echo -e "${YELLOW}  Configuration Required${NC}"
        echo -e "${YELLOW}================================================${NC}"
        echo ""
        echo "Please edit the following files with your actual data:"
        echo -e "  ${BLUE}1.${NC} data/private_keys.txt - Add your wallet private keys (one per line)"
        echo -e "  ${BLUE}2.${NC} data/proxies.txt - Add your proxy addresses (format: http://user:pass@ip:port)"
        echo ""
        echo "You can also edit config.yaml to customize settings (optional)"
        echo ""
        read -p "Press Enter after editing the files, or Ctrl+C to exit and edit them later..."
        echo ""
    fi
}

# Parse command line arguments
AUTO_START=false
SELECTED_OPTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto|--start|-s)
            AUTO_START=true
            shift
            ;;
        --option|-o)
            SELECTED_OPTION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto, --start, -s    Auto-start farming (skip menu)"
            echo "  --option, -o <num>     Select menu option directly (1-4)"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Interactive mode with menu"
            echo "  $0 --auto              # Auto-start farming"
            echo "  $0 --option 2          # Open config editor directly"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    check_python
    setup_venv
    install_dependencies
    setup_config_files

    echo ""
    print_success "Setup completed! Starting bot..."
    echo ""

    # Start the bot with appropriate option
    if [ "$AUTO_START" = true ] || [ "$SELECTED_OPTION" = "1" ]; then
        echo "1" | $PYTHON_CMD main.py
    elif [ -n "$SELECTED_OPTION" ]; then
        echo "$SELECTED_OPTION" | $PYTHON_CMD main.py
    else
        $PYTHON_CMD main.py
    fi
}

# Run main function
main
