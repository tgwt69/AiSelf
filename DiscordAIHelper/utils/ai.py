"""
AI integration utilities for Discord AI Selfbot
Enhanced with 2025 Groq API and OpenAI support, improved error handling
"""

import os
import asyncio
import json
import logging
import time
import random
from typing import List, Optional, Dict, Any
import httpx
from groq import Groq
from openai import OpenAI

from .helpers import load_config, load_instructions
from .db import log_conversation, log_error

logger = logging.getLogger(__name__)

# Global AI clients
groq_client = None
openai_client = None
config = None

# Rate limiting and retry settings
RATE_LIMIT_DELAY = 1.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30.0

class AIError(Exception):
    """Custom exception for AI-related errors"""
    pass

class RateLimitError(AIError):
    """Exception for rate limit errors"""
    pass

def init_ai():
    """Initialize AI clients with API keys"""
    global groq_client, openai_client, config
    
    config = load_config()
    
    # Initialize Groq client
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            groq_client = Groq(api_key=groq_api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
    
    # Initialize OpenAI client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            openai_client = OpenAI(api_key=openai_api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    if not groq_client and not openai_client:
        logger.warning("No AI clients initialized. Please check your API keys.")

async def generate_response_groq(prompt: str, instructions: str, history: List[str] = None) -> Optional[str]:
    """Generate response using Groq API with enhanced error handling"""
    if not groq_client:
        raise AIError("Groq client not initialized")
    
    try:
        # Prepare messages
        messages = [
            {"role": "system", "content": instructions}
        ]
        
        # Add conversation history
        if history:
            for i, msg in enumerate(history[-10:]):  # Limit history to last 10 messages
                role = "assistant" if i % 2 == 1 else "user"
                messages.append({"role": role, "content": msg})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Get AI settings from config
        ai_settings = config.get("ai", {}).get("groq_settings", {})
        model = config.get("bot", {}).get("groq_model", "llama-3.3-70b-versatile")
        
        # Make API request with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = await asyncio.to_thread(
                    groq_client.chat.completions.create,
                    model=model,
                    messages=messages,
                    max_tokens=ai_settings.get("max_tokens", 1024),
                    temperature=config.get("ai", {}).get("temperature", 0.7),
                    top_p=ai_settings.get("top_p", 0.9),
                    frequency_penalty=ai_settings.get("frequency_penalty", 0.0),
                    presence_penalty=ai_settings.get("presence_penalty", 0.0)
                )
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content.strip()
                    
                    # Log token usage
                    usage = getattr(response, 'usage', None)
                    tokens_used = usage.total_tokens if usage else 0
                    logger.info(f"Groq response generated using {tokens_used} tokens")
                    
                    return content
                else:
                    logger.warning("Empty response from Groq API")
                    return None
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg or "quota" in error_msg:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit, waiting {wait_time:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    
                    if attempt == MAX_RETRIES - 1:
                        raise RateLimitError("Rate limit exceeded after all retries")
                    continue
                
                elif attempt == MAX_RETRIES - 1:
                    logger.error(f"Groq API error after {MAX_RETRIES} attempts: {e}")
                    raise AIError(f"Groq API error: {e}")
                else:
                    logger.warning(f"Groq API error (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(1.0)
        
        return None
        
    except Exception as e:
        logger.error(f"Error in generate_response_groq: {e}")
        log_error("groq_api_error", str(e))
        raise

async def generate_response_openai(prompt: str, instructions: str, history: List[str] = None) -> Optional[str]:
    """Generate response using OpenAI API with enhanced error handling"""
    if not openai_client:
        raise AIError("OpenAI client not initialized")
    
    try:
        # Prepare messages
        messages = [
            {"role": "system", "content": instructions}
        ]
        
        # Add conversation history
        if history:
            for i, msg in enumerate(history[-10:]):  # Limit history to last 10 messages
                role = "assistant" if i % 2 == 1 else "user"
                messages.append({"role": role, "content": msg})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Get AI settings from config
        ai_settings = config.get("ai", {}).get("openai_settings", {})
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        model = config.get("bot", {}).get("openai_model", "gpt-4o")
        
        # Make API request with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = await asyncio.to_thread(
                    openai_client.chat.completions.create,
                    model=model,
                    messages=messages,
                    max_tokens=ai_settings.get("max_tokens", 1024),
                    temperature=config.get("ai", {}).get("temperature", 0.7),
                    top_p=ai_settings.get("top_p", 0.9),
                    frequency_penalty=ai_settings.get("frequency_penalty", 0.0),
                    presence_penalty=ai_settings.get("presence_penalty", 0.0)
                )
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content.strip()
                    
                    # Log token usage
                    usage = getattr(response, 'usage', None)
                    tokens_used = usage.total_tokens if usage else 0
                    logger.info(f"OpenAI response generated using {tokens_used} tokens")
                    
                    return content
                else:
                    logger.warning("Empty response from OpenAI API")
                    return None
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg or "quota" in error_msg:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit, waiting {wait_time:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    
                    if attempt == MAX_RETRIES - 1:
                        raise RateLimitError("Rate limit exceeded after all retries")
                    continue
                
                elif attempt == MAX_RETRIES - 1:
                    logger.error(f"OpenAI API error after {MAX_RETRIES} attempts: {e}")
                    raise AIError(f"OpenAI API error: {e}")
                else:
                    logger.warning(f"OpenAI API error (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(1.0)
        
        return None
        
    except Exception as e:
        logger.error(f"Error in generate_response_openai: {e}")
        log_error("openai_api_error", str(e))
        raise

async def generate_response(prompt: str, instructions: str, history: List[str] = None) -> Optional[str]:
    """Generate AI response using available providers with fallback"""
    start_time = time.time()
    
    try:
        # Validate input
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return None
        
        if len(prompt) > 4000:  # Reasonable limit
            logger.warning("Prompt too long, truncating")
            prompt = prompt[:4000]
        
        # Try Groq first (recommended for speed and cost)
        if groq_client:
            try:
                response = await generate_response_groq(prompt, instructions, history)
                if response:
                    response_time = time.time() - start_time
                    logger.info(f"Groq response generated in {response_time:.2f}s")
                    return response
            except RateLimitError:
                logger.warning("Groq rate limit hit, trying OpenAI fallback")
            except AIError as e:
                logger.warning(f"Groq error, trying OpenAI fallback: {e}")
        
        # Fallback to OpenAI
        if openai_client:
            try:
                response = await generate_response_openai(prompt, instructions, history)
                if response:
                    response_time = time.time() - start_time
                    logger.info(f"OpenAI response generated in {response_time:.2f}s")
                    return response
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
        
        logger.error("All AI providers failed or unavailable")
        return "I'm having trouble connecting to AI services right now. Please try again later."
        
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        log_error("ai_generation_error", str(e))
        return "Sorry, I encountered an error while processing your request."

async def generate_response_image(prompt: str, instructions: str, image_url: str, history: List[str] = None) -> Optional[str]:
    """Generate AI response for image with text using vision models"""
    start_time = time.time()
    
    try:
        # For now, prioritize OpenAI for image analysis as it has better vision capabilities
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        if openai_client:
            try:
                # Prepare messages for vision model
                messages = [
                    {"role": "system", "content": instructions}
                ]
                
                # Add conversation history (text only)
                if history:
                    for i, msg in enumerate(history[-5:]):  # Reduced for image context
                        role = "assistant" if i % 2 == 1 else "user"
                        messages.append({"role": role, "content": msg})
                
                # Add current prompt with image
                user_content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
                messages.append({"role": "user", "content": user_content})
                
                ai_settings = config.get("ai", {}).get("openai_settings", {})
                
                response = await asyncio.to_thread(
                    openai_client.chat.completions.create,
                    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                    # do not change this unless explicitly requested by the user
                    model="gpt-4o",  # Use vision-capable model
                    messages=messages,
                    max_tokens=ai_settings.get("max_tokens", 1024),
                    temperature=config.get("ai", {}).get("temperature", 0.7)
                )
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content.strip()
                    response_time = time.time() - start_time
                    
                    tokens_used = getattr(response, 'usage', {}).get('total_tokens', 0)
                    logger.info(f"OpenAI vision response generated in {response_time:.2f}s using {tokens_used} tokens")
                    
                    return content
                
            except Exception as e:
                logger.error(f"OpenAI vision error: {e}")
        
        # Fallback: Try to use Groq with text-only prompt
        if groq_client:
            try:
                fallback_prompt = f"{prompt}\n\n[Note: An image was shared but I cannot analyze it. Please describe the image if you'd like me to comment on it.]"
                response = await generate_response_groq(fallback_prompt, instructions, history)
                if response:
                    response_time = time.time() - start_time
                    logger.info(f"Groq fallback response generated in {response_time:.2f}s")
                    return response
            except Exception as e:
                logger.error(f"Groq fallback error: {e}")
        
        return "I can see you shared an image, but I'm having trouble analyzing it right now. Could you describe what's in the image?"
        
    except Exception as e:
        logger.error(f"Error in generate_response_image: {e}")
        log_error("ai_image_error", str(e))
        return "Sorry, I encountered an error while analyzing the image."

async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment of text using AI"""
    try:
        if not text or not text.strip():
            return {"sentiment": "neutral", "confidence": 0.0}
        
        # Use available AI provider for sentiment analysis
        prompt = f"""Analyze the sentiment of this text and respond with JSON:
Text: "{text}"

Respond with JSON in this format:
{{"sentiment": "positive/negative/neutral", "confidence": 0.95, "explanation": "brief explanation"}}"""
        
        if groq_client:
            try:
                response = await asyncio.to_thread(
                    groq_client.chat.completions.create,
                    model=config.get("bot", {}).get("groq_model", "llama-3.3-70b-versatile"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.3
                )
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content.strip()
                    try:
                        result = json.loads(content)
                        return result
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse sentiment JSON from Groq")
            except Exception as e:
                logger.error(f"Groq sentiment analysis error: {e}")
        
        # Fallback to simple keyword-based analysis
        positive_words = ["good", "great", "awesome", "love", "like", "happy", "excellent", "amazing"]
        negative_words = ["bad", "hate", "terrible", "awful", "sad", "angry", "horrible", "disgusting"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"sentiment": "positive", "confidence": 0.6, "explanation": "Keyword-based analysis"}
        elif negative_count > positive_count:
            return {"sentiment": "negative", "confidence": 0.6, "explanation": "Keyword-based analysis"}
        else:
            return {"sentiment": "neutral", "confidence": 0.5, "explanation": "Keyword-based analysis"}
            
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}")
        return {"sentiment": "neutral", "confidence": 0.0, "explanation": "Analysis failed"}

async def get_available_models() -> Dict[str, List[str]]:
    """Get list of available AI models"""
    models = {"groq": [], "openai": []}
    
    # Get Groq models
    if groq_client:
        try:
            groq_models = await asyncio.to_thread(groq_client.models.list)
            models["groq"] = [model.id for model in groq_models.data]
        except Exception as e:
            logger.error(f"Error getting Groq models: {e}")
    
    # Get OpenAI models
    if openai_client:
        try:
            openai_models = await asyncio.to_thread(openai_client.models.list)
            models["openai"] = [model.id for model in openai_models.data if "gpt" in model.id.lower()]
        except Exception as e:
            logger.error(f"Error getting OpenAI models: {e}")
    
    return models

def get_ai_status() -> Dict[str, Any]:
    """Get status of AI services"""
    return {
        "groq_available": groq_client is not None,
        "openai_available": openai_client is not None,
        "groq_model": config.get("bot", {}).get("groq_model", "llama-3.3-70b-versatile"),
        "openai_model": config.get("bot", {}).get("openai_model", "gpt-4o"),
        "config_loaded": config is not None
    }

async def generate_auto_conversation_starter(channel_context: str = None, recent_messages: List[str] = None) -> Optional[str]:
    """Generate a natural conversation starter for auto-initiated messages"""
    try:
        config = load_config()
        instructions = load_instructions()
        
        # Create context for auto conversation
        auto_prompt = f"""Generate a natural, casual conversation starter that feels like a real person randomly starting a chat. 

Channel context: {channel_context or 'general chat'}
Recent messages: {recent_messages[-3:] if recent_messages else 'No recent messages'}

Guidelines:
- Keep it super casual and chill, like texting a friend
- Don't reference being AI or a bot
- Use minimal emojis, act like a regular person
- Make it feel spontaneous, not forced
- Topics can be: random thoughts, observations, questions, current events, gaming, memes, etc.
- Keep it short (1-2 sentences max)
- Should feel like someone just thought of something random to share

Examples of good starters:
"yo anyone else think pineapple on pizza is actually fire?"
"just saw the weirdest thing outside lol"
"bro why do they call it rush hour when nobody's moving"
"anyone playing anything good lately?"
"random thought but why do we say 'after dark' when it's just nighttime"

Generate ONE casual conversation starter:"""

        # Use the primary AI provider to generate starter
        response = await generate_response_groq(auto_prompt, instructions, [])
        
        if not response:
            response = await generate_response_openai(auto_prompt, instructions, [])
        
        if response:
            # Clean up the response to ensure it's natural
            response = response.strip().strip('"').strip("'")
            
            # Ensure it's not too long
            if len(response) > 150:
                response = response[:147] + "..."
            
            return response
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to generate auto conversation starter: {e}")
        return None
