"""
Cogs package for Discord AI Selfbot
Enhanced command modules for 2025
"""

__version__ = "3.0.0"
__author__ = "Najmul190"

# Import all cog classes for easy access
from .commands import GeneralCommands
from .admin import AdminCommands

__all__ = ["GeneralCommands", "AdminCommands"]

