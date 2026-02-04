"""
Format detection module for various script formats
"""

import re
import json

def detect_format(text):
    """
    Detects script format and extracts metadata
    
    Args:
        text (str): Raw script text
        
    Returns:
        dict: Format information including type, timestamps, structure
    """
    # Timestamp patterns
    timestamp_patterns = [
        r"\[\d+:\d+(?::\d+)?\]",  # [00:30] or [00:30:15]
        r"\d+:\d+(?::\d+)?",       # 00:30 or 00:30:15
        r"\d+\.\d+s",              # 10.5s
        r"\d{2}:\d{2}:\d{2}",      # 00:00:30 (timecode)
    ]
    
    has_timestamp = any(re.search(pattern, text) for pattern in timestamp_patterns)
    
    # Screenplay detection
    screenplay_indicators = [
        "INT.", "EXT.", "FADE IN:", "FADE OUT", "CUT TO:", 
        "SCENE", "INTERIOR", "EXTERIOR"
    ]
    is_screenplay = any(indicator in text.upper() for indicator in screenplay_indicators)
    
    # Check for stage directions (parentheses)
    has_stage_directions = bool(re.search(r"\([^)]{3,}\)", text))
    
    # Check for dialogue format (CHARACTER NAME:\n dialogue)
    has_dialogue_format = bool(re.search(r"^[A-Z][A-Z\s]+:\s*", text, re.MULTILINE))
    
    # Check for act/scene structure
    has_act_structure = bool(re.search(r"(?:ACT|SCENE)\s+[IVX\d]+", text, re.IGNORECASE))
    
    # Try to detect if it's JSON/structured
    is_json = False
    try:
        json.loads(text)
        is_json = True
    except:
        pass
    
    # Detect CSV structure
    is_csv = bool(re.search(r'^[^,]+,[^,]+', text, re.MULTILINE)) and text.count(',') > 10
    
    return {
        "timestamped": has_timestamp,
        "screenplay": is_screenplay,
        "stage_directions": has_stage_directions,
        "dialogue_format": has_dialogue_format,
        "act_structure": has_act_structure,
        "is_json": is_json,
        "is_csv": is_csv,
        "estimated_format": _estimate_format(
            is_screenplay, has_timestamp, is_json, is_csv, has_dialogue_format
        ),
        "complexity": _estimate_complexity(text)
    }

def _estimate_format(screenplay, timestamped, is_json, is_csv, dialogue_format):
    """Helper to estimate overall format type"""
    if is_json:
        return "structured_json"
    elif is_csv:
        return "csv"
    elif screenplay:
        return "screenplay"
    elif timestamped:
        return "timestamped_script"
    elif dialogue_format:
        return "dialogue_script"
    else:
        return "plain_text"

def _estimate_complexity(text):
    """Estimate script complexity"""
    word_count = len(text.split())
    line_count = len(text.split('\n'))
    
    if word_count > 10000:
        return "high"
    elif word_count > 3000:
        return "medium"
    else:
        return "low"