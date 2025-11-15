#!/bin/bash

# Script untuk menjalankan backend dan frontend secara bersamaan

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup processes
cleanup() {
    echo ""
    log_info "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    log_success "Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Israeli Product Detection System..."

# Start backend
log_info "Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || {
    log_error "Virtual environment not found. Run setup.sh first."
    exit 1
}

python main.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
log_info "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait a bit for frontend to start
sleep 5

log_success "Both servers are running!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID