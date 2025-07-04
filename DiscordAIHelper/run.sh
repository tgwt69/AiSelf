#!/bin/bash

# Discord AI Selfbot - Linux/Mac Setup Script
# 2025 Enhanced Edition

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Clear screen and show header
clear
echo -e "${CYAN}"
echo "============================================"
echo "     Discord AI Selfbot - Setup Script"
echo "           2025 Enhanced Edition"
echo "============================================"
echo -e "${NC}"

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed!"
    echo "Please install Python 3.9+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    echo "  macOS:         brew install python3"
    exit 1
fi

print_info "Python found. Checking version..."
python3 --version

# Check Python version (minimum 3.9)
python3 -c "
import sys
if sys.version_info < (3, 9):
    print('ERROR: Python 3.9+ is required')
    sys.exit(1)
else:
    print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible')
"

if [ $? -ne 0 ]; then
    print_error "Python version too old. Please upgrade to Python 3.9 or higher."
    exit 1
fi

# Check if we're in a virtual environment
python3 -c "
import sys
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print('Virtual environment detected')
else:
    print('No virtual environment')
"

echo
print_info "Setting up Discord AI Selfbot..."
echo

# Create virtual environment if it doesn't exist
if [ ! -d "bot-env" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv bot-env
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        print_info "Trying to install python3-venv..."
        if command_exists apt; then
            sudo apt install python3-venv
        elif command_exists yum; then
            sudo yum install python3-venv
        elif command_exists pacman; then
            sudo pacman -S python-virtualenv
        fi
        python3 -m venv bot-env
        if [ $? -ne 0 ]; then
            print_error "Still failed to create virtual environment. Please install python3-venv manually."
            exit 1
        fi
    fi
    print_success "Virtual environment created successfully"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source bot-env/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
print_info "Installing/updating dependencies..."
print_warning "This may take a few minutes..."

# Core dependencies for 2025 compatibility
python -m pip install --upgrade discord.py-self>=2.0.1
python -m pip install --upgrade groq>=0.4.0
python -m pip install --upgrade openai>=1.0.0
python -m pip install --upgrade colorama>=0.4.6
python -m pip install --upgrade httpx>=0.24.0
python -m pip install --upgrade asyncio
python -m pip install --upgrade python-dotenv>=1.0.0
python -m pip install --upgrade pyyaml>=6.0
python -m pip install --upgrade requests>=2.31.0
python -m pip install --upgrade psutil>=5.9.0

if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    print_info "Please check your internet connection and try again"
    exit 1
fi

echo
print_success "Dependencies installed successfully!"
echo

# Create data directory
mkdir -p data
mkdir -p logs

# Check if configuration exists
if [ ! -f "config/.env" ]; then
    print_info "Configuration not found. Running setup wizard..."
    python -c "from utils.setup import create_config; create_config()"
    if [ $? -ne 0 ]; then
        print_error "Setup failed. Please check the error messages above."
        exit 1
    fi
else
    print_info "Configuration found. Validating..."
    python -c "from utils.helpers import load_config; load_config(); print('Configuration valid')"
    if [ $? -ne 0 ]; then
        print_warning "Configuration validation failed. You may need to update your config."
        echo -n "Would you like to run the setup wizard? (y/N): "
        read -r choice
        if [[ $choice =~ ^[Yy]$ ]]; then
            python -c "from utils.setup import create_config; create_config()"
        fi
    fi
fi

# Set executable permissions
chmod +x run.sh

echo
print_info "Starting Discord AI Selfbot..."
echo
echo -e "${CYAN}"
echo "============================================"
echo "          Bot is now running!"
echo "    Press Ctrl+C to stop the bot"
echo "============================================"
echo -e "${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo
    print_info "Bot stopped. Cleaning up..."
    deactivate 2>/dev/null || true
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Run the bot
python main.py

# If we get here, the bot stopped normally
cleanup

