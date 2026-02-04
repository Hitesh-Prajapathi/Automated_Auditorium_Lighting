"""
Text cleaning and preprocessing module
"""

import re

def clean_text(text, preserve_structure=True):
    """
    Clean text while optionally preserving important structural elements
    
    Args:
        text (str): Raw text to clean
        preserve_structure (bool): Whether to preserve scene markers and structure
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    if preserve_structure:
        # Preserve important markers before cleaning
        text = _preserve_markers(text)
    
    # Remove excessive whitespace but preserve paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
    text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 newlines
    
    # Remove special characters but keep essential punctuation
    # Keep: letters, numbers, spaces, basic punctuation, parentheses, colons, dashes
    text = re.sub(r"[^\w\s.,!?':\-\(\)\[\]/\n\"']", "", text)
    
    # Clean up any remaining formatting artifacts
    text = re.sub(r"\s+([.,!?])", r"\1", text)  # Remove space before punctuation
    
    return text.strip()

def _preserve_markers(text):
    """Preserve important scene markers"""
    # This is a placeholder - you can add logic to mark important sections
    # before cleaning and restore them after
    return text

def extract_stage_directions(text):
    """
    Extract stage directions (text in parentheses) separately
    
    Args:
        text (str): Script text
        
    Returns:
        list: List of stage directions
    """
    # Match text in parentheses (at least 3 chars to avoid single letters)
    directions = re.findall(r"\(([^)]{3,}?)\)", text)
    return [d.strip() for d in directions if d.strip()]

def remove_stage_directions(text):
    """
    Remove stage directions from text
    
    Args:
        text (str): Script text with stage directions
        
    Returns:
        str: Text without stage directions
    """
    # Remove text in parentheses (at least 3 chars)
    return re.sub(r"\([^)]{3,}?\)", "", text)

def extract_character_names(text):
    """
    Extract character names from dialogue format
    
    Args:
        text (str): Script text
        
    Returns:
        list: List of unique character names
    """
    # Match character names (ALL CAPS followed by colon or newline)
    names = re.findall(r"^([A-Z][A-Z\s]{2,}):", text, re.MULTILINE)
    return list(set(name.strip() for name in names))

def normalize_whitespace(text):
    """
    Normalize all whitespace in text
    
    Args:
        text (str): Text to normalize
        
    Returns:
        str: Text with normalized whitespace
    """
    return " ".join(text.split())