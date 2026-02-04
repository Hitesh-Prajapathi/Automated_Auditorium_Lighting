"""
Timestamp generation and extraction module
"""

import re
from config import WORDS_PER_MINUTE, SCENE_TRANSITION_BUFFER

def generate_timestamps(scenes):
    """
    Generate timestamps based on word count and speaking speed
    
    Args:
        scenes (list): List of scene dictionaries
        
    Returns:
        list: List of timestamp dictionaries with start and end times
    """
    timestamps = []
    current_time = 0
    
    for scene in scenes:
        scene_text = scene.get("content", "")
        duration = _calculate_duration(scene_text)
        
        timestamps.append({
            "start": current_time,
            "end": current_time + duration,
            "duration": duration
        })
        
        # Add transition buffer between scenes
        current_time += duration + SCENE_TRANSITION_BUFFER
    
    return timestamps

def extract_timestamps(text, scenes):
    """
    Extract existing timestamps from text
    
    Args:
        text (str): Original text with timestamps
        scenes (list): List of scene dictionaries
        
    Returns:
        list: List of extracted timestamps
    """
    # Patterns for various timestamp formats
    patterns = [
        (r"\[(\d+):(\d+)(?::(\d+))?\]", "brackets"),  # [00:30] or [00:30:15]
        (r"^(\d+):(\d+)(?::(\d+))?", "plain"),        # 00:30 or 00:30:15
        (r"(\d+)\.(\d+)s", "seconds"),                # 10.5s
    ]
    
    timestamps = []
    scene_starts = []
    
    # Try to find timestamps in original text
    for pattern, pattern_type in patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if matches:
            for match in matches:
                time_seconds = _parse_timestamp(match, pattern_type)
                if time_seconds is not None:
                    scene_starts.append(time_seconds)
    
    # If we found timestamps, use them
    if scene_starts and len(scene_starts) >= len(scenes):
        for i, start_time in enumerate(scene_starts[:len(scenes)]):
            if i < len(scenes) - 1:
                end_time = scene_starts[i + 1]
            else:
                # For last scene, estimate duration
                duration = _calculate_duration(scenes[i].get("content", ""))
                end_time = start_time + duration
            
            timestamps.append({
                "start": start_time,
                "end": end_time,
                "duration": end_time - start_time,
                "extracted": True
            })
    else:
        # Fall back to generation
        timestamps = generate_timestamps(scenes)
        for ts in timestamps:
            ts["extracted"] = False
    
    return timestamps

def _parse_timestamp(match, pattern_type):
    """
    Parse timestamp from regex match
    
    Args:
        match: Regex match object
        pattern_type (str): Type of pattern matched
        
    Returns:
        int: Time in seconds, or None if invalid
    """
    try:
        groups = match.groups()
        
        if pattern_type == "seconds":
            # Format: 10.5s
            return int(groups[0]) + float(f"0.{groups[1]}")
        else:
            # Format: HH:MM:SS or MM:SS
            if len(groups) >= 3 and groups[2]:
                # HH:MM:SS
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                # MM:SS
                minutes = int(groups[0])
                seconds = int(groups[1])
                return minutes * 60 + seconds
    except (ValueError, IndexError):
        return None

def _calculate_duration(text):
    """
    Calculate scene duration based on word count
    
    Args:
        text (str): Scene text
        
    Returns:
        int: Duration in seconds
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    duration = int((word_count / WORDS_PER_MINUTE) * 60)
    
    # Minimum duration of 2 seconds
    return max(duration, 2)

def format_timestamp(seconds, format_type="seconds"):
    """
    Format seconds into various timestamp formats
    
    Args:
        seconds (int/float): Time in seconds
        format_type (str): Output format ('seconds', 'timecode', 'short')
        
    Returns:
        str: Formatted timestamp
    """
    if format_type == "timecode":
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    elif format_type == "short":
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    else:
        return f"{seconds:.1f}s"