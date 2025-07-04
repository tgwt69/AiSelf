"""
Response splitting utilities for Discord AI Selfbot
Enhanced for 2025 with better message chunking and formatting
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Discord message limits
DISCORD_MAX_LENGTH = 2000
CHUNK_OVERLAP = 50  # Characters to overlap between chunks for context

def split_response(response: str, max_length: int = DISCORD_MAX_LENGTH) -> List[str]:
    """
    Split AI response into Discord-friendly chunks with enhanced logic
    
    Args:
        response: The AI response text to split
        max_length: Maximum length per chunk (default: Discord's 2000 limit)
    
    Returns:
        List of message chunks
    """
    try:
        if not response or not response.strip():
            return []
        
        response = response.strip()
        
        # If response fits in one message, return as-is
        if len(response) <= max_length:
            return [response]
        
        chunks = []
        
        # Try to split by paragraphs first (double newlines)
        paragraphs = response.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed limit
            if len(current_chunk) + len(paragraph) + 2 > max_length:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If paragraph itself is too long, split it further
                if len(paragraph) > max_length:
                    sub_chunks = split_long_paragraph(paragraph, max_length)
                    chunks.extend(sub_chunks[:-1])  # Add all but last
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If we still don't have chunks, force split
        if not chunks:
            chunks = force_split_response(response, max_length)
        
        # Clean up chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        # Log if response was split
        if len(chunks) > 1:
            logger.info(f"Response split into {len(chunks)} chunks")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error splitting response: {e}")
        # Fallback: simple character-based split
        return force_split_response(response, max_length)

def split_long_paragraph(paragraph: str, max_length: int) -> List[str]:
    """Split a long paragraph using sentence boundaries"""
    try:
        # Try to split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed limit
            if len(current_chunk) + len(sentence) + 1 > max_length:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If sentence itself is too long, split by commas or force split
                if len(sentence) > max_length:
                    if ',' in sentence:
                        sub_chunks = split_by_commas(sentence, max_length)
                        chunks.extend(sub_chunks[:-1])
                        current_chunk = sub_chunks[-1] if sub_chunks else ""
                    else:
                        # Force split long sentence
                        sub_chunks = force_split_text(sentence, max_length)
                        chunks.extend(sub_chunks[:-1])
                        current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = sentence
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [paragraph[:max_length]]
        
    except Exception as e:
        logger.error(f"Error splitting paragraph: {e}")
        return force_split_text(paragraph, max_length)

def split_by_commas(text: str, max_length: int) -> List[str]:
    """Split text by commas when sentences are too long"""
    try:
        parts = text.split(',')
        chunks = []
        current_chunk = ""
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # If adding this part would exceed limit
            if len(current_chunk) + len(part) + 1 > max_length:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If part itself is too long, force split
                if len(part) > max_length:
                    sub_chunks = force_split_text(part, max_length)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = part
            else:
                # Add part to current chunk
                if current_chunk:
                    current_chunk += ", " + part
                else:
                    current_chunk = part
        
        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:max_length]]
        
    except Exception as e:
        logger.error(f"Error splitting by commas: {e}")
        return force_split_text(text, max_length)

def force_split_text(text: str, max_length: int) -> List[str]:
    """Force split text by character count with word boundary preference"""
    try:
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        remaining = text
        
        while len(remaining) > max_length:
            # Find the best split point (prefer word boundaries)
            split_point = max_length
            
            # Look for word boundary within last 100 characters
            search_start = max(0, max_length - 100)
            word_boundary = remaining.rfind(' ', search_start, max_length)
            
            if word_boundary != -1 and word_boundary > search_start:
                split_point = word_boundary
            
            # Extract chunk
            chunk = remaining[:split_point].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next part
            remaining = remaining[split_point:].strip()
        
        # Add remaining text
        if remaining:
            chunks.append(remaining)
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error in force split: {e}")
        # Ultimate fallback
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def force_split_response(response: str, max_length: int) -> List[str]:
    """Force split response when other methods fail"""
    try:
        if len(response) <= max_length:
            return [response]
        
        chunks = []
        start = 0
        
        while start < len(response):
            end = start + max_length
            
            # If this isn't the last chunk, try to find a good split point
            if end < len(response):
                # Look for word boundary in last 50 characters
                search_start = max(start, end - 50)
                word_boundary = response.rfind(' ', search_start, end)
                
                if word_boundary != -1 and word_boundary > search_start:
                    end = word_boundary
            
            chunk = response[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end
            if start < len(response) and response[start] == ' ':
                start += 1  # Skip the space
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error in force split response: {e}")
        # Ultimate fallback
        return [response[:max_length]]

def clean_chunk(chunk: str) -> str:
    """Clean and format a message chunk"""
    try:
        # Remove excessive whitespace
        chunk = re.sub(r'\n\s*\n\s*\n', '\n\n', chunk)  # Max 2 consecutive newlines
        chunk = re.sub(r' +', ' ', chunk)  # Remove multiple spaces
        
        # Remove leading/trailing whitespace
        chunk = chunk.strip()
        
        # Ensure chunk doesn't start with punctuation (except specific cases)
        if chunk and chunk[0] in '.,;:!?' and len(chunk) > 1:
            chunk = chunk[1:].strip()
        
        return chunk
        
    except Exception as e:
        logger.error(f"Error cleaning chunk: {e}")
        return chunk

def validate_chunks(chunks: List[str], max_length: int = DISCORD_MAX_LENGTH) -> List[str]:
    """Validate and fix chunks that are still too long"""
    try:
        validated_chunks = []
        
        for chunk in chunks:
            if len(chunk) <= max_length:
                validated_chunks.append(chunk)
            else:
                # Split oversized chunk
                logger.warning(f"Chunk still too long ({len(chunk)} chars), force splitting")
                sub_chunks = force_split_text(chunk, max_length)
                validated_chunks.extend(sub_chunks)
        
        return validated_chunks
        
    except Exception as e:
        logger.error(f"Error validating chunks: {e}")
        return chunks

def smart_split_response(response: str, max_length: int = DISCORD_MAX_LENGTH, 
                        preserve_formatting: bool = True) -> List[str]:
    """
    Enhanced response splitting with smart formatting preservation
    
    Args:
        response: The response to split
        max_length: Maximum length per chunk
        preserve_formatting: Whether to preserve markdown/formatting
    
    Returns:
        List of properly formatted chunks
    """
    try:
        if not response or not response.strip():
            return []
        
        # Clean the response
        response = response.strip()
        
        # If it fits in one message, return as-is
        if len(response) <= max_length:
            return [response]
        
        # Handle code blocks specially if preserving formatting
        if preserve_formatting and '```' in response:
            return split_with_code_blocks(response, max_length)
        
        # Regular splitting
        chunks = split_response(response, max_length)
        
        # Clean and validate chunks
        chunks = [clean_chunk(chunk) for chunk in chunks]
        chunks = validate_chunks(chunks, max_length)
        
        # Remove empty chunks
        chunks = [chunk for chunk in chunks if chunk.strip()]
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error in smart split: {e}")
        return [response[:max_length]] if response else []

def split_with_code_blocks(response: str, max_length: int) -> List[str]:
    """Split response while preserving code block integrity"""
    try:
        chunks = []
        current_chunk = ""
        in_code_block = False
        
        lines = response.split('\n')
        
        for line in lines:
            # Check for code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            # Calculate new length if we add this line
            new_length = len(current_chunk) + len(line) + 1  # +1 for newline
            
            # If adding this line would exceed limit and we're not in a code block
            if new_length > max_length and not in_code_block and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                # Add line to current chunk
                if current_chunk:
                    current_chunk += '\n' + line
                else:
                    current_chunk = line
                
                # If we're still over limit even in a code block, we need to force split
                if len(current_chunk) > max_length * 1.5:  # Allow some overflow for code blocks
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    in_code_block = False  # Reset state
        
        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error splitting with code blocks: {e}")
        return split_response(response, max_length)

# Backwards compatibility
def split_message(content: str) -> List[str]:
    """Legacy function name for backwards compatibility"""
    return split_response(content)
