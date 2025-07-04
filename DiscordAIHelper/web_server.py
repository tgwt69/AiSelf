"""
Simple web server for Discord AI Selfbot
Provides health check endpoint for Replit workflow detection
"""

import asyncio
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

class HealthServer:
    """Simple health check server"""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "Discord AI Selfbot",
            "version": "3.0.0"
        })
    
    async def start_server(self):
        """Start the health check server"""
        try:
            self.app = web.Application()
            self.app.router.add_get('/', self.health_check)
            self.app.router.add_get('/health', self.health_check)
            
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            
            logger.info(f"Health server started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start health server: {e}")
    
    async def stop_server(self):
        """Stop the health check server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("Health server stopped")
        except Exception as e:
            logger.error(f"Error stopping health server: {e}")

# Global health server instance
_health_server = None

async def start_health_server(port=5000):
    """Start the health check server"""
    global _health_server
    _health_server = HealthServer(port)
    await _health_server.start_server()

async def stop_health_server():
    """Stop the health check server"""
    global _health_server
    if _health_server:
        await _health_server.stop_server()
        _health_server = None