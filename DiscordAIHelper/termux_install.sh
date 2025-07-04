#!/bin/bash
# Discord AI Selfbot - Termux Installation Script
# Run this script on Termux to automatically set up the selfbot

echo "🤖 Discord AI Selfbot - Termux Setup"
echo "====================================="

# Check if running on Termux
if [[ ! "$PREFIX" == *"com.termux"* ]]; then
    echo "❌ This script is designed for Termux only!"
    exit 1
fi

echo "📱 Detected Termux environment"

# Update packages
echo "📦 Updating packages..."
pkg update -y && pkg upgrade -y

# Install required packages
echo "🔧 Installing dependencies..."
pkg install -y python git nodejs wget curl nano

# Install Python packages
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install aiohttp colorama discord.py-self groq httpx openai psutil python-dotenv pyyaml requests

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p ~/discord-selfbot
cd ~/discord-selfbot

# Create config directory
mkdir -p config
mkdir -p data
mkdir -p logs

# Create .env template
echo "⚙️ Creating configuration template..."
cat > config/.env << EOF
# Discord AI Selfbot Configuration
# Replace with your actual tokens

DISCORD_TOKEN=your_discord_token_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ERROR_WEBHOOK_URL=
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd ~/discord-selfbot

# Prevent Termux from sleeping
termux-wake-lock

# Set environment variables
export PYTHONUNBUFFERED=1
export TERM=xterm-256color

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot with logging
echo "Starting Discord AI Selfbot..."
python main.py 2>&1 | tee logs/bot.log
EOF

chmod +x start_bot.sh

# Create restart script
cat > restart_bot.sh << 'EOF'
#!/bin/bash
echo "Stopping bot..."
pkill -f main.py
sleep 2
echo "Starting bot..."
cd ~/discord-selfbot
./start_bot.sh
EOF

chmod +x restart_bot.sh

# Create background runner
cat > run_background.sh << 'EOF'
#!/bin/bash
cd ~/discord-selfbot
termux-wake-lock
nohup ./start_bot.sh > logs/background.log 2>&1 &
echo "Bot started in background. Check logs with: tail -f ~/discord-selfbot/logs/background.log"
EOF

chmod +x run_background.sh

# Create stop script
cat > stop_bot.sh << 'EOF'
#!/bin/bash
echo "Stopping Discord AI Selfbot..."
pkill -f main.py
termux-wake-unlock
echo "Bot stopped."
EOF

chmod +x stop_bot.sh

# Setup tmux session script
cat > tmux_session.sh << 'EOF'
#!/bin/bash
# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Installing tmux..."
    pkg install tmux -y
fi

# Create or attach to selfbot session
if tmux has-session -t selfbot 2>/dev/null; then
    echo "Attaching to existing selfbot session..."
    tmux attach-session -t selfbot
else
    echo "Creating new selfbot session..."
    tmux new-session -d -s selfbot -c ~/discord-selfbot
    tmux send-keys -t selfbot './start_bot.sh' Enter
    tmux attach-session -t selfbot
fi
EOF

chmod +x tmux_session.sh

# Create requirements.txt for easy reinstallation
cat > requirements.txt << EOF
aiohttp>=3.8.0
colorama>=0.4.4
discord.py-self>=2.0.0
groq>=0.4.0
httpx>=0.24.0
openai>=1.0.0
psutil>=5.9.0
python-dotenv>=1.0.0
PyYAML>=6.0
requests>=2.28.0
EOF

# Create helpful aliases
echo "🔗 Setting up aliases..."
cat >> ~/.bashrc << 'EOF'

# Discord Selfbot Aliases
alias selfbot-start='cd ~/discord-selfbot && ./start_bot.sh'
alias selfbot-stop='cd ~/discord-selfbot && ./stop_bot.sh'
alias selfbot-restart='cd ~/discord-selfbot && ./restart_bot.sh'
alias selfbot-background='cd ~/discord-selfbot && ./run_background.sh'
alias selfbot-tmux='cd ~/discord-selfbot && ./tmux_session.sh'
alias selfbot-logs='tail -f ~/discord-selfbot/logs/bot.log'
alias selfbot-config='nano ~/discord-selfbot/config/.env'
alias selfbot-status='ps aux | grep -v grep | grep main.py'
EOF

echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your bot files to ~/discord-selfbot/"
echo "2. Edit config: nano ~/discord-selfbot/config/.env"
echo "3. Add your Discord token and API keys"
echo "4. Run: ./start_bot.sh"
echo ""
echo "🔧 Useful Commands:"
echo "selfbot-start     - Start the bot"
echo "selfbot-stop      - Stop the bot"
echo "selfbot-restart   - Restart the bot"
echo "selfbot-background - Run in background"
echo "selfbot-tmux      - Run in tmux session"
echo "selfbot-logs      - View bot logs"
echo "selfbot-config    - Edit configuration"
echo "selfbot-status    - Check if bot is running"
echo ""
echo "📱 To enable aliases, restart Termux or run: source ~/.bashrc"
echo ""
echo "⚠️  IMPORTANT: Make sure to add your Discord token to config/.env before starting!"