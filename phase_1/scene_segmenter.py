"""
Scene segmentation module with context-aware splitting
"""

import re
from config import MAX_WORDS_PER_SCENE, MIN_WORDS_PER_SCENE, SCENE_MARKERS

def segment_scenes(text, format_info):
    """
    Context-aware scene segmentation based on format
    
    Args:
        text (str): Cleaned script text
        format_info (dict): Format information from detect_format()
        
    Returns:
        list: List of scene dictionaries with content and metadata
    """
    if format_info.get("screenplay"):
        return _segment_screenplay(text)
    elif format_info.get("dialogue_format"):
        return _segment_dialogue(text)
    elif format_info.get("act_structure"):
        return _segment_by_acts(text)
    else:
        return _segment_generic(text)

def _segment_screenplay(text):
    """
    Segment screenplay by scene headers (INT., EXT., etc.)
    
    Args:
        text (str): Screenplay text
        
    Returns:
        list: Segmented scenes
    """
    # Create regex pattern from scene markers
    markers_pattern = "|".join(re.escape(marker) for marker in SCENE_MARKERS)
    scene_pattern = rf"({markers_pattern}[^\n]+)"
    
    # Split by scene headers
    parts = re.split(scene_pattern, text, flags=re.IGNORECASE)
    
    scenes = []
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i].strip()
            content = parts[i+1].strip()
            
            if content:  # Only add non-empty scenes
                scenes.append({
                    "header": header,
                    "content": content,
                    "type": "screenplay_scene",
                    "location": _extract_location(header)
                })
    
    # If no scenes found, fall back to generic segmentation
    if not scenes:
        return _segment_generic(text)
    
    return scenes

def _extract_location(header):
    """Extract location from scene header"""
    # Remove common prefixes
    location = re.sub(r"^(INT\.|EXT\.|INTERIOR|EXTERIOR)\s*", "", header, flags=re.IGNORECASE)
    # Extract first part before dash or period
    location = re.split(r"[-\.]", location)[0].strip()
    return location if location else "UNKNOWN"

def _segment_dialogue(text):
    """
    Segment by speaker changes (for dialogue-heavy scripts)
    
    Args:
        text (str): Dialogue script text
        
    Returns:
        list: Segmented dialogue blocks
    """
    # Split by character names (ALL CAPS followed by colon)
    dialogue_pattern = r"(^[A-Z][A-Z\s]{2,}:)"
    parts = re.split(dialogue_pattern, text, flags=re.MULTILINE)
    
    scenes = []
    current_scene = []
    current_speakers = []
    word_count = 0
    
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            speaker = parts[i].strip().rstrip(':')
            dialogue = parts[i+1].strip()
            
            current_scene.append(f"{speaker}: {dialogue}")
            current_speakers.append(speaker)
            word_count += len(dialogue.split())
            
            # Create scene if word limit reached
            if word_count >= MAX_WORDS_PER_SCENE:
                scenes.append({
                    "content": "\n".join(current_scene),
                    "type": "dialogue_block",
                    "speakers": list(set(current_speakers)),
                    "speaker_count": len(set(current_speakers))
                })
                current_scene = []
                current_speakers = []
                word_count = 0
    
    # Add remaining content
    if current_scene:
        scenes.append({
            "content": "\n".join(current_scene),
            "type": "dialogue_block",
            "speakers": list(set(current_speakers)),
            "speaker_count": len(set(current_speakers))
        })
    
    return scenes if scenes else _segment_generic(text)

def _segment_by_acts(text):
    """
    Segment by acts and scenes
    
    Args:
        text (str): Script with act structure
        
    Returns:
        list: Segmented by acts/scenes
    """
    # Split by ACT or SCENE markers
    act_pattern = r"((?:ACT|SCENE)\s+[IVX\d]+[^\n]*)"
    parts = re.split(act_pattern, text, flags=re.IGNORECASE)
    
    scenes = []
    for i in range(1, len(parts), 2):
        if i+1 < len(parts):
            header = parts[i].strip()
            content = parts[i+1].strip()
            
            # Further segment long acts into smaller scenes
            if len(content.split()) > MAX_WORDS_PER_SCENE * 2:
                subscenes = _segment_generic(content)
                for j, subscene in enumerate(subscenes):
                    scenes.append({
                        "header": f"{header} - Part {j+1}",
                        "content": subscene["content"],
                        "type": "act_segment"
                    })
            else:
                scenes.append({
                    "header": header,
                    "content": content,
                    "type": "act_segment"
                })
    
    return scenes if scenes else _segment_generic(text)

def _segment_generic(text, max_words=MAX_WORDS_PER_SCENE):
    """
    Generic segmentation by word count with sentence awareness
    
    Args:
        text (str): Text to segment
        max_words (int): Maximum words per scene
        
    Returns:
        list: Segmented scenes
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    scenes = []
    current_scene = []
    word_count = 0
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        sentence_words = len(sentence.split())
        
        # Check if adding this sentence would exceed limit
        if word_count + sentence_words > max_words and word_count >= MIN_WORDS_PER_SCENE:
            scenes.append({
                "content": " ".join(current_scene),
                "type": "segment",
                "word_count": word_count
            })
            current_scene = [sentence]
            word_count = sentence_words
        else:
            current_scene.append(sentence)
            word_count += sentence_words
    
    # Add remaining content
    if current_scene:
        scenes.append({
            "content": " ".join(current_scene),
            "type": "segment",
            "word_count": word_count
        })
    
    return scenes