"""
Playback engine for lighting cues with precise timing
"""

import json
import time
import asyncio
from typing import Dict, List, Callable, Optional
from pathlib import Path

class PlaybackEngine:
    """
    Engine to play lighting cues with accurate timing
    """
    
    def __init__(self, cues_file: str):
        """
        Initialize playback engine
        
        Args:
            cues_file: Path to cues JSON file
        """
        self.cues_file = cues_file
        self.cues_data = self._load_cues()
        self.current_cue_index = 0
        self.is_playing = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = None
        self.elapsed_time = 0
        self.callbacks = []
    
    def _load_cues(self) -> Dict:
        """Load cues from file"""
        with open(self.cues_file, 'r') as f:
            return json.load(f)
    
    def get_total_duration(self) -> float:
        """Get total duration of all cues"""
        cues = self.cues_data.get("cues", [])
        if not cues:
            return 0
        return max(cue.get("end_time", 0) for cue in cues)
    
    def get_current_cue(self) -> Optional[Dict]:
        """Get cue at current playback position"""
        for cue in self.cues_data.get("cues", []):
            start = cue.get("start_time", 0)
            end = cue.get("end_time", 0)
            if start <= self.elapsed_time < end:
                return cue
        return None
    
    def seek(self, time_seconds: float):
        """
        Seek to specific time
        
        Args:
            time_seconds: Time to seek to
        """
        self.elapsed_time = time_seconds
        self._notify_callbacks("seek", time_seconds)
    
    def play(self):
        """Start or resume playback"""
        if self.is_paused:
            # Resume from pause
            self.start_time = time.time() - self.elapsed_time
            self.is_paused = False
        else:
            # Start fresh
            self.start_time = time.time()
            self.elapsed_time = 0
        
        self.is_playing = True
        self._notify_callbacks("play", self.elapsed_time)
    
    def pause(self):
        """Pause playback"""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()
            self.elapsed_time = self.pause_time - self.start_time
            self._notify_callbacks("pause", self.elapsed_time)
    
    def stop(self):
        """Stop playback"""
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time = 0
        self.current_cue_index = 0
        self._notify_callbacks("stop", 0)
    
    def update(self) -> Dict:
        """
        Update playback state (call this in a loop)
        
        Returns:
            Current state dictionary
        """
        if self.is_playing and not self.is_paused:
            self.elapsed_time = time.time() - self.start_time
            
            # Check if playback finished
            if self.elapsed_time >= self.get_total_duration():
                self.stop()
        
        current_cue = self.get_current_cue()
        
        state = {
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "elapsed_time": self.elapsed_time,
            "total_duration": self.get_total_duration(),
            "current_cue": current_cue,
            "progress": (self.elapsed_time / self.get_total_duration() * 100) if self.get_total_duration() > 0 else 0
        }
        
        return state
    
    def register_callback(self, callback: Callable):
        """
        Register callback for playback events
        
        Args:
            callback: Function to call on events
        """
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, event: str, data):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def async_update_loop(self, websocket_broadcast: Callable):
        """
        Async update loop for WebSocket broadcasting
        
        Args:
            websocket_broadcast: Function to broadcast state updates
        """
        while True:
            if self.is_playing:
                state = self.update()
                await websocket_broadcast(state)
            await asyncio.sleep(0.05)  # 20 updates per second