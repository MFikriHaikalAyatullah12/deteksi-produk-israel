#!/bin/bash

# Script untuk menjalankan aplikasi Deteksi Produk Israel

echo "🚀 Starting Israeli Product Detection System..."

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function untuk log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed. Please install npm first."
    exit 1
fi

log_info "Setting up the application..."

# Install frontend dependencies
log_info "Installing frontend dependencies..."
if npm install; then
    log_success "Frontend dependencies installed successfully"
else
    log_error "Failed to install frontend dependencies"
    exit 1
fi

# Setup backend
log_info "Setting up backend environment..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        log_success "Virtual environment created successfully"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
if pip install -r requirements.txt; then
    log_success "Python dependencies installed successfully"
else
    log_error "Failed to install Python dependencies"
    exit 1
fi

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    log_warning "Tesseract OCR is not installed. Please install it for better text recognition:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  MacOS: brew install tesseract"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

cd ..

log_success "Setup completed successfully!"
echo ""
echo "🎉 Ready to start the application!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && source venv/bin/activate && python main.py"
echo "2. Frontend: npm run dev"
echo ""
echo "Then open: http://localhost:3000"