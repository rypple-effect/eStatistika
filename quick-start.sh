#!/bin/bash

# Quick Start Script for Llama Chat Workshop
# This script helps you get started quickly

set -e

echo "=================================="
echo "Llama Chat Workshop - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available!"
    echo "Please install Docker Compose or update Docker Desktop"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is available"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Ask user if they want to start fresh
read -p "Do you want to start fresh (remove existing containers and volumes)? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning up existing containers and volumes..."
    docker compose down -v
    echo ""
fi

echo "🚀 Starting services..."
echo ""
echo "This will:"
echo "  1. Start Ollama service"
echo "  2. Download Llama 3.2 model (~4.7GB) - this may take a few minutes"
echo "  3. Start FastAPI application"
echo ""

# Start services
docker compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for API to be ready
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8081/health &> /dev/null; then
        echo ""
        echo "✅ All services are ready!"
        echo ""
        echo "=================================="
        echo "Your Llama Chat API is running!"
        echo "=================================="
        echo ""
        echo "📚 API Documentation: http://localhost:8081/docs"
        echo "❤️  Health Check:      http://localhost:8081/health"
        echo "💬 Chat Endpoint:      http://localhost:8081/chat"
        echo ""
        echo "=================================="
        echo "Quick Test"
        echo "=================================="
        echo ""
        echo "Test with curl:"
        echo 'curl -X POST "http://localhost:8081/chat" \\'
        echo '  -H "Content-Type: application/json" \\'
        echo '  -d '\''{"message": "Hello, who are you?"}'\'''
        echo ""
        echo "Or run the example client:"
        echo "  python example_client.py"
        echo ""
        echo "=================================="
        echo "Useful Commands"
        echo "=================================="
        echo ""
        echo "View logs:           docker compose logs -f"
        echo "Stop services:       docker compose down"
        echo "Restart services:    docker compose restart"
        echo "Remove everything:   docker compose down -v"
        echo ""
        exit 0
    fi

    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

echo ""
echo "⚠️  Services are taking longer than expected to start."
echo "This is normal on the first run when downloading the model."
echo ""
echo "Check the logs with: docker compose logs -f"
echo ""
echo "The API will be available at http://localhost:8081 once ready."
