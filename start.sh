#!/bin/bash

# ScanWitch Startup Script
echo "🚀 Starting ScanWitch - Advanced Threat Detection Platform"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start Flask application
echo "🌐 Starting ScanWitch application..."
python main_simple.py



