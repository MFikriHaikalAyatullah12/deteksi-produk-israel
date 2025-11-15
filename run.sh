#!/bin/bash

# Install Dependencies and Run Israeli Product Detection System

echo "🚀 Setting up Israeli Product Detection System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "📦 Installing Python dependencies..."
cd backend
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# Install system dependencies for OpenCV and Tesseract
echo "🔧 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ara tesseract-ocr-heb libzbar0

echo "📦 Installing Node.js dependencies..."
cd ..
npm install

echo "🏃‍♂️ Starting the applications..."

# Start Python backend in background
echo "Starting Python backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start Next.js frontend
echo "Starting Next.js frontend..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Israeli Product Detection System is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on script exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Setup signal trapping
trap cleanup SIGINT SIGTERM

# Wait for either process to finish
wait