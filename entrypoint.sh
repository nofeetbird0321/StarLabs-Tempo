#!/bin/bash

# Exit on error
set -e

echo "==========================================="
echo "  StarLabs Tempo Bot - Docker Container"
echo "==========================================="
echo ""

# Check if private_keys.txt exists and has content
if [ ! -f "/app/data/private_keys.txt" ] || [ ! -s "/app/data/private_keys.txt" ]; then
    echo "ERROR: /app/data/private_keys.txt is missing or empty"
    echo "Please create data/private_keys.txt with your private keys (one per line)"
    exit 1
fi

# Check if proxies.txt exists and has content
if [ ! -f "/app/data/proxies.txt" ] || [ ! -s "/app/data/proxies.txt" ]; then
    echo "ERROR: /app/data/proxies.txt is missing or empty"
    echo "Please create data/proxies.txt with your proxies (format: http://user:pass@ip:port)"
    exit 1
fi

# Check if config.yaml exists
if [ ! -f "/app/config.yaml" ]; then
    echo "ERROR: config.yaml is missing"
    echo "Please make sure config.yaml exists in the project root"
    exit 1
fi

echo "✓ Configuration files validated"
echo ""
echo "Starting StarLabs Tempo Bot..."
echo ""

# Run the bot automatically (option 1 - Start farming)
# Using echo to simulate user input selecting option 1
# Set AUTO_START environment variable to allow customization
AUTO_SELECT_OPTION="${AUTO_SELECT_OPTION:-1}"
echo "$AUTO_SELECT_OPTION" | python main.py

echo ""
echo "Bot execution completed"
