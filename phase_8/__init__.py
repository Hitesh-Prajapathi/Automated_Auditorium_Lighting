"""
Phase 8: Hardware Automation Module
DMX, OSC, MIDI control - real-world signals

This is the ONLY phase where hardware-specific concepts are allowed:
- DMX channels/universes
- OSC addresses
- MIDI notes/CC
- Patch maps
"""

from .dmx_adapter import DMXAdapter, convert_instruction_to_cues
from .osc_sender import get_osc_client
from .lightkey_control import LightKeyController

__all__ = [
    'DMXAdapter',
    'convert_instruction_to_cues',
    'get_osc_client',
    'LightKeyController',
]
