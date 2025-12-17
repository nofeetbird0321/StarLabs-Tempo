#!/bin/bash

# StarLabs Tempo Bot - Docker Quick Start Script
# This script helps you quickly set up and run the bot using Docker

echo "================================================"
echo "  StarLabs Tempo Bot - Docker Quick Start"
echo "================================================"
echo ""

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed!"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo "✓ Docker is installed"
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed!"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo "✓ Docker Compose is installed"
}

# Function to setup configuration files
setup_config() {
    echo ""
    echo "Setting up configuration files..."
    
    # Check if private_keys.txt exists
    if [ ! -f "data/private_keys.txt" ]; then
        if [ -f "data/private_keys.txt.example" ]; then
            echo "⚠️  data/private_keys.txt not found"
            echo "Creating from example file..."
            cp data/private_keys.txt.example data/private_keys.txt
            echo "⚠️  Please edit data/private_keys.txt and add your private keys!"
            NEED_CONFIG=true
        else
            echo "❌ data/private_keys.txt.example not found!"
            exit 1
        fi
    else
        # Check if it's just the example content
        if grep -q "your_private_key" data/private_keys.txt; then
            echo "⚠️  data/private_keys.txt contains example data"
            echo "Please edit data/private_keys.txt and add your actual private keys!"
            NEED_CONFIG=true
        else
            echo "✓ data/private_keys.txt exists"
        fi
    fi
    
    # Check if proxies.txt exists
    if [ ! -f "data/proxies.txt" ]; then
        if [ -f "data/proxies.txt.example" ]; then
            echo "⚠️  data/proxies.txt not found"
            echo "Creating from example file..."
            cp data/proxies.txt.example data/proxies.txt
            echo "⚠️  Please edit data/proxies.txt and add your proxies!"
            NEED_CONFIG=true
        else
            echo "❌ data/proxies.txt.example not found!"
            exit 1
        fi
    else
        # Check if it's just the example content
        if grep -q "user1:pass1" data/proxies.txt; then
            echo "⚠️  data/proxies.txt contains example data"
            echo "Please edit data/proxies.txt and add your actual proxies!"
            NEED_CONFIG=true
        else
            echo "✓ data/proxies.txt exists"
        fi
    fi
    
    # Check if config.yaml exists
    if [ ! -f "config.yaml" ]; then
        echo "❌ config.yaml not found!"
        exit 1
    else
        echo "✓ config.yaml exists"
    fi
    
    if [ "$NEED_CONFIG" = true ]; then
        echo ""
        echo "================================================"
        echo "⚠️  CONFIGURATION REQUIRED"
        echo "================================================"
        echo "Please edit the following files before running:"
        echo "  - data/private_keys.txt (add your wallet private keys)"
        echo "  - data/proxies.txt (add your proxy addresses)"
        echo ""
        read -p "Press Enter after updating the configuration files, or Ctrl+C to exit..."
    fi
}

# Function to build Docker image
build_image() {
    echo ""
    echo "Building Docker image..."
    docker-compose build
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build Docker image"
        exit 1
    fi
    echo "✓ Docker image built successfully"
}

# Function to start the bot
start_bot() {
    echo ""
    echo "Starting StarLabs Tempo Bot..."
    echo ""
    echo "Choose run mode:"
    echo "  [1] Foreground (see logs in real-time, Ctrl+C to stop)"
    echo "  [2] Background (detached mode)"
    echo ""
    read -p "Enter your choice (1 or 2): " mode_choice
    
    case $mode_choice in
        1)
            echo ""
            echo "Starting in foreground mode..."
            echo "Press Ctrl+C to stop the bot"
            echo ""
            docker-compose up
            ;;
        2)
            echo ""
            echo "Starting in background mode..."
            docker-compose up -d
            echo ""
            echo "✓ Bot is running in background"
            echo ""
            echo "To view logs: docker-compose logs -f"
            echo "To stop the bot: docker-compose down"
            ;;
        *)
            echo "Invalid choice. Starting in foreground mode..."
            docker-compose up
            ;;
    esac
}

# Main execution
main() {
    check_docker
    check_docker_compose
    setup_config
    build_image
    start_bot
}

# Run main function
main
