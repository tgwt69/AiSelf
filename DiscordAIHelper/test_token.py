#!/usr/bin/env python3
"""
Discord Token Tester - 2025 Edition
Quick utility to test Discord token validity
"""

import os
import asyncio
import discord
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)

async def test_discord_token():
    """Test Discord token connection"""
    load_dotenv("config/.env")
    token = os.getenv("DISCORD_TOKEN")
    
    if not token or token == "your_discord_token_here":
        print(f"{Fore.RED}No valid token found in config/.env{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Testing Discord Token...{Style.RESET_ALL}")
    print(f"Token preview: {token[:15]}...{token[-5:]}")
    print(f"Token length: {len(token)} characters")
    
    # Create a minimal client for testing
    intents = discord.Intents.default()
    intents.message_content = True
    
    class TestClient(discord.Client):
        async def on_ready(self):
            print(f"{Fore.GREEN}✓ Successfully connected to Discord!{Style.RESET_ALL}")
            print(f"Logged in as: {self.user.name} (ID: {self.user.id})")
            print(f"Account created: {self.user.created_at}")
            await self.close()
        
        async def on_error(self, event, *args, **kwargs):
            print(f"{Fore.RED}✗ Connection error: {event}{Style.RESET_ALL}")
            await self.close()
    
    client = TestClient(intents=intents)
    
    try:
        await client.start(token)
    except discord.LoginFailure as e:
        print(f"{Fore.RED}✗ Login failed: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Possible solutions:{Style.RESET_ALL}")
        print("1. Get a fresh token from Discord")
        print("2. Make sure you copied the entire token")
        print("3. Check if your Discord account has 2FA enabled")
        print("4. Try logging out and back into Discord")
    except Exception as e:
        print(f"{Fore.RED}✗ Unexpected error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(test_discord_token())