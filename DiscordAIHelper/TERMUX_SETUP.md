# Running Discord AI Selfbot on Termux (Android)

This guide will help you set up and run the Discord AI Selfbot on your Android device using Termux.

## Prerequisites

1. **Termux App** - Install from F-Droid (recommended) or GitHub releases
   - Download from: https://f-droid.org/en/packages/com.termux/
   - DO NOT use Google Play Store version (it's outdated)

2. **Android Device Requirements**
   - Android 7.0+ (API level 24+)
   - At least 2GB RAM recommended
   - Stable internet connection

## Step 1: Initial Termux Setup

Open Termux and run these commands:

```bash
# Update package repositories
pkg update && pkg upgrade -y

# Install essential packages
pkg install -y python git nodejs wget curl

# Install Python packages manager
pip install --upgrade pip

# Set up storage access (optional but recommended)
termux-setup-storage
```

## Step 2: Install Required Dependencies

```bash
# Install Python dependencies for the bot
pip install aiohttp colorama discord.py-self groq httpx openai psutil python-dotenv pyyaml requests

# Install additional tools
pkg install -y nano vim
```

## Step 3: Download the Selfbot

```bash
# Clone the repository
git clone <your-repo-url> discord-selfbot
cd discord-selfbot

# Or if you have the files locally, create the directory
mkdir discord-selfbot
cd discord-selfbot
```

## Step 4: Configuration Setup

1. **Create configuration files:**

```bash
# Create config directory
mkdir -p config

# Create .env file
nano config/.env
```

Add your tokens to the `.env` file:
```
DISCORD_TOKEN=your_discord_token_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

2. **Copy configuration files:**
Make sure you have these files in the `config/` directory:
- `config.yaml`
- `instructions.txt`

## Step 5: Termux-Specific Optimizations

Create a startup script for easier management:

```bash
# Create startup script
nano start_bot.sh
```

Add this content to `start_bot.sh`:
```bash
#!/bin/bash
cd ~/discord-selfbot

# Prevent Termux from sleeping
termux-wake-lock

# Set environment variables
export PYTHONUNBUFFERED=1
export TERM=xterm-256color

# Start the bot with auto-restart
while true; do
    echo "Starting Discord AI Selfbot..."
    python main.py
    echo "Bot stopped. Restarting in 5 seconds..."
    sleep 5
done
```

Make it executable:
```bash
chmod +x start_bot.sh
```

## Step 6: Running the Bot

### Method 1: Direct Execution
```bash
cd discord-selfbot
python main.py
```

### Method 2: Using Startup Script
```bash
./start_bot.sh
```

### Method 3: Background Execution
```bash
# Run in background (bot continues even if you close Termux)
nohup ./start_bot.sh > bot.log 2>&1 &

# Check if it's running
ps aux | grep python

# View logs
tail -f bot.log
```

## Step 7: Termux Session Management

To keep the bot running when you close Termux:

1. **Install Termux:Boot (optional):**
   - Download from F-Droid
   - Allows auto-start on device boot

2. **Use tmux for session persistence:**
```bash
# Install tmux
pkg install tmux

# Start a new session
tmux new-session -d -s selfbot

# Attach to session
tmux attach-session -t selfbot

# Run your bot in the session
./start_bot.sh

# Detach from session (Ctrl+B, then D)
# Session continues running in background
```

## Important Termux Commands

```bash
# Check running processes
ps aux | grep python

# Kill the bot process
pkill -f main.py

# Check memory usage
free -h

# Check storage space
df -h

# Update packages
pkg update && pkg upgrade

# View bot logs
tail -f selfbot.log
```

## Troubleshooting

### Common Issues:

1. **Permission Denied:**
```bash
chmod +x main.py
chmod +x start_bot.sh
```

2. **Module Not Found:**
```bash
pip install --upgrade pip
pip install [missing-module-name]
```

3. **Network Issues:**
```bash
# Check internet connection
ping google.com

# Restart Termux networking
termux-reload-settings
```

4. **Memory Issues:**
```bash
# Clear package cache
pkg clean

# Check memory usage
free -h
```

### Performance Optimization:

1. **Reduce memory usage:**
   - Close unnecessary apps
   - Lower AI context window in config
   - Disable auto-conversation feature

2. **Battery optimization:**
   - Disable battery optimization for Termux in Android settings
   - Use `termux-wake-lock` to prevent sleeping

3. **Stability improvements:**
   - Use stable WiFi connection
   - Keep device charged
   - Monitor temperature (avoid overheating)

## Auto-Start on Boot (Advanced)

1. **Install Termux:Boot**
2. **Create boot script:**

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-selfbot.sh
```

Add:
```bash
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
cd ~/discord-selfbot
./start_bot.sh
```

Make executable:
```bash
chmod +x ~/.termux/boot/start-selfbot.sh
```

## Security Considerations

1. **Protect your tokens:**
   - Never share your Discord token
   - Use secure WiFi networks
   - Consider using a VPN

2. **Device security:**
   - Lock your phone with PIN/password
   - Don't run on public/shared devices
   - Regularly update Termux and packages

## Commands for Managing the Bot

```bash
# Start bot
./start_bot.sh

# Stop bot
pkill -f main.py

# Restart bot
pkill -f main.py && ./start_bot.sh

# Update bot
git pull
pip install -r requirements.txt

# View status
ps aux | grep python
```

## Tips for Success

1. **Keep Termux updated** - Regular updates fix bugs and improve performance
2. **Monitor resource usage** - Check memory and CPU usage regularly
3. **Use stable internet** - Mobile data or stable WiFi works best
4. **Battery management** - Keep device charged or plugged in
5. **Regular backups** - Backup your config files and tokens

Your Discord AI Selfbot should now be running successfully on Termux!