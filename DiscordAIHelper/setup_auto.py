#!/usr/bin/env python3
"""
Automatic setup script for Discord AI Selfbot
Non-interactive configuration for automated environments like Replit
"""

import os
import yaml
from pathlib import Path

def create_default_config():
    """Create default configuration files"""
    
    # Ensure config directory exists
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create config.yaml with default settings
    config = {
        "bot": {
            "owner_id": 123456789012345678,  # Placeholder - needs to be updated by user
            "prefix": "~",
            "trigger": "AI",  # Default trigger word
            "groq_model": "llama-3.3-70b-versatile",
            "openai_model": "gpt-4o",
            "allow_dm": True,
            "allow_gc": True,
            "reply_ping": True,
            "realistic_typing": True,
            "batch_messages": True,
            "batch_wait_time": 8.0,
            "hold_conversation": True,
            "anti_age_ban": True,
            "disable_mentions": True,
            "help_command_enabled": True,
            "max_messages_per_minute": 10,
            "cooldown_duration": 60,
            "conversation_timeout": 300
        },
        "security": {
            "random_delays": True,
            "typing_variation": True,
            "message_variation": True,
            "adaptive_cooldowns": True,
            "smart_batching": True,
            "detailed_logging": True,
            "error_tracking": True
        },
        "ai": {
            "max_response_length": 2000,
            "context_window": 20,
            "temperature": 0.7,
            "content_filter": True,
            "profanity_filter": False,
            "groq_settings": {
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            },
            "openai_settings": {
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "notifications": {
            "error_webhook": "",
            "ratelimit_notifications": True,
            "error_notifications": True,
            "startup_notifications": False
        },
        "advanced": {
            "conversation_memory": True,
            "user_preferences": True,
            "message_caching": True,
            "response_caching": False,
            "sentiment_analysis": False,
            "topic_detection": False,
            "multilingual_support": False
        }
    }
    
    # Save config.yaml
    config_path = config_dir / "config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"✓ Created default config.yaml")
    
    # Create instructions.txt
    instructions_path = config_dir / "instructions.txt"
    default_instructions = """You are a helpful, friendly, and engaging AI assistant. You should:

1. Be conversational and natural in your responses
2. Show personality and character in your interactions
3. Ask follow-up questions to keep conversations engaging
4. Be helpful and informative when needed
5. Use emojis occasionally to add personality (but don't overuse them)
6. Adapt your tone to match the conversation style
7. Be concise but informative - avoid overly long responses
8. Remember context from the conversation
9. Be respectful and considerate to all users
10. If you're unsure about something, admit it rather than guessing

Additional guidelines:
- Respond as if you're a real person in a Discord chat
- Keep responses under 2000 characters when possible
- Don't mention that you're an AI unless directly asked
- Be authentic and genuine in your interactions
- Maintain appropriate boundaries and be helpful"""
    
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(default_instructions)
    
    print(f"✓ Created default instructions.txt")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Created data directory")
    
    return True

def setup_environment():
    """Set up the environment for the selfbot"""
    
    print("🤖 Discord AI Selfbot - Automatic Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_path = Path("config/.env")
    if env_path.exists():
        print("✓ Environment file already exists")
    else:
        print("❌ Environment file missing - please create config/.env with your tokens")
        return False
    
    # Create config files
    if create_default_config():
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update config/config.yaml with your Discord user ID as owner_id")
        print("2. Add your Discord token to config/.env")
        print("3. Add API keys (Groq/OpenAI) to config/.env")
        print("4. Run the bot with: python main.py")
        return True
    else:
        print("\n❌ Setup failed!")
        return False

if __name__ == "__main__":
    setup_environment()