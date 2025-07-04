# Discord AI Selfbot - 2025 Edition

## Overview

This is a Discord selfbot application built with Python that integrates AI capabilities through Groq and OpenAI APIs. The bot can engage in conversations, analyze images, and provide various utility commands. It's designed with modern Python practices, enhanced security features, and comprehensive error handling.

**Important Note**: This is an educational project that violates Discord's Terms of Service. Use at your own risk.

## System Architecture

### Frontend Architecture
- **Discord Interface**: Uses `discord.py-self` library for Discord API interaction
- **Command System**: Implements a cog-based command structure with separate modules for general and admin commands
- **User Interface**: Terminal-based interface with colorized output using `colorama`

### Backend Architecture
- **Event-Driven**: Asynchronous event handling for Discord messages and commands
- **Modular Design**: Organized into separate utilities for AI, database, error handling, and helpers
- **State Management**: Maintains conversation context and user preferences in memory and database

### Database Architecture
- **SQLite Database**: Local file-based storage for persistence
- **Thread-Safe Operations**: Uses thread-local storage for database connections
- **Connection Pooling**: Context manager pattern for automatic connection cleanup

## Key Components

### Core Bot (`main.py`)
- Main bot instance and event handlers
- Message processing and AI response generation
- Rate limiting and anti-detection measures
- Conversation memory and context management

### Command System (`cogs/`)
- **GeneralCommands**: User-facing commands (help, stats, channel management)
- **AdminCommands**: Owner-only commands (reload, maintenance, system info)

### AI Integration (`utils/ai.py`)
- **Groq API**: Primary AI provider using `llama-3.3-70b-versatile` model
- **OpenAI**: Fallback provider using `gpt-4o` model
- **Image Analysis**: Vision model support for image recognition
- **Error Handling**: Automatic fallback between providers

### Database Operations (`utils/db.py`)
- Channel management (active channels for AI responses)
- User management (ignored users, statistics)
- Conversation logging and error tracking
- Data cleanup and maintenance functions

### Error Management (`utils/error_notifications.py`)
- Discord webhook notifications for errors
- Rate limiting for error notifications
- Comprehensive error logging and categorization

## Data Flow

1. **Message Reception**: Bot receives Discord messages through websocket connection
2. **Processing Pipeline**: 
   - Check if channel is active for AI responses
   - Validate user permissions and rate limits
   - Extract message content and context
3. **AI Processing**:
   - Send message to primary AI provider (Groq)
   - Fallback to secondary provider (OpenAI) if needed
   - Process response and handle errors
4. **Response Generation**:
   - Split long responses into Discord-compatible chunks
   - Apply typing simulation for realistic behavior
   - Send response with rate limiting
5. **Data Storage**: Log conversation data and statistics to SQLite database

## External Dependencies

### AI Providers
- **Groq API**: Primary AI service with free tier
- **OpenAI API**: Secondary AI service for fallback

### Python Libraries
- `discord.py-self`: Discord API interaction
- `groq`: Groq API client
- `openai`: OpenAI API client
- `sqlite3`: Database operations
- `httpx`: HTTP requests
- `yaml`: Configuration file parsing
- `colorama`: Terminal color output

### Environment Variables
- `DISCORD_TOKEN`: Discord user token
- `GROQ_API_KEY`: Groq API key
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ERROR_WEBHOOK_URL`: Discord webhook for error notifications (optional)

## Deployment Strategy

### Local Development
- Python 3.13+ required
- Virtual environment recommended
- Configuration through YAML files and environment variables
- Setup wizard for initial configuration

### Production Considerations
- **Security**: Anti-detection measures and rate limiting
- **Monitoring**: Error logging and webhook notifications
- **Maintenance**: Database cleanup and system monitoring commands
- **Reliability**: Automatic fallback between AI providers

### File Structure
```
├── main.py                 # Main bot application
├── cogs/                   # Command modules
├── utils/                  # Utility modules
├── config/                 # Configuration files
└── data/                   # Database and logs
```

## Changelog

- July 04, 2025: **Complete Web Dashboard with Advanced Features**
  - ✅ **Full Web Dashboard** - Modern, responsive interface for complete bot control
  - ✅ **Fixed Multiple Response Bug** - Simplified message handling to prevent bot responding multiple times to same message
  - ✅ **Fixed Owner Commands** - Commands now work properly for bot owner with correct prefix (~)
  - ✅ **Real-time Bot Control** - Start/stop bot, view live logs, manage configuration through web interface
  - ✅ **Send Messages from Website** - Send messages to any Discord channel directly through the web interface
  - ✅ **Join Servers from Website** - Enter Discord invite links to join new servers automatically
  - ✅ **Execute Commands from Website** - Run bot commands like ~help, ~ping, ~status directly from web interface
  - ✅ **Channel Management** - View all available channels with guild names, refresh automatically
  - ✅ **Enhanced System Monitoring** - Detailed CPU (per-core, frequency, load average), memory (RAM/swap), disk, network, and process-specific monitoring
  - ✅ **Configuration Reload Feature** - Reload configuration from files without restarting the web interface
  - ✅ **Configuration Management** - Easy form-based setup for Discord token, API keys, and bot settings
  - ✅ **Live Log Viewing** - Real-time bot logs with WebSocket updates and error tracking
  - ✅ **Enhanced Security** - Web interface validates tokens and API keys before saving
  - ✅ **Mobile Responsive** - Bootstrap-based UI works on all devices
  - ✅ **Error Monitoring** - Centralized error tracking and notification system

- July 02, 2025: **Project Successfully Modernized for 2025**
  - ✅ Updated to Python 3.11+ compatibility
  - ✅ Integrated latest AI models (Groq llama-3.3-70b-versatile, OpenAI gpt-4o)
  - ✅ Enhanced security with comprehensive anti-detection measures
  - ✅ Added automated setup scripts for Replit environment
  - ✅ Implemented health monitoring and error tracking
  - ✅ Created comprehensive documentation and configuration system
  - ✅ Fixed AI response issues and token handling
  - ✅ Configured chill AI personality with minimal emojis
  - ✅ Made toggle commands discreet with silent reactions
  - ✅ Enhanced anti-detection with startup delays, realistic typing patterns, and human-like response timing
  - ✅ Fixed AI repetition issues with improved conversation memory and response variety guidelines
  - ✅ Enhanced AI to learn from human typing patterns and act more naturally like a real person instead of an AI
  - ✅ Enhanced AI to use context and think more naturally in conversations instead of one-time responses
  - ✅ **Implemented Auto-Conversation Feature** - Bot can now automatically initiate conversations in targeted servers without waiting for others to speak first
  - ✅ **Fixed Command Errors and Enhanced Intelligence** (Previous update):
    - Fixed embed-related command errors by converting to plain text responses
    - Added Discord Rich Presence (RPC) functionality to set custom status
    - Enhanced AI intelligence with better conversation context and critical thinking
    - Made bot significantly more discreet with reaction-based confirmations
    - Improved AI parameters for smarter responses (higher context window, better penalties)
    - Commands now send help to DMs when possible for discretion
    - Reduced auto-conversation frequency and message rates for stealth
    - Disabled reply pings to avoid detection
    - Enhanced instructions for more thoughtful and engaging conversations
  - ✅ **Fixed Self-Conversation Bug and Added Termux Support** (Latest update):
    - Fixed critical bug where bot was talking to itself in DMs
    - Added multiple layers of protection to prevent self-responses
    - Created comprehensive Termux setup guide for Android users
    - Added automatic installation script for easy Termux deployment
    - Enhanced anti-detection with improved message filtering

## User Preferences

Preferred communication style: Simple, everyday language.
AI personality: Chill, laid-back, minimal emojis, casual texting style like hanging out with friends.