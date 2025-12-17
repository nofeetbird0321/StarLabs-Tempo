#!/bin/bash

# StarLabs Tempo Bot - Docker Setup Verification Script
# This script verifies that your Docker setup is correct before running

echo "================================================"
echo "  Docker Setup Verification"
echo "================================================"
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo "Checking Docker installation..."
echo "--------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "   Please install Docker from: https://docs.docker.com/get-docker/"
else
    print_success "Docker is installed"
    docker --version
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "   Please install Docker Compose from: https://docs.docker.com/compose/install/"
else
    print_success "Docker Compose is installed"
    docker-compose --version
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "   Please start Docker service"
else
    print_success "Docker daemon is running"
fi

echo ""
echo "Checking required files..."
echo "--------------------------------"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found"
else
    print_success "Dockerfile found"
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found"
else
    print_success "docker-compose.yml found"
fi

# Check if entrypoint.sh exists and is executable
if [ ! -f "entrypoint.sh" ]; then
    print_error "entrypoint.sh not found"
else
    if [ ! -x "entrypoint.sh" ]; then
        print_warning "entrypoint.sh is not executable"
        echo "   Run: chmod +x entrypoint.sh"
    else
        print_success "entrypoint.sh found and executable"
    fi
fi

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    print_error "config.yaml not found"
else
    print_success "config.yaml found"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
else
    print_success "requirements.txt found"
fi

echo ""
echo "Checking data directory..."
echo "--------------------------------"

# Check if data directory exists
if [ ! -d "data" ]; then
    print_error "data directory not found"
    echo "   Creating data directory..."
    mkdir -p data
else
    print_success "data directory found"
fi

# Check if private_keys.txt exists
if [ ! -f "data/private_keys.txt" ]; then
    print_error "data/private_keys.txt not found"
    echo "   Copy from example: cp data/private_keys.txt.example data/private_keys.txt"
else
    # Check if file is empty
    if [ ! -s "data/private_keys.txt" ]; then
        print_warning "data/private_keys.txt is empty"
        echo "   Please add your wallet private keys"
    # Check if it contains example data
    elif grep -q "$EXAMPLE_KEY_PATTERN" data/private_keys.txt; then
        print_warning "data/private_keys.txt contains example data"
        echo "   Please replace with your actual private keys"
    else
        print_success "data/private_keys.txt found and populated"
        # Count number of keys
        KEY_COUNT=$(grep -v '^[[:space:]]*$' data/private_keys.txt | wc -l)
        echo "   Number of keys: $KEY_COUNT"
    fi
fi

# Check if proxies.txt exists
if [ ! -f "data/proxies.txt" ]; then
    print_error "data/proxies.txt not found"
    echo "   Copy from example: cp data/proxies.txt.example data/proxies.txt"
else
    # Check if file is empty
    if [ ! -s "data/proxies.txt" ]; then
        print_warning "data/proxies.txt is empty"
        echo "   Please add your proxy addresses"
    # Check if it contains example data
    elif grep -q "$EXAMPLE_PROXY_PATTERN" data/proxies.txt; then
        print_warning "data/proxies.txt contains example data"
        echo "   Please replace with your actual proxies"
    else
        print_success "data/proxies.txt found and populated"
        # Count number of proxies
        PROXY_COUNT=$(grep -v '^[[:space:]]*$' data/proxies.txt | wc -l)
        echo "   Number of proxies: $PROXY_COUNT"
    fi
fi

echo ""
echo "Checking docker-compose.yml syntax..."
echo "--------------------------------"

# Validate docker-compose.yml
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    if docker-compose config --quiet 2>/dev/null; then
        print_success "docker-compose.yml syntax is valid"
    else
        print_error "docker-compose.yml has syntax errors"
        echo "   Run: docker-compose config"
    fi
fi

echo ""
echo "Checking directory permissions..."
echo "--------------------------------"

# Check if data directory is writable
if [ ! -w "data" ]; then
    print_warning "data directory is not writable"
    echo "   Run: chmod -R u+w data"
else
    print_success "data directory is writable"
fi

# Check if logs directory exists and is writable
if [ ! -d "logs" ]; then
    print_warning "logs directory not found, will be created by Docker"
    mkdir -p logs
else
    if [ ! -w "logs" ]; then
        print_warning "logs directory is not writable"
        echo "   Run: chmod -R u+w logs"
    else
        print_success "logs directory is writable"
    fi
fi

echo ""
echo "================================================"
echo "  Verification Summary"
echo "================================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! You're ready to run the bot.${NC}"
    echo ""
    echo "To start the bot, run:"
    echo "  ./docker-start.sh"
    echo ""
    echo "Or manually:"
    echo "  docker-compose up -d"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Found $WARNINGS warning(s).${NC}"
    echo "Please review the warnings above."
    echo "The bot may still run, but you should address these issues."
else
    echo -e "${RED}❌ Found $ERRORS error(s) and $WARNINGS warning(s).${NC}"
    echo "Please fix the errors above before running the bot."
    exit 1
fi

echo ""
