@echo off
title Discord AI Selfbot - 2025 Edition
color 0A

echo.
echo ============================================
echo     Discord AI Selfbot - Setup Script
echo           2025 Enhanced Edition
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found. Checking version...
python -c "import sys; print(f'Python {sys.version}')"

REM Check if we're in a virtual environment
python -c "import sys; print('Virtual environment detected' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'No virtual environment')"

echo.
echo [INFO] Setting up Discord AI Selfbot...
echo.

REM Create virtual environment if it doesn't exist
if not exist "bot-env" (
    echo [INFO] Creating virtual environment...
    python -m venv bot-env
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call bot-env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [INFO] Installing/updating dependencies...
echo This may take a few minutes...

REM Core dependencies for 2025 compatibility
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

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Dependencies installed successfully!
echo.

REM Check if configuration exists
if not exist "config\.env" (
    echo [INFO] Configuration not found. Running setup wizard...
    python -c "from utils.setup import create_config; create_config()"
    if %errorlevel% neq 0 (
        echo [ERROR] Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Configuration found. Validating...
    python -c "from utils.helpers import load_config; load_config(); print('Configuration valid')"
    if %errorlevel% neq 0 (
        echo [WARNING] Configuration validation failed. You may need to update your config.
        echo Would you like to run the setup wizard? (Y/N)
        set /p choice="> "
        if /i "%choice%"=="Y" (
            python -c "from utils.setup import create_config; create_config()"
        )
    )
)

echo.
echo [INFO] Starting Discord AI Selfbot...
echo.
echo ============================================
echo          Bot is now running!
echo    Press Ctrl+C to stop the bot
echo ============================================
echo.

REM Run the bot
python main.py

REM If we get here, the bot stopped
echo.
echo [INFO] Bot stopped. Press any key to exit...
pause >nul

