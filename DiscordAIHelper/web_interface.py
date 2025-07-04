"""
Web interface for Discord AI Selfbot - 2025 Edition
Simple web dashboard to control the bot with real-time logs
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import yaml
from utils.helpers import validate_discord_token, load_config, save_config
from utils.db import get_database_stats, get_recent_errors
from utils.ai import get_ai_status, get_available_models
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store bot instance reference
bot_instance = None
bot_thread = None
bot_logs = []
is_bot_running = False

class LogCapture(logging.Handler):
    """Custom log handler to capture bot logs for web interface"""
    def emit(self, record):
        global bot_logs
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        }
        bot_logs.append(log_entry)
        # Keep only last 100 logs
        if len(bot_logs) > 100:
            bot_logs.pop(0)
        
        # Emit to connected clients
        socketio.emit('new_log', log_entry)

# Add log capture handler
log_capture = LogCapture()
log_capture.setLevel(logging.INFO)
logging.getLogger().addHandler(log_capture)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get bot status and system information"""
    try:
        # Enhanced System information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        net_io = psutil.net_io_counters()
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        # Load averages (Unix-like systems)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]
        
        # Bot status
        bot_status = {
            'running': is_bot_running,
            'uptime': time.time() - start_time if is_bot_running else 0
        }
        
        # AI status
        try:
            ai_status = get_ai_status()
            if ai_status is None:
                ai_status = {'status': 'unknown', 'providers': []}
        except Exception as e:
            ai_status = {'status': 'error', 'error': str(e), 'providers': []}
        
        # Database stats
        try:
            db_stats = get_database_stats()
            if db_stats is None:
                db_stats = {'total_conversations': 0, 'total_errors': 0}
        except Exception as e:
            db_stats = {'total_conversations': 0, 'total_errors': 0, 'error': str(e)}
        
        return jsonify({
            'success': True,
            'bot_status': bot_status,
            'ai_status': ai_status,
            'system': {
                'cpu': {
                    'percent': cpu_percent,
                    'per_core': cpu_per_core,
                    'count': cpu_count,
                    'freq': {
                        'current': cpu_freq.current if cpu_freq else 0,
                        'min': cpu_freq.min if cpu_freq else 0,
                        'max': cpu_freq.max if cpu_freq else 0
                    } if cpu_freq else None,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free,
                    'buffers': memory.buffers,
                    'cached': memory.cached
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process_cpu,
                    'pid': process.pid
                }
            },
            'database': db_stats
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update bot configuration"""
    try:
        if request.method == 'GET':
            config = load_config()
            # Remove sensitive data
            safe_config = config.copy()
            return jsonify({'success': True, 'config': safe_config})
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['discord_token', 'groq_api_key', 'owner_id']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({
                    'success': False, 
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                })
            
            # Validate Discord token
            if not validate_discord_token(data['discord_token']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid Discord token format'
                })
            
            # Save environment variables
            env_path = 'config/.env'
            env_content = f"""# Discord AI Selfbot Configuration
DISCORD_TOKEN={data['discord_token']}
GROQ_API_KEY={data['groq_api_key']}
OPENAI_API_KEY={data.get('openai_api_key', '')}
ERROR_WEBHOOK_URL={data.get('error_webhook_url', '')}
"""
            
            with open(env_path, 'w') as f:
                f.write(env_content)
            
            # Update config.yaml
            config = load_config()
            config['bot']['owner_id'] = int(data['owner_id'])
            config['bot']['prefix'] = data.get('prefix', '.')
            config['bot']['trigger'] = data.get('trigger', 'everyone')
            config['bot']['groq_model'] = data.get('groq_model', 'llama-3.3-70b-versatile')
            config['bot']['openai_model'] = data.get('openai_model', 'gpt-4o')
            
            save_config(config)
            
            return jsonify({'success': True, 'message': 'Configuration saved successfully'})
            
    except Exception as e:
        logger.error(f"Error handling config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/config/reload', methods=['POST'])
def api_config_reload():
    """Reload configuration from file"""
    try:
        # Force reload configuration from file
        config = load_config()
        
        return jsonify({
            'success': True, 
            'message': 'Configuration reloaded successfully',
            'config': config
        })
    
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bot/start', methods=['POST'])
def api_bot_start():
    """Start the Discord bot"""
    global bot_instance, bot_thread, is_bot_running, start_time
    
    try:
        if is_bot_running:
            return jsonify({'success': False, 'error': 'Bot is already running'})
        
        # Import and start bot
        def run_bot():
            global is_bot_running, start_time, bot_instance
            try:
                # Import main bot module
                import main
                is_bot_running = True
                start_time = time.time()
                
                # Store bot instance reference
                bot_instance = main.bot
                
                # Run the bot
                main.main()
                
            except Exception as e:
                logger.error(f"Bot error: {e}")
                is_bot_running = False
                bot_instance = None
            finally:
                is_bot_running = False
                bot_instance = None
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bot/stop', methods=['POST'])
def api_bot_stop():
    """Stop the Discord bot"""
    global is_bot_running
    
    try:
        if not is_bot_running:
            return jsonify({'success': False, 'error': 'Bot is not running'})
        
        # Stop the bot
        is_bot_running = False
        
        # Force exit if needed
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logs')
def api_logs():
    """Get bot logs"""
    try:
        return jsonify({
            'success': True,
            'logs': bot_logs[-50:],  # Return last 50 logs
            'total_logs': len(bot_logs)
        })
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/errors')
def api_errors():
    """Get recent errors"""
    try:
        errors = get_recent_errors(limit=20)
        return jsonify({
            'success': True,
            'errors': errors
        })
    except Exception as e:
        logger.error(f"Error getting errors: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/models')
def api_models():
    """Get available AI models"""
    try:
        models = asyncio.run(get_available_models())
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/channels')
def api_channels():
    """Get bot's available channels"""
    try:
        if not bot_instance or not hasattr(bot_instance, 'guilds'):
            return jsonify({'success': False, 'error': 'Bot not running'})
        
        channels = []
        for guild in bot_instance.guilds:
            for channel in guild.text_channels:
                channels.append({
                    'id': channel.id,
                    'name': f"#{channel.name}",
                    'guild': guild.name,
                    'guild_id': guild.id
                })
        
        return jsonify({
            'success': True,
            'channels': channels
        })
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    """Send a message through the bot"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'error': 'Bot not running'})
        
        data = request.get_json()
        channel_id = data.get('channel_id')
        message = data.get('message')
        
        if not channel_id or not message:
            return jsonify({'success': False, 'error': 'Channel ID and message required'})
        
        # Send message asynchronously
        async def send_message():
            try:
                channel = bot_instance.get_channel(int(channel_id))
                if not channel:
                    return False, "Channel not found"
                
                await channel.send(message)
                return True, "Message sent successfully"
            except Exception as e:
                return False, str(e)
        
        # Run async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, result = loop.run_until_complete(send_message())
        loop.close()
        
        return jsonify({
            'success': success,
            'message': result
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/join_server', methods=['POST'])
def api_join_server():
    """Join a Discord server via invite"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'error': 'Bot not running'})
        
        data = request.get_json()
        invite_url = data.get('invite_url')
        
        if not invite_url:
            return jsonify({'success': False, 'error': 'Invite URL required'})
        
        # Extract invite code from URL
        invite_code = invite_url.split('/')[-1].split('?')[0]
        
        # Join server asynchronously
        async def join_server():
            try:
                invite = await bot_instance.fetch_invite(invite_code)
                await invite.accept()
                return True, f"Successfully joined {invite.guild.name}"
            except Exception as e:
                return False, str(e)
        
        # Run async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, result = loop.run_until_complete(join_server())
        loop.close()
        
        return jsonify({
            'success': success,
            'message': result
        })
        
    except Exception as e:
        logger.error(f"Error joining server: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/execute_command', methods=['POST'])
def api_execute_command():
    """Execute a bot command"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'error': 'Bot not running'})
        
        data = request.get_json()
        command = data.get('command')
        channel_id = data.get('channel_id')
        
        if not command:
            return jsonify({'success': False, 'error': 'Command required'})
        
        # Execute command asynchronously
        async def execute_command():
            try:
                # Get channel or use first available channel
                if channel_id:
                    channel = bot_instance.get_channel(int(channel_id))
                else:
                    # Use first available text channel
                    channel = None
                    for guild in bot_instance.guilds:
                        for ch in guild.text_channels:
                            channel = ch
                            break
                        if channel:
                            break
                
                if not channel:
                    return False, "No available channels"
                
                # Create a fake message to trigger command processing
                class FakeMessage:
                    def __init__(self, content, channel, author):
                        self.content = content
                        self.channel = channel
                        self.author = author
                        self.guild = channel.guild
                        self.id = 0
                        self.attachments = []
                
                fake_msg = FakeMessage(command, channel, bot_instance.user)
                await bot_instance.process_commands(fake_msg)
                
                return True, "Command executed successfully"
            except Exception as e:
                return False, str(e)
        
        # Run async function
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, result = loop.run_until_complete(execute_command())
        loop.close()
        
        return jsonify({
            'success': success,
            'message': result
        })
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to WebSocket')
    # Send current logs to new client
    emit('logs_update', {'logs': bot_logs[-20:]})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from WebSocket')

start_time = time.time()

def run_web_server(host='0.0.0.0', port=5000):
    """Run the web server"""
    try:
        logger.info(f"Starting web server on {host}:{port}")
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Error running web server: {e}")

if __name__ == "__main__":
    run_web_server()