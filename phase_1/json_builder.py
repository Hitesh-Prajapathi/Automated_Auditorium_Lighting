"""
JSON output builder module
"""

import json
from datetime import datetime
from config import JSON_INDENT, TIMESTAMP_FORMAT
from pipeline.timestamp_generator import format_timestamp

def build_scene_json(scene_id, scene_data, timestamp, emotion_analysis):
    """
    Build comprehensive scene JSON with all metadata
    
    Args:
        scene_id (str): Unique scene identifier
        scene_data (dict): Scene content and metadata
        timestamp (dict): Start/end times
        emotion_analysis (dict): Emotion analysis results
        
    Returns:
        dict: Complete scene JSON object
    """
    scene_json = {
        "scene_id": scene_id,
        "timing": {
            "start_time": timestamp["start"],
            "end_time": timestamp["end"],
            "duration": timestamp.get("duration", timestamp["end"] - timestamp["start"])
        },
        "content": {
            "text": scene_data.get("content", ""),
            "word_count": len(scene_data.get("content", "").split()),
            "type": scene_data.get("type", "segment")
        },
        "emotion": emotion_analysis
    }
    
    # Add optional fields if present
    if "header" in scene_data:
        scene_json["content"]["header"] = scene_data["header"]
    
    if "location" in scene_data:
        scene_json["content"]["location"] = scene_data["location"]
    
    if "speakers" in scene_data:
        scene_json["content"]["speakers"] = scene_data["speakers"]
        scene_json["content"]["speaker_count"] = len(scene_data["speakers"])
    
    # Add formatted timestamps if requested
    if TIMESTAMP_FORMAT == "timecode":
        scene_json["timing"]["start_timecode"] = format_timestamp(
            timestamp["start"], "timecode"
        )
        scene_json["timing"]["end_timecode"] = format_timestamp(
            timestamp["end"], "timecode"
        )
    
    return scene_json

def build_complete_output(scenes, metadata):
    """
    Build complete JSON output with metadata
    
    Args:
        scenes (list): List of scene JSON objects
        metadata (dict): Script metadata
        
    Returns:
        dict: Complete output JSON structure
    """
    total_duration = scenes[-1]["timing"]["end_time"] if scenes else 0
    
    # Calculate emotion distribution
    emotion_distribution = _calculate_emotion_distribution(scenes)
    
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "total_scenes": len(scenes),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": format_timestamp(total_duration, "timecode"),
            "format_detected": metadata.get("format", "unknown"),
            "source_file": metadata.get("source", "unknown"),
            "emotion_distribution": emotion_distribution
        },
        "scenes": scenes
    }
    
    # Add optional metadata fields
    if "genre" in metadata:
        output["metadata"]["genre"] = metadata["genre"]
    
    if "stage_directions_found" in metadata:
        output["metadata"]["stage_directions_count"] = metadata["stage_directions_found"]
    
    if "complexity" in metadata:
        output["metadata"]["complexity"] = metadata["complexity"]
    
    return output

def _calculate_emotion_distribution(scenes):
    """
    Calculate emotion distribution across all scenes
    
    Args:
        scenes (list): List of scene objects
        
    Returns:
        dict: Emotion distribution statistics
    """
    emotion_counts = {}
    total_scenes = len(scenes)
    
    for scene in scenes:
        emotion = scene.get("emotion", {}).get("primary_emotion", "neutral")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Calculate percentages
    emotion_percentages = {
        emotion: round((count / total_scenes) * 100, 1) if total_scenes > 0 else 0
        for emotion, count in emotion_counts.items()
    }
    
    # Find dominant emotion
    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
    
    return {
        "counts": emotion_counts,
        "percentages": emotion_percentages,
        "dominant_emotion": dominant_emotion
    }

def save_json(data, filepath):
    """
    Save JSON to file with pretty printing
    
    Args:
        data (dict): Data to save
        filepath (str): Output file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=JSON_INDENT, ensure_ascii=False)

def save_json_compact(data, filepath):
    """
    Save JSON in compact format (no indentation)
    
    Args:
        data (dict): Data to save
        filepath (str): Output file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)