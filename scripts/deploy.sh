#!/bin/bash

# Exit on error
set -e

echo "Deployment Starts..."

DEPLOY_DIR="/home/stillbloom/HyrosAdTool"
VENV_DIR="/home/stillbloom/venv"

# Ensure virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Ensure project directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "Error: Deployment directory missing: $DEPLOY_DIR"
    exit 1
fi

cd "$DEPLOY_DIR"

# Install dependencies safely
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: No requirements.txt found."
fi

# Run migrations and collect static files
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "Deployment Done..."
