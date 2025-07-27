#!/bin/bash

# Docker run script for Multi-Agent Real Estate Application

echo "🏠 Multi-Agent Real Estate Application - Docker Setup"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your OpenAI API key:"
    echo ""
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    read -p "Do you want to create the .env file now? (y/n): " create_env
    
    if [ "$create_env" = "y" ] || [ "$create_env" = "Y" ]; then
        read -p "Enter your OpenAI API key: " api_key
        echo "OPENAI_API_KEY=$api_key" > .env
        echo "✅ .env file created!"
    else
        echo "❌ Please create the .env file manually and run this script again."
        exit 1
    fi
fi

echo "🚀 Starting the application with Docker Compose..."
echo ""

# Build and run the containers
docker-compose up --build

echo ""
echo "🎉 Application started successfully!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop the application, press Ctrl+C or run: docker-compose down" 