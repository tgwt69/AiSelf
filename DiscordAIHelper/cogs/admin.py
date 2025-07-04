"""
Admin commands cog for Discord AI Selfbot
Owner-only commands for bot management and maintenance
"""

import asyncio
import os
import sys
import subprocess
import logging
import gc
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import discord
from discord.ext import commands

from utils.db import cleanup_old_data, get_database_stats, get_recent_errors
from utils.error_notifications import test_webhook, log_security_event
from utils.helpers import load_config, save_config, get_system_info
from utils.ai import get_ai_status

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Admin-only commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.maintenance_mode = False
    
    async def cog_check(self, ctx):
        """Check if user is the bot owner"""
        return ctx.author.id == self.bot.state.owner_id
    
    @commands.command(name="reload")
    async def reload_cogs(self, ctx, cog_name: Optional[str] = None):
        """Reload bot cogs"""
        try:
            if cog_name:
                # Reload specific cog
                try:
                    await self.bot.reload_extension(f"cogs.{cog_name}")
                    await ctx.send(f"✅ Reloaded cog: `{cog_name}`")
                except commands.ExtensionNotLoaded:
                    await ctx.send(f"❌ Cog `{cog_name}` is not loaded")
                except commands.ExtensionNotFound:
                    await ctx.send(f"❌ Cog `{cog_name}` not found")
                except Exception as e:
                    await ctx.send(f"❌ Error reloading `{cog_name}`: {e}")
            else:
                # Reload all cogs
                reloaded = []
                failed = []
                
                # Get list of loaded extensions
                extensions = list(self.bot.extensions.keys())
                
                for extension in extensions:
                    try:
                        await self.bot.reload_extension(extension)
                        reloaded.append(extension.split('.')[-1])
                    except Exception as e:
                        failed.append(f"{extension}: {str(e)[:50]}")
                        logger.error(f"Failed to reload {extension}: {e}")
                
                embed = discord.Embed(
                    title="🔄 Cog Reload Results",
                    color=0x00ff00 if not failed else 0xffff00,
                    timestamp=datetime.utcnow()
                )
                
                if reloaded:
                    embed.add_field(
                        name="✅ Successfully Reloaded",
                        value="```\n" + "\n".join(reloaded) + "```",
                        inline=False
                    )
                
                if failed:
                    embed.add_field(
                        name="❌ Failed to Reload", 
                        value="```\n" + "\n".join(failed) + "```",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in reload command: {e}")
            await ctx.send(f"❌ Critical error during reload: {e}")
    
    @commands.command(name="restart")
    async def restart_bot(self, ctx):
        """Restart the bot"""
        try:
            embed = discord.Embed(
                title="🔄 Restarting Bot",
                description="Bot is restarting... This may take a moment.",
                color=0xffff00,
                timestamp=datetime.utcnow()
            )
            
            await ctx.send(embed=embed)
            
            # Log security event
            await log_security_event(
                "BotRestart",
                f"Bot restart initiated by owner {ctx.author.id}",
                ctx.author.id,
                ctx.channel.id,
                "Medium"
            )
            
            # Close database connections gracefully
            try:
                # Allow time for pending operations
                await asyncio.sleep(2)
                
                # Close bot connection
                await self.bot.close()
                
                # Restart the process
                python = sys.executable
                os.execl(python, python, *sys.argv)
                
            except Exception as e:
                logger.error(f"Error during restart: {e}")
                await ctx.send(f"❌ Restart failed: {e}")
                
        except Exception as e:
            logger.error(f"Error in restart command: {e}")
            await ctx.send(f"❌ Error initiating restart: {e}")
    
    @commands.command(name="shutdown")
    async def shutdown_bot(self, ctx):
        """Shutdown the bot"""
        try:
            embed = discord.Embed(
                title="🛑 Shutting Down",
                description="Bot is shutting down gracefully...",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            
            await ctx.send(embed=embed)
            
            # Log security event
            await log_security_event(
                "BotShutdown",
                f"Bot shutdown initiated by owner {ctx.author.id}",
                ctx.author.id,
                ctx.channel.id,
                "High"
            )
            
            # Graceful shutdown
            await asyncio.sleep(2)
            await self.bot.close()
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error in shutdown command: {e}")
            await ctx.send(f"❌ Error during shutdown: {e}")
    
    @commands.command(name="cleanup")
    async def cleanup_database(self, ctx, days: Optional[int] = 30):
        """Clean up old database records"""
        try:
            if days < 1 or days > 365:
                await ctx.send("❌ Days must be between 1 and 365")
                return
            
            embed = discord.Embed(
                title="🧹 Database Cleanup",
                description=f"Cleaning up records older than {days} days...",
                color=0xffff00,
                timestamp=datetime.utcnow()
            )
            
            message = await ctx.send(embed=embed)
            
            # Get stats before cleanup
            stats_before = get_database_stats()
            
            # Perform cleanup
            success = cleanup_old_data(days)
            
            if success:
                # Get stats after cleanup
                stats_after = get_database_stats()
                
                # Calculate cleaned records
                conv_cleaned = stats_before.get('conversation_records', 0) - stats_after.get('conversation_records', 0)
                error_cleaned = stats_before.get('error_logs', 0) - stats_after.get('error_logs', 0)
                
                embed.title = "✅ Database Cleanup Complete"
                embed.description = f"Successfully cleaned up old records"
                embed.color = 0x00ff00
                
                embed.add_field(
                    name="📊 Records Cleaned",
                    value=f"**Conversations:** {conv_cleaned:,}\n"
                          f"**Error Logs:** {error_cleaned:,}\n"
                          f"**Total:** {conv_cleaned + error_cleaned:,}",
                    inline=True
                )
                
                embed.add_field(
                    name="💾 Database Size",
                    value=f"**Before:** {self.format_bytes(stats_before.get('database_size', 0))}\n"
                          f"**After:** {self.format_bytes(stats_after.get('database_size', 0))}\n"
                          f"**Saved:** {self.format_bytes(stats_before.get('database_size', 0) - stats_after.get('database_size', 0))}",
                    inline=True
                )
                
                # Run garbage collection
                gc.collect()
                
            else:
                embed.title = "❌ Database Cleanup Failed"
                embed.description = "An error occurred during cleanup"
                embed.color = 0xff0000
            
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in cleanup command: {e}")
            await ctx.send(f"❌ Error during cleanup: {e}")
    
    @commands.command(name="logs")
    async def view_logs(self, ctx, log_type: Optional[str] = "error", limit: Optional[int] = 10):
        """View recent logs"""
        try:
            if limit > 50:
                limit = 50
            
            if log_type.lower() == "error":
                # Get recent errors
                errors = get_recent_errors(limit)
                
                if not errors:
                    await ctx.send("✅ No recent errors found")
                    return
                
                embed = discord.Embed(
                    title=f"⚠️ Recent Errors (Last {len(errors)})",
                    color=0xff0000,
                    timestamp=datetime.utcnow()
                )
                
                for i, error in enumerate(errors[:5]):  # Show top 5 in detail
                    timestamp = datetime.fromisoformat(error['timestamp']).strftime('%m/%d %H:%M')
                    embed.add_field(
                        name=f"{i+1}. {error['error_type']} - {timestamp}",
                        value=f"```{error['error_message'][:200]}{'...' if len(error['error_message']) > 200 else ''}```",
                        inline=False
                    )
                
                if len(errors) > 5:
                    embed.add_field(
                        name="📋 Additional Errors",
                        value=f"... and {len(errors) - 5} more errors. Use log files for complete details.",
                        inline=False
                    )
                
            else:
                await ctx.send("❌ Invalid log type. Use 'error'")
                return
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in logs command: {e}")
            await ctx.send(f"❌ Error retrieving logs: {e}")
    
    @commands.command(name="maintenance")
    async def toggle_maintenance(self, ctx):
        """Toggle maintenance mode"""
        try:
            self.maintenance_mode = not self.maintenance_mode
            
            if self.maintenance_mode:
                # Enable maintenance mode
                self.bot.state.paused = True
                
                embed = discord.Embed(
                    title="🚧 Maintenance Mode Enabled",
                    description="Bot is now in maintenance mode. All responses are paused.",
                    color=0xffff00,
                    timestamp=datetime.utcnow()
                )
                
                await log_security_event(
                    "MaintenanceMode",
                    f"Maintenance mode enabled by owner {ctx.author.id}",
                    ctx.author.id,
                    ctx.channel.id,
                    "Medium"
                )
                
            else:
                # Disable maintenance mode
                self.bot.state.paused = False
                
                embed = discord.Embed(
                    title="✅ Maintenance Mode Disabled",
                    description="Bot is now operational. Responses resumed.",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                
                await log_security_event(
                    "MaintenanceMode",
                    f"Maintenance mode disabled by owner {ctx.author.id}",
                    ctx.author.id,
                    ctx.channel.id,
                    "Medium"
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in maintenance command: {e}")
            await ctx.send(f"❌ Error toggling maintenance mode: {e}")
    
    @commands.command(name="config")
    async def manage_config(self, ctx, action: Optional[str] = "view", setting: Optional[str] = None, *, value: Optional[str] = None):
        """Manage bot configuration"""
        try:
            config = load_config()
            
            if action.lower() == "view":
                # Display current configuration
                embed = discord.Embed(
                    title="⚙️ Bot Configuration",
                    color=0x0099ff,
                    timestamp=datetime.utcnow()
                )
                
                # Bot settings
                bot_config = config.get("bot", {})
                embed.add_field(
                    name="🤖 Bot Settings",
                    value=f"**Trigger:** {bot_config.get('trigger', 'Not set')}\n"
                          f"**Prefix:** {bot_config.get('prefix', '~')}\n"
                          f"**Groq Model:** {bot_config.get('groq_model', 'N/A')}\n"
                          f"**OpenAI Model:** {bot_config.get('openai_model', 'N/A')}",
                    inline=True
                )
                
                # Behavior settings
                embed.add_field(
                    name="⚡ Behavior",
                    value=f"**Allow DM:** {bot_config.get('allow_dm', True)}\n"
                          f"**Allow GC:** {bot_config.get('allow_gc', True)}\n"
                          f"**Realistic Typing:** {bot_config.get('realistic_typing', True)}\n"
                          f"**Hold Conversations:** {bot_config.get('hold_conversation', True)}",
                    inline=True
                )
                
                # Security settings
                security_config = config.get("security", {})
                embed.add_field(
                    name="🔒 Security",
                    value=f"**Anti-age Ban:** {bot_config.get('anti_age_ban', True)}\n"
                          f"**Disable Mentions:** {bot_config.get('disable_mentions', True)}\n"
                          f"**Random Delays:** {security_config.get('random_delays', True)}\n"
                          f"**Error Tracking:** {security_config.get('error_tracking', True)}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            elif action.lower() == "set":
                if not setting or not value:
                    await ctx.send("❌ Usage: `~config set <setting> <value>`")
                    return
                
                # Update configuration setting
                # This is a simplified example - you'd want more robust validation
                setting_path = setting.split('.')
                current = config
                
                # Navigate to the setting
                for part in setting_path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value (with type conversion)
                key = setting_path[-1]
                if value.lower() in ['true', 'false']:
                    current[key] = value.lower() == 'true'
                elif value.isdigit():
                    current[key] = int(value)
                else:
                    try:
                        current[key] = float(value)
                    except ValueError:
                        current[key] = value
                
                # Save configuration
                if save_config(config):
                    await ctx.send(f"✅ Updated `{setting}` to `{value}`")
                    
                    # Log the configuration change
                    await log_security_event(
                        "ConfigChange",
                        f"Configuration '{setting}' changed to '{value}' by owner {ctx.author.id}",
                        ctx.author.id,
                        ctx.channel.id,
                        "Medium"
                    )
                else:
                    await ctx.send("❌ Failed to save configuration")
                    
            else:
                await ctx.send("❌ Invalid action. Use 'view' or 'set'")
                
        except Exception as e:
            logger.error(f"Error in config command: {e}")
            await ctx.send(f"❌ Error managing configuration: {e}")
    
    @commands.command(name="system")
    async def system_info(self, ctx):
        """Display detailed system information"""
        try:
            sys_info = get_system_info()
            
            embed = discord.Embed(
                title="💻 System Information",
                color=0x0099ff,
                timestamp=datetime.utcnow()
            )
            
            # System details
            embed.add_field(
                name="🖥️ System",
                value=f"**OS:** {sys_info['system']} {sys_info['release']}\n"
                      f"**Platform:** {sys_info['platform']}\n"
                      f"**Architecture:** {sys_info['architecture']}\n"
                      f"**Processor:** {sys_info['processor'][:30]}...",
                inline=True
            )
            
            # Python details
            embed.add_field(
                name="🐍 Python",
                value=f"**Version:** {sys_info['python_version'].split()[0]}\n"
                      f"**Executable:** {sys.executable.split('/')[-1]}\n"
                      f"**PID:** {os.getpid()}\n"
                      f"**Working Dir:** {os.getcwd().split('/')[-1]}",
                inline=True
            )
            
            # Resource usage
            import psutil
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            embed.add_field(
                name="📊 Resources",
                value=f"**CPU Usage:** {psutil.cpu_percent()}%\n"
                      f"**Memory:** {memory.percent}% ({self.format_bytes(memory.used)})\n"
                      f"**Disk Usage:** {disk.percent}%\n"
                      f"**Available:** {self.format_bytes(memory.available)}",
                inline=True
            )
            
            # Bot-specific info
            ai_status = get_ai_status()
            embed.add_field(
                name="🤖 Bot Status",
                value=f"**Discord.py:** {discord.__version__}\n"
                      f"**Groq Available:** {'✅' if ai_status.get('groq_available') else '❌'}\n"
                      f"**OpenAI Available:** {'✅' if ai_status.get('openai_available') else '❌'}\n"
                      f"**Maintenance:** {'🚧 Yes' if self.maintenance_mode else '✅ No'}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in system command: {e}")
            await ctx.send(f"❌ Error getting system information: {e}")
    
    @commands.command(name="testwh")
    async def test_webhook(self, ctx):
        """Test error webhook notification"""
        try:
            success = await test_webhook()
            
            if success:
                await ctx.send("✅ Webhook test successful! Check your webhook channel.")
            else:
                await ctx.send("❌ Webhook test failed. Check webhook URL and try again.")
                
        except Exception as e:
            logger.error(f"Error in testwh command: {e}")
            await ctx.send(f"❌ Error testing webhook: {e}")
    
    @commands.command(name="prompt")
    async def manage_prompt(self, ctx, action: Optional[str] = "view", *, content: Optional[str] = None):
        """Manage AI prompt/instructions"""
        try:
            from utils.helpers import resource_path, load_instructions
            
            instructions_path = resource_path("config/instructions.txt")
            
            if action.lower() == "view":
                # Show current instructions
                instructions = load_instructions()
                
                embed = discord.Embed(
                    title="📝 Current AI Instructions",
                    description=f"```{instructions[:1500]}{'...' if len(instructions) > 1500 else ''}```",
                    color=0x0099ff,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="📊 Stats",
                    value=f"**Length:** {len(instructions)} characters\n"
                          f"**Words:** {len(instructions.split())} words",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            elif action.lower() == "set":
                if not content:
                    await ctx.send("❌ Please provide new instructions")
                    return
                
                if len(content) > 5000:
                    await ctx.send("❌ Instructions too long (max 5000 characters)")
                    return
                
                # Save new instructions
                try:
                    with open(instructions_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    await ctx.send("✅ AI instructions updated successfully")
                    
                    # Log the change
                    await log_security_event(
                        "InstructionsChanged",
                        f"AI instructions updated by owner {ctx.author.id} (length: {len(content)})",
                        ctx.author.id,
                        ctx.channel.id,
                        "Medium"
                    )
                    
                except Exception as e:
                    await ctx.send(f"❌ Error saving instructions: {e}")
                    
            elif action.lower() == "clear":
                # Reset to default instructions
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
                
                try:
                    with open(instructions_path, 'w', encoding='utf-8') as f:
                        f.write(default_instructions)
                    
                    await ctx.send("✅ AI instructions reset to default")
                    
                    # Log the reset
                    await log_security_event(
                        "InstructionsReset",
                        f"AI instructions reset to default by owner {ctx.author.id}",
                        ctx.author.id,
                        ctx.channel.id,
                        "Medium"
                    )
                    
                except Exception as e:
                    await ctx.send(f"❌ Error resetting instructions: {e}")
                    
            else:
                await ctx.send("❌ Invalid action. Use 'view', 'set', or 'clear'")
                
        except Exception as e:
            logger.error(f"Error in prompt command: {e}")
            await ctx.send(f"❌ Error managing prompt: {e}")
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AdminCommands(bot))

