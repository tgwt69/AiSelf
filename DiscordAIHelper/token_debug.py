#!/usr/bin/env python3
"""
Advanced Discord Token Debugger - 2025
Tests token with multiple approaches and provides detailed diagnostics
"""

import os
import asyncio
import aiohttp
import base64
import json
from dotenv import load_dotenv
from colorama import init, Fore, Style

init(autoreset=True)

async def test_token_api_direct():
    """Test token by calling Discord API directly"""
    load_dotenv("config/.env")
    token = os.getenv("DISCORD_TOKEN")
    
    if not token or token == "your_discord_token_here":
        print(f"{Fore.RED}No valid token found{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.CYAN}Testing token with direct API calls...{Style.RESET_ALL}")
    print(f"Token preview: {token[:15]}...{token[-10:]}")
    print(f"Token length: {len(token)} characters")
    
    # Test with Discord API directly
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://discord.com, 1.0)"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Try to get user info
            async with session.get("https://discord.com/api/v10/users/@me", headers=headers) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"{Fore.GREEN}✓ Token is valid!{Style.RESET_ALL}")
                    print(f"User: {user_data.get('username')}#{user_data.get('discriminator')}")
                    print(f"ID: {user_data.get('id')}")
                    print(f"Verified: {user_data.get('verified', 'Unknown')}")
                    return True
                elif resp.status == 401:
                    error_data = await resp.json()
                    print(f"{Fore.RED}✗ Token invalid: {error_data.get('message', 'Unauthorized')}{Style.RESET_ALL}")
                    
                    # Analyze token format
                    if token.count('.') >= 2:
                        parts = token.split('.')
                        print(f"\n{Fore.YELLOW}Token analysis:{Style.RESET_ALL}")
                        print(f"- Part 1 (User ID): {parts[0]} ({len(parts[0])} chars)")
                        try:
                            # Decode user ID from token
                            user_id_encoded = parts[0]
                            # Add padding if needed
                            missing_padding = len(user_id_encoded) % 4
                            if missing_padding:
                                user_id_encoded += '=' * (4 - missing_padding)
                            user_id = base64.b64decode(user_id_encoded).decode('utf-8')
                            print(f"- Decoded User ID: {user_id}")
                        except Exception as e:
                            print(f"- Could not decode User ID: {e}")
                    
                    return False
                else:
                    print(f"{Fore.RED}✗ Unexpected status: {resp.status}{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            print(f"{Fore.RED}✗ Connection error: {e}{Style.RESET_ALL}")
            return False

def analyze_token_format(token):
    """Analyze token format and provide feedback"""
    print(f"\n{Fore.CYAN}Token Format Analysis:{Style.RESET_ALL}")
    
    # Check basic format
    if len(token) < 50:
        print(f"{Fore.RED}✗ Token too short (needs 50+ characters){Style.RESET_ALL}")
        return False
    
    # Check for common issues
    issues = []
    if token.startswith('Bearer '):
        issues.append("Remove 'Bearer ' prefix")
    if token.startswith('"') and token.endswith('"'):
        issues.append("Remove quotes around token")
    if ' ' in token:
        issues.append("Remove spaces in token")
    if '\n' in token or '\r' in token:
        issues.append("Remove newlines in token")
    
    if issues:
        print(f"{Fore.YELLOW}Found issues:{Style.RESET_ALL}")
        for issue in issues:
            print(f"- {issue}")
        return False
    
    # Check if it looks like a valid Discord token
    if token.count('.') >= 2:
        print(f"{Fore.GREEN}✓ Token has proper structure (3 parts){Style.RESET_ALL}")
    elif len(token) >= 70:
        print(f"{Fore.GREEN}✓ Token length looks correct{Style.RESET_ALL}")
    
    return True

async def main():
    """Main testing function"""
    print(f"{Fore.CYAN}Discord Token Advanced Debugger{Style.RESET_ALL}")
    print("=" * 50)
    
    load_dotenv("config/.env")
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print(f"{Fore.RED}No token found in config/.env{Style.RESET_ALL}")
        return
    
    # Analyze format first
    format_ok = analyze_token_format(token)
    
    if format_ok:
        # Test with API
        api_ok = await test_token_api_direct()
        
        if api_ok:
            print(f"\n{Fore.GREEN}Token is working! The issue might be with discord.py-self library.{Style.RESET_ALL}")
            print(f"Try updating the library or using a different version.")
        else:
            print(f"\n{Fore.RED}Token is invalid. Try getting a fresh token.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Fix token format issues first.{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())