#!/bin/bash

# Exit on error
set -e

echo "Starting Stillbloom cleanup Process..."

DEPLOY_DIR="/home/stillbloom/HyrosAdTool"

# Fix permissions before deletion
echo "Fixing permissions..."
sudo chown -R jenkins:jenkins "$DEPLOY_DIR"
sudo chmod -R 775 "$DEPLOY_DIR"

# Remove project directory if it exists
if [ -d "$DEPLOY_DIR" ]; then
    echo "Removing old deployment directory..."
    rm -rf "$DEPLOY_DIR"
fi

echo "Cleanup Done..."
