"""
Error notification utilities for Discord AI Selfbot
Enhanced webhook and logging system for 2025
"""

import os
import asyncio
import json
import logging
import traceback
import time
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
import discord

from .db import log_error

logger = logging.getLogger(__name__)

class ErrorNotificationManager:
    """Enhanced error notification system with webhook support"""
    
    def __init__(self):
        self.webhook_url = os.getenv("ERROR_WEBHOOK_URL")
        self.rate_limit_window = {}  # Track rate limits per error type
        self.last_error_times = {}   # Track last occurrence of each error
        self.error_counts = {}       # Count occurrences of each error
        
    async def send_webhook_notification(self, error_data: Dict[str, Any]) -> bool:
        """Send error notification via Discord webhook"""
        if not self.webhook_url:
            return False
        
        try:
            # Create embed for error notification
            embed = {
                "title": "🔴 Discord AI Selfbot Error",
                "color": 0xFF0000,  # Red color
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "Error Type",
                        "value": f"```{error_data.get('error_type', 'Unknown')}```",
                        "inline": True
                    },
                    {
                        "name": "Severity",
                        "value": error_data.get('severity', 'Medium'),
                        "inline": True
                    },
                    {
                        "name": "User ID",
                        "value": str(error_data.get('user_id', 'N/A')),
                        "inline": True
                    },
                    {
                        "name": "Channel ID", 
                        "value": str(error_data.get('channel_id', 'N/A')),
                        "inline": True
                    },
                    {
                        "name": "Error Message",
                        "value": f"```{error_data.get('error_message', 'No message')[:1000]}```",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"Selfbot v3.0.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            # Add stack trace if available (truncated)
            stack_trace = error_data.get('stack_trace')
            if stack_trace:
                embed["fields"].append({
                    "name": "Stack Trace (Truncated)",
                    "value": f"```python\n{stack_trace[:800]}{'...' if len(stack_trace) > 800 else ''}```",
                    "inline": False
                })
            
            payload = {
                "embeds": [embed],
                "username": "Selfbot Error Reporter"
            }
            
            # Send webhook with timeout
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 204:
                    logger.info("Error notification sent successfully via webhook")
                    return True
                else:
                    logger.warning(f"Webhook returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def should_notify(self, error_type: str, error_message: str) -> bool:
        """Determine if we should send notification based on rate limiting"""
        current_time = time.time()
        error_key = f"{error_type}:{hash(error_message) % 10000}"
        
        # Update error count
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
        self.error_counts[error_key] += 1
        
        # Check if we've seen this error recently
        if error_key in self.last_error_times:
            time_since_last = current_time - self.last_error_times[error_key]
            
            # Rate limit: Don't notify for same error within 5 minutes
            if time_since_last < 300:  # 5 minutes
                return False
            
            # If error is happening frequently (>5 times in 1 hour), reduce notifications
            if self.error_counts[error_key] > 5 and time_since_last < 3600:  # 1 hour
                # Only notify every 30 minutes for frequent errors
                return time_since_last > 1800  # 30 minutes
        
        self.last_error_times[error_key] = current_time
        return True
    
    def get_error_severity(self, error_type: str, error_message: str) -> str:
        """Determine error severity level"""
        error_lower = error_message.lower()
        
        # Critical errors
        if any(keyword in error_lower for keyword in [
            'token', 'unauthorized', 'forbidden', 'authentication',
            'database', 'corruption', 'segmentation fault'
        ]):
            return "🔴 Critical"
        
        # High severity
        elif any(keyword in error_lower for keyword in [
            'rate limit', 'quota', 'api', 'connection', 'timeout'
        ]):
            return "🟠 High"
        
        # Medium severity  
        elif any(keyword in error_lower for keyword in [
            'permission', 'missing', 'not found', 'invalid'
        ]):
            return "🟡 Medium"
        
        # Low severity
        else:
            return "🟢 Low"

# Global error notification manager
_error_manager = ErrorNotificationManager()

async def webhook_log(message: discord.Message, error: Any) -> bool:
    """Log error with webhook notification support"""
    try:
        # Extract error information
        if isinstance(error, Exception):
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
        else:
            error_type = "GeneralError"
            error_message = str(error)
            stack_trace = None
        
        # Prepare error data
        error_data = {
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "user_id": message.author.id if message else None,
            "channel_id": message.channel.id if message else None,
            "username": message.author.name if message else None,
            "guild_id": message.guild.id if message and message.guild else None,
            "severity": _error_manager.get_error_severity(error_type, error_message),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to database
        log_error(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            user_id=error_data.get("user_id"),
            channel_id=error_data.get("channel_id")
        )
        
        # Check if we should send webhook notification
        if _error_manager.should_notify(error_type, error_message):
            webhook_sent = await _error_manager.send_webhook_notification(error_data)
            
            if webhook_sent:
                logger.info(f"Error notification sent for {error_type}")
            else:
                logger.warning(f"Failed to send error notification for {error_type}")
            
            return webhook_sent
        else:
            logger.debug(f"Skipped webhook notification for {error_type} (rate limited)")
            return False
            
    except Exception as e:
        logger.error(f"Error in webhook_log function: {e}")
        return False

async def log_startup_event(bot_user: discord.User) -> bool:
    """Log bot startup event"""
    try:
        startup_data = {
            "error_type": "StartupEvent",
            "error_message": f"Bot {bot_user.name} ({bot_user.id}) started successfully",
            "severity": "🟢 Info",
            "user_id": bot_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Only send if startup notifications are enabled
        from .helpers import load_config
        config = load_config()
        
        if config.get("notifications", {}).get("startup_notifications", False):
            return await _error_manager.send_webhook_notification(startup_data)
        
        return True
        
    except Exception as e:
        logger.error(f"Error logging startup event: {e}")
        return False

async def log_rate_limit_event(user_id: int, channel_id: int, retry_after: float) -> bool:
    """Log rate limit events"""
    try:
        rate_limit_data = {
            "error_type": "RateLimitHit",
            "error_message": f"Rate limit hit for user {user_id} in channel {channel_id}. Retry after: {retry_after}s",
            "severity": "🟡 Medium",
            "user_id": user_id,
            "channel_id": channel_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check config for rate limit notifications
        from .helpers import load_config
        config = load_config()
        
        if config.get("notifications", {}).get("ratelimit_notifications", True):
            return await _error_manager.send_webhook_notification(rate_limit_data)
        
        return True
        
    except Exception as e:
        logger.error(f"Error logging rate limit event: {e}")
        return False

async def log_security_event(event_type: str, details: str, user_id: int = None, 
                           channel_id: int = None, severity: str = "High") -> bool:
    """Log security-related events"""
    try:
        security_data = {
            "error_type": f"SecurityEvent_{event_type}",
            "error_message": details,
            "severity": f"🔴 {severity}",
            "user_id": user_id,
            "channel_id": channel_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Security events are always sent (no rate limiting)
        return await _error_manager.send_webhook_notification(security_data)
        
    except Exception as e:
        logger.error(f"Error logging security event: {e}")
        return False

async def log_ai_error(model_used: str, error_message: str, user_id: int = None,
                      tokens_used: int = 0) -> bool:
    """Log AI-specific errors"""
    try:
        ai_error_data = {
            "error_type": "AI_Error",
            "error_message": f"Model: {model_used} | Error: {error_message} | Tokens: {tokens_used}",
            "severity": "🟠 High",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if _error_manager.should_notify("AI_Error", error_message):
            return await _error_manager.send_webhook_notification(ai_error_data)
        
        return True
        
    except Exception as e:
        logger.error(f"Error logging AI error: {e}")
        return False

def get_error_stats() -> Dict[str, Any]:
    """Get error statistics"""
    try:
        return {
            "total_error_types": len(_error_manager.error_counts),
            "total_errors": sum(_error_manager.error_counts.values()),
            "recent_errors": len([t for t in _error_manager.last_error_times.values() 
                                if time.time() - t < 3600]),  # Last hour
            "webhook_configured": bool(_error_manager.webhook_url),
            "most_common_errors": sorted(_error_manager.error_counts.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]
        }
    except Exception as e:
        logger.error(f"Error getting error stats: {e}")
        return {}

async def test_webhook() -> bool:
    """Test webhook notification"""
    try:
        test_data = {
            "error_type": "WebhookTest",
            "error_message": "This is a test notification to verify webhook functionality",
            "severity": "🟢 Info",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await _error_manager.send_webhook_notification(test_data)
        
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        return False

