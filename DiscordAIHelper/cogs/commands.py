"""
General commands cog for Discord AI Selfbot
Enhanced with 2025 features, better error handling, and more discreet operation
"""

import discord
from discord.ext import commands
import asyncio
import time
import logging
import psutil
import platform
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from utils.db import (
    add_channel, remove_channel, get_channels, add_ignored_user, 
    remove_ignored_user, get_ignored_users, log_conversation,
    get_user_stats, get_database_stats, cleanup_old_data
)
from utils.ai import get_ai_status, get_available_models, analyze_sentiment
from utils.error_notifications import webhook_log, test_webhook, get_error_stats
from utils.helpers import load_config, save_config, get_system_info

logger = logging.getLogger(__name__)

class GeneralCommands(commands.Cog):
    """Enhanced general commands for the selfbot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx):
        """Enhanced help command with categorized commands"""
        try:
            config = load_config()
            
            # Check if help is enabled for everyone or owner only
            if not config.get("bot", {}).get("help_command_enabled", True):
                if ctx.author.id != self.bot.state.owner_id:
                    await ctx.message.add_reaction("❌")
                    return
            
            # More discreet help - send as plain text
            help_text = "**Commands:**\n\n"
            
            # Get current prefix from config
            prefix = config.get("bot", {}).get("prefix", "~")
            
            # Basic Commands
            basic_commands = [
                f"{prefix}help - Show commands",
                f"{prefix}ping - Check status", 
                f"{prefix}status - Bot info",
                f"{prefix}toggleactive [channel] - Toggle AI",
                f"{prefix}toggledm - Toggle DMs",
                f"{prefix}togglegc - Toggle groups",
                f"{prefix}pause - Pause responses",
                f"{prefix}wipe - Clear history",
                f"{prefix}ignore @user - Ignore user"
            ]
            help_text += "**Basic:**\n" + "\n".join(f"• {cmd}" for cmd in basic_commands) + "\n\n"
            
            # AI Commands
            ai_commands = [
                f"{prefix}models - List AI models",
                f"{prefix}analyze @user - Analyze user",
                f"{prefix}sentiment <text> - Check sentiment"
            ]
            help_text += "**AI:**\n" + "\n".join(f"• {cmd}" for cmd in ai_commands) + "\n\n"
            
            # Owner Commands (if owner)
            if ctx.author.id == self.bot.state.owner_id:
                owner_commands = [
                    f"{prefix}reload - Reload cogs",
                    f"{prefix}restart - Restart bot", 
                    f"{prefix}cleanup - Clean database",
                    f"{prefix}rpc <activity> - Set Discord status"
                ]
                help_text += "**Owner:**\n" + "\n".join(f"• {cmd}" for cmd in owner_commands) + "\n\n"
            
            # Try to send in DM for discretion, fallback to channel
            try:
                await ctx.author.send(help_text)
                await ctx.message.add_reaction("📬")  # Indicate sent to DM
            except:
                await ctx.send(help_text)
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Enhanced ping command with detailed status"""
        try:
            start_time = time.time()
            websocket_latency = round(self.bot.latency * 1000, 2)
            
            # Send initial ping message
            message = await ctx.send("🏓 Pong!")
            
            # Calculate edit latency
            edit_time = time.time()
            edit_latency = round((edit_time - start_time) * 1000, 2)
            
            # Discreet ping response with minimal info
            ping_text = f"🏓 **{websocket_latency}ms** | **{edit_latency}ms** | **{self.get_uptime()}**"
            await message.edit(content=ping_text)
            
        except Exception as e:
            logger.error(f"Error in ping command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="rpc")
    async def set_discord_rpc(self, ctx, *, activity: str = None):
        """Set Discord Rich Presence status"""
        try:
            if ctx.author.id != self.bot.state.owner_id:
                await ctx.message.add_reaction("❌")
                return
            
            if not activity:
                # Clear activity
                await self.bot.change_presence(activity=None)
                await ctx.message.add_reaction("✅")
                return
            
            # Parse activity type and name
            activity_lower = activity.lower()
            
            if activity_lower.startswith("playing "):
                game_name = activity[8:]  # Remove "playing "
                game_activity = discord.Game(name=game_name)
                await self.bot.change_presence(activity=game_activity)
                
            elif activity_lower.startswith("watching "):
                watch_name = activity[9:]  # Remove "watching "
                watch_activity = discord.Activity(type=discord.ActivityType.watching, name=watch_name)
                await self.bot.change_presence(activity=watch_activity)
                
            elif activity_lower.startswith("listening "):
                listen_name = activity[10:]  # Remove "listening "
                listen_activity = discord.Activity(type=discord.ActivityType.listening, name=listen_name)
                await self.bot.change_presence(activity=listen_activity)
                
            elif activity_lower.startswith("streaming "):
                stream_name = activity[10:]  # Remove "streaming "
                stream_activity = discord.Streaming(name=stream_name, url="https://twitch.tv/placeholder")
                await self.bot.change_presence(activity=stream_activity)
                
            else:
                # Default to playing
                game_activity = discord.Game(name=activity)
                await self.bot.change_presence(activity=game_activity)
            
            await ctx.message.add_reaction("✅")
            
        except Exception as e:
            logger.error(f"Error in RPC command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="status")
    async def status(self, ctx):
        """Detailed bot status information"""
        try:
            # More discreet status response
            ai_status = get_ai_status()
            channels = get_channels()
            ignored = get_ignored_users()
            
            status_text = f"**Status:**\n"
            status_text += f"• Uptime: {self.get_uptime()}\n"
            status_text += f"• Active channels: {len(channels)}\n"
            status_text += f"• Ignored users: {len(ignored)}\n"
            status_text += f"• Groq: {'✅' if ai_status.get('groq_available') else '❌'}\n"
            status_text += f"• OpenAI: {'✅' if ai_status.get('openai_available') else '❌'}\n"
            status_text += f"• Paused: {'Yes' if getattr(self.bot.state, 'paused', False) else 'No'}\n"
            
            await ctx.send(status_text)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="toggleactive", aliases=["ta"])
    async def toggle_active(self, ctx, channel_id: Optional[int] = None):
        """Toggle bot activity in a channel"""
        try:
            target_channel_id = channel_id or ctx.channel.id
            channels = get_channels()
            
            if target_channel_id in channels:
                remove_channel(target_channel_id)
                await ctx.message.add_reaction("🔴")  # Red for deactivated
            else:
                # Get guild ID safely
                guild_id = ctx.guild.id if ctx.guild else None
                if add_channel(target_channel_id, guild_id, getattr(ctx.channel, 'name', None), ctx.author.id):
                    await ctx.message.add_reaction("🟢")  # Green for activated
                else:
                    await ctx.message.add_reaction("❌")
                    
        except Exception as e:
            logger.error(f"Error in toggle active command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="toggledm", aliases=["tdm"])
    async def toggle_dm(self, ctx):
        """Toggle DM responses"""
        try:
            self.bot.state.allow_dm = not self.bot.state.allow_dm
            await ctx.message.add_reaction("✅" if self.bot.state.allow_dm else "❌")
            
        except Exception as e:
            logger.error(f"Error in toggle DM command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="togglegc", aliases=["tgc"])
    async def toggle_gc(self, ctx):
        """Toggle group chat responses"""
        try:
            self.bot.state.allow_gc = not self.bot.state.allow_gc
            await ctx.message.add_reaction("✅" if self.bot.state.allow_gc else "❌")
            
        except Exception as e:
            logger.error(f"Error in toggle GC command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="ignore")
    async def ignore_user(self, ctx, user: Optional[discord.Member] = None):
        """Ignore or unignore a user"""
        try:
            target_user = user or ctx.message.mentions[0] if ctx.message.mentions else None
            
            if not target_user:
                await ctx.message.add_reaction("❓")
                return
            
            ignored_users = get_ignored_users()
            
            if target_user.id in ignored_users:
                # Unignore user
                if remove_ignored_user(target_user.id):
                    await ctx.message.add_reaction("🟢")  # Green for unignored
                else:
                    await ctx.message.add_reaction("❌")
            else:
                # Ignore user
                if add_ignored_user(target_user.id, str(target_user), "Manual ignore", ctx.author.id):
                    await ctx.message.add_reaction("🔴")  # Red for ignored
                else:
                    await ctx.message.add_reaction("❌")
                    
        except Exception as e:
            logger.error(f"Error in ignore command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="pause")
    async def pause_bot(self, ctx):
        """Pause or unpause bot responses"""
        try:
            self.bot.state.paused = not self.bot.state.paused
            await ctx.message.add_reaction("⏸️" if self.bot.state.paused else "▶️")
            
        except Exception as e:
            logger.error(f"Error in pause command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="wipe", aliases=["clear"])
    async def wipe_history(self, ctx, user: Optional[discord.Member] = None):
        """Clear conversation history"""
        try:
            if user:
                # Clear specific user's history
                if user.id in self.bot.state.message_history:
                    del self.bot.state.message_history[user.id]
                    await ctx.message.add_reaction("✅")
                else:
                    await ctx.message.add_reaction("❓")
            else:
                # Clear all history
                self.bot.state.message_history.clear()
                await ctx.message.add_reaction("🗑️")
                
        except Exception as e:
            logger.error(f"Error in wipe command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="models")
    async def list_models(self, ctx):
        """List available AI models"""
        try:
            models = await get_available_models()
            
            model_text = "**Available Models:**\n\n"
            
            if models.get("groq"):
                model_text += "**Groq:**\n" + "\n".join(f"• {model}" for model in models["groq"]) + "\n\n"
            
            if models.get("openai"):
                model_text += "**OpenAI:**\n" + "\n".join(f"• {model}" for model in models["openai"]) + "\n\n"
            
            if len(model_text) > 2000:
                model_text = model_text[:1980] + "\n... (truncated)"
            
            await ctx.send(model_text)
            
        except Exception as e:
            logger.error(f"Error in models command: {e}")
            await ctx.message.add_reaction("❌")

    @commands.command(name="sentiment")
    async def analyze_sentiment_command(self, ctx, *, text: str = None):
        """Analyze sentiment of provided text"""
        try:
            if not text:
                await ctx.message.add_reaction("❓")
                return
            
            sentiment = await analyze_sentiment(text)
            
            if sentiment:
                sentiment_text = f"**Sentiment Analysis:**\n"
                sentiment_text += f"• Overall: {sentiment.get('overall', 'Unknown')}\n"
                sentiment_text += f"• Confidence: {sentiment.get('confidence', 0):.1%}\n"
                
                await ctx.send(sentiment_text)
            else:
                await ctx.message.add_reaction("❌")
                
        except Exception as e:
            logger.error(f"Error in sentiment command: {e}")
            await ctx.message.add_reaction("❌")

    def get_uptime(self) -> str:
        """Get formatted uptime string"""
        uptime_seconds = time.time() - self.start_time
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(GeneralCommands(bot))