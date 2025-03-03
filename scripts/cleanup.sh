#!/bin/bash

# Exit on error
set -e

echo "Starting Stillbloom cleanup Process..."

DEPLOY_DIR="/home/stillbloom/HyrosAdTool"

# Ensure proper ownership and permissions only if needed
if [ -d "/home/stillbloom" ]; then
    sudo chown -R jenkins:jenkins /home/stillbloom
    sudo chmod -R 2775 /home/stillbloom
    sudo find /home/stillbloom -type d -exec chmod g+s {} \;
fi

# Remove project directory if it exists
if [ -d "$DEPLOY_DIR" ]; then
    echo "Removing old deployment directory..."
    sudo rm -rf "$DEPLOY_DIR"
fi

echo "Cleanup Done..."
