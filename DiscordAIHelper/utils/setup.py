"""
Setup utilities for Discord AI Selfbot
Enhanced configuration wizard for 2025
"""

import os
import sys
import getpass
from pathlib import Path
from colorama import Fore, Style, init
from typing import Dict, Any, Optional
import logging

from .helpers import resource_path, save_config, validate_discord_token, validate_api_key

init()
logger = logging.getLogger(__name__)

def print_banner():
    """Print setup banner"""
    print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║          Discord AI Selfbot Setup - 2025 Edition            ║")
    print(f"║                    Configuration Wizard                     ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

def print_warning():
    """Print important warnings"""
    print(f"{Fore.RED}⚠️  IMPORTANT WARNINGS ⚠️{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}• Using selfbots violates Discord's Terms of Service")
    print(f"• Your account could be banned (risk is low but exists)")
    print(f"• Use an account you don't mind losing")
    print(f"• This tool is for educational purposes{Style.RESET_ALL}\n")
    
    response = input(f"{Fore.CYAN}Do you understand and accept these risks? (yes/no): {Style.RESET_ALL}")
    if response.lower() not in ['yes', 'y']:
        print(f"{Fore.RED}Setup cancelled.{Style.RESET_ALL}")
        sys.exit(1)
    print()

def get_discord_token() -> str:
    """Get Discord token from user with validation"""
    print(f"{Fore.GREEN}📱 Discord Token Setup{Style.RESET_ALL}")
    print("To get your Discord token:")
    print("1. Open Discord in your browser")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the Network tab")
    print("4. Send a message or change servers")
    print("5. Look for a request and find 'Authorization' in headers")
    print("6. Copy the token value\n")
    
    while True:
        token = getpass.getpass(f"{Fore.CYAN}Enter your Discord token: {Style.RESET_ALL}")
        
        if not token:
            print(f"{Fore.RED}Token cannot be empty!{Style.RESET_ALL}")
            continue
        
        if validate_discord_token(token):
            return token.strip()
        else:
            print(f"{Fore.RED}Invalid token format! Please check and try again.{Style.RESET_ALL}")

def get_owner_id() -> int:
    """Get owner ID from user"""
    print(f"\n{Fore.GREEN}👤 Owner ID Setup{Style.RESET_ALL}")
    print("Your Discord User ID (not the bot account's ID)")
    print("To get your ID: Enable Developer Mode in Discord settings,")
    print("then right-click on your profile and select 'Copy User ID'\n")
    
    while True:
        try:
            owner_id = input(f"{Fore.CYAN}Enter your Discord User ID: {Style.RESET_ALL}")
            owner_id = int(owner_id.strip())
            
            if owner_id > 0:
                return owner_id
            else:
                print(f"{Fore.RED}Invalid ID! Must be a positive number.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid ID! Must be a number.{Style.RESET_ALL}")

def get_trigger_word() -> str:
    """Get trigger word from user"""
    print(f"\n{Fore.GREEN}🎯 Trigger Word Setup{Style.RESET_ALL}")
    print("This is the word that will make the bot respond to messages")
    print("Example: If you set 'Alex', people need to say 'Hey Alex' to trigger the bot")
    print("You can use multiple words separated by commas: 'Alex,Alexander,Al'\n")
    
    while True:
        trigger = input(f"{Fore.CYAN}Enter trigger word(s): {Style.RESET_ALL}").strip()
        
        if not trigger:
            print(f"{Fore.RED}Trigger word cannot be empty!{Style.RESET_ALL}")
            continue
        
        if len(trigger) < 2:
            print(f"{Fore.RED}Trigger word must be at least 2 characters long!{Style.RESET_ALL}")
            continue
        
        return trigger

def get_api_keys() -> Dict[str, str]:
    """Get API keys from user"""
    print(f"\n{Fore.GREEN}🔑 API Keys Setup{Style.RESET_ALL}")
    print("You need at least one AI service API key:")
    print("• Groq: Free tier available (Recommended)")
    print("• OpenAI: Paid service\n")
    
    api_keys = {}
    
    # Groq API Key
    print(f"{Fore.CYAN}Groq API Key (Recommended){Style.RESET_ALL}")
    print("Get free API key from: https://console.groq.com/keys")
    groq_key = input(f"{Fore.CYAN}Enter Groq API key (or press Enter to skip): {Style.RESET_ALL}").strip()
    
    if groq_key and validate_api_key(groq_key, "groq"):
        api_keys["GROQ_API_KEY"] = groq_key
        print(f"{Fore.GREEN}✓ Valid Groq API key{Style.RESET_ALL}")
    elif groq_key:
        print(f"{Fore.YELLOW}⚠ Invalid Groq API key format, skipping{Style.RESET_ALL}")
    
    # OpenAI API Key
    print(f"\n{Fore.CYAN}OpenAI API Key (Optional){Style.RESET_ALL}")
    print("Get API key from: https://platform.openai.com/api-keys")
    openai_key = input(f"{Fore.CYAN}Enter OpenAI API key (or press Enter to skip): {Style.RESET_ALL}").strip()
    
    if openai_key and validate_api_key(openai_key, "openai"):
        api_keys["OPENAI_API_KEY"] = openai_key
        print(f"{Fore.GREEN}✓ Valid OpenAI API key{Style.RESET_ALL}")
    elif openai_key:
        print(f"{Fore.YELLOW}⚠ Invalid OpenAI API key format, skipping{Style.RESET_ALL}")
    
    if not api_keys:
        print(f"{Fore.RED}Error: You need at least one valid API key to continue!{Style.RESET_ALL}")
        return get_api_keys()  # Retry
    
    return api_keys

def get_bot_settings() -> Dict[str, Any]:
    """Get bot behavior settings"""
    print(f"\n{Fore.GREEN}⚙️ Bot Behavior Settings{Style.RESET_ALL}")
    
    settings = {}
    
    # Realistic typing
    response = input(f"{Fore.CYAN}Enable realistic typing delays? (y/n) [default: y]: {Style.RESET_ALL}").strip().lower()
    settings["realistic_typing"] = response != 'n'
    
    # DM responses
    response = input(f"{Fore.CYAN}Respond to direct messages? (y/n) [default: y]: {Style.RESET_ALL}").strip().lower()
    settings["allow_dm"] = response != 'n'
    
    # Group chat responses
    response = input(f"{Fore.CYAN}Respond in group chats? (y/n) [default: y]: {Style.RESET_ALL}").strip().lower()
    settings["allow_gc"] = response != 'n'
    
    # Conversation holding
    response = input(f"{Fore.CYAN}Continue conversations without triggers? (y/n) [default: y]: {Style.RESET_ALL}").strip().lower()
    settings["hold_conversation"] = response != 'n'
    
    # Anti-age ban
    response = input(f"{Fore.CYAN}Enable anti-age ban protection? (y/n) [default: y]: {Style.RESET_ALL}").strip().lower()
    settings["anti_age_ban"] = response != 'n'
    
    return settings

def create_env_file(api_keys: Dict[str, str], token: str) -> bool:
    """Create .env file"""
    try:
        env_path = resource_path("config/.env")
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        
        with open(env_path, 'w') as f:
            f.write("# Discord AI Selfbot Environment Configuration - 2025 Edition\n")
            f.write("# Generated by setup wizard\n\n")
            
            f.write("# Discord Token (Required)\n")
            f.write(f"DISCORD_TOKEN={token}\n\n")
            
            for key, value in api_keys.items():
                service = key.split('_')[0].title()
                f.write(f"# {service} API Key\n")
                f.write(f"{key}={value}\n\n")
            
            # Optional settings with defaults
            f.write("# Optional Configuration\n")
            f.write("ERROR_WEBHOOK_URL=\n")
            f.write("DATABASE_URL=sqlite:///selfbot.db\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("LOG_FILE=selfbot.log\n")
        
        print(f"{Fore.GREEN}✓ Environment file created successfully{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error creating environment file: {e}{Style.RESET_ALL}")
        return False

def create_config_file(owner_id: int, trigger: str, settings: Dict[str, Any]) -> bool:
    """Create config.yaml file"""
    try:
        config = {
            "bot": {
                "owner_id": owner_id,
                "prefix": "~",
                "trigger": trigger,
                "groq_model": "llama-3.3-70b-versatile",  # Updated model
                "openai_model": "gpt-4o",  # Latest OpenAI model
                "allow_dm": settings.get("allow_dm", True),
                "allow_gc": settings.get("allow_gc", True),
                "reply_ping": True,
                "realistic_typing": settings.get("realistic_typing", True),
                "batch_messages": True,
                "batch_wait_time": 8.0,
                "hold_conversation": settings.get("hold_conversation", True),
                "anti_age_ban": settings.get("anti_age_ban", True),
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
        
        if save_config(config):
            print(f"{Fore.GREEN}✓ Configuration file created successfully{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ Error creating configuration file{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}✗ Error creating configuration file: {e}{Style.RESET_ALL}")
        return False

def create_instructions_file() -> bool:
    """Create instructions.txt file"""
    try:
        instructions_path = resource_path("config/instructions.txt")
        os.makedirs(os.path.dirname(instructions_path), exist_ok=True)
        
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
        
        print(f"{Fore.GREEN}✓ Instructions file created successfully{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error creating instructions file: {e}{Style.RESET_ALL}")
        return False

def create_config():
    """Main configuration creation function"""
    try:
        print_banner()
        print_warning()
        
        # Collect user input
        token = get_discord_token()
        owner_id = get_owner_id()
        trigger = get_trigger_word()
        api_keys = get_api_keys()
        bot_settings = get_bot_settings()
        
        print(f"\n{Fore.GREEN}📁 Creating configuration files...{Style.RESET_ALL}")
        
        # Create files
        success = True
        success &= create_env_file(api_keys, token)
        success &= create_config_file(owner_id, trigger, bot_settings)
        success &= create_instructions_file()
        
        if success:
            print(f"\n{Fore.GREEN}✅ Setup completed successfully!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
            print("1. Run the bot with: python main.py")
            print("2. Use ~help to see available commands")
            print("3. Use ~toggleactive in a channel to activate the bot")
            print(f"\n{Fore.YELLOW}Join our Discord for support: https://discord.gg/yUWmzQBV4P{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Setup failed! Please check the errors above.{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup cancelled by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error during setup: {e}{Style.RESET_ALL}")
        logger.error(f"Setup error: {e}")

if __name__ == "__main__":
    create_config()
