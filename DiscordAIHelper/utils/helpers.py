"""
Helper utilities for Discord AI Selfbot
Enhanced for 2025 with better error handling and modern Python practices
"""

import os
import sys
import yaml
import platform
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def clear_console():
    """Clear the console screen cross-platform"""
    try:
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        # Fallback: print newlines
        print("\n" * 50)

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_env_path() -> str:
    """Get path to .env file"""
    return resource_path("config/.env")

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to YAML file"""
    try:
        config_path = resource_path("config/config.yaml")
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file with enhanced error handling"""
    config_path = resource_path("config/config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Validate required fields
        required_fields = [
            "bot.owner_id",
            "bot.prefix", 
            "bot.trigger",
            "bot.groq_model"
        ]
        
        for field in required_fields:
            keys = field.split('.')
            value = config
            try:
                for key in keys:
                    value = value[key]
                if value is None:
                    raise ValueError(f"Required field {field} is None")
            except (KeyError, TypeError):
                raise ValueError(f"Required field {field} is missing from config")
        
        # Set defaults for new fields
        config.setdefault("security", {})
        config.setdefault("ai", {})
        config.setdefault("advanced", {})
        config.setdefault("notifications", {})
        
        # Bot defaults
        bot_config = config["bot"]
        bot_config.setdefault("max_messages_per_minute", 10)
        bot_config.setdefault("cooldown_duration", 60)
        bot_config.setdefault("conversation_timeout", 300)
        bot_config.setdefault("realistic_typing", True)
        bot_config.setdefault("batch_messages", True)
        bot_config.setdefault("batch_wait_time", 8.0)
        bot_config.setdefault("hold_conversation", True)
        bot_config.setdefault("anti_age_ban", True)
        bot_config.setdefault("disable_mentions", True)
        bot_config.setdefault("reply_ping", True)
        bot_config.setdefault("help_command_enabled", True)
        bot_config.setdefault("allow_dm", True)
        bot_config.setdefault("allow_gc", True)
        
        # Security defaults
        security_config = config["security"]
        security_config.setdefault("random_delays", True)
        security_config.setdefault("typing_variation", True)
        security_config.setdefault("message_variation", True)
        security_config.setdefault("adaptive_cooldowns", True)
        security_config.setdefault("smart_batching", True)
        security_config.setdefault("detailed_logging", True)
        security_config.setdefault("error_tracking", True)
        
        # AI defaults
        ai_config = config["ai"]
        ai_config.setdefault("max_response_length", 2000)
        ai_config.setdefault("context_window", 20)
        ai_config.setdefault("temperature", 0.7)
        ai_config.setdefault("content_filter", True)
        ai_config.setdefault("profanity_filter", False)
        
        # Groq settings
        ai_config.setdefault("groq_settings", {
            "max_tokens": 1024,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        })
        
        # OpenAI settings
        ai_config.setdefault("openai_settings", {
            "max_tokens": 1024,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        })
        
        # Notification defaults
        notifications_config = config["notifications"]
        notifications_config.setdefault("error_webhook", "")
        notifications_config.setdefault("ratelimit_notifications", True)
        notifications_config.setdefault("error_notifications", True)
        notifications_config.setdefault("startup_notifications", False)
        
        # Advanced defaults
        advanced_config = config["advanced"]
        advanced_config.setdefault("conversation_memory", True)
        advanced_config.setdefault("user_preferences", True)
        advanced_config.setdefault("message_caching", True)
        advanced_config.setdefault("response_caching", False)
        advanced_config.setdefault("sentiment_analysis", False)
        advanced_config.setdefault("topic_detection", False)
        advanced_config.setdefault("multilingual_support", False)
        
        logger.info("Configuration loaded successfully")
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise ValueError(f"Error parsing YAML configuration: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise

def load_instructions() -> str:
    """Load AI instructions from file with fallback"""
    instructions_path = resource_path("config/instructions.txt")
    
    try:
        with open(instructions_path, 'r', encoding='utf-8') as file:
            instructions = file.read().strip()
        
        if not instructions:
            logger.warning("Instructions file is empty, using default")
            return get_default_instructions()
        
        logger.info("AI instructions loaded successfully")
        return instructions
        
    except FileNotFoundError:
        logger.warning(f"Instructions file not found: {instructions_path}, using default")
        return get_default_instructions()
    except Exception as e:
        logger.error(f"Error loading instructions: {e}, using default")
        return get_default_instructions()

def get_default_instructions() -> str:
    """Get default AI instructions"""
    return """You are a helpful, friendly, and engaging AI assistant. Be conversational and natural in your responses, show personality, and adapt your tone to match the conversation. Keep responses concise but informative, and be respectful to all users."""

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to YAML file"""
    config_path = resource_path("config/config.yaml")
    
    try:
        # Create backup
        backup_path = f"{config_path}.backup"
        if os.path.exists(config_path):
            import shutil
            shutil.copy2(config_path, backup_path)
        
        # Save new config
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, indent=2)
        
        logger.info("Configuration saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False

def get_file_size(file_path: str) -> Optional[int]:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return None

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_discord_token(token: str) -> bool:
    """Enhanced Discord token validation for 2025"""
    if not token or len(token.strip()) == 0:
        return False
    
    token = token.strip()
    
    # Skip validation for placeholder values
    if token == "your_discord_token_here":
        return False
    
    # Enhanced validation - User tokens can have different formats
    import re
    
    # Modern user token patterns (more flexible for 2025)
    patterns = [
        r'^[A-Za-z0-9_-]{20,}\..*\..*',  # Classic format with dots
        r'^[A-Za-z0-9_-]{50,}$',        # Modern format without dots
        r'^MTA[A-Za-z0-9_-]{50,}$',     # User token starting with MTA
        r'^MTU[A-Za-z0-9_-]{50,}$',     # User token starting with MTU
        r'^Nz[A-Za-z0-9_-]{50,}$',      # User token starting with Nz
        r'^OD[A-Za-z0-9_-]{50,}$',      # User token starting with OD
    ]
    
    # Check if token matches any valid pattern
    for pattern in patterns:
        if re.match(pattern, token):
            return True
    
    # If no pattern matches but token is long enough, accept it
    # This handles edge cases and new formats Discord might introduce
    return len(token) >= 50

def validate_api_key(api_key: str, service: str = "groq") -> bool:
    """Validate API key format"""
    if not api_key or len(api_key.strip()) == 0:
        return False
    
    api_key = api_key.strip()
    
    if service.lower() == "groq":
        # Groq API keys typically start with "gsk_"
        return api_key.startswith("gsk_") and len(api_key) > 20
    elif service.lower() == "openai":
        # OpenAI API keys typically start with "sk-"
        return api_key.startswith("sk-") and len(api_key) > 20
    
    return len(api_key) > 10  # Generic validation

def get_system_info() -> Dict[str, str]:
    """Get system information for debugging"""
    import sys
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor() or "Unknown",
        "system": platform.system(),
        "release": platform.release()
    }
