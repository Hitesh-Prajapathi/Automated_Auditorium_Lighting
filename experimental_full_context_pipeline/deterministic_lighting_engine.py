"""
Deterministic Lighting Engine

Converts emotion vectors → lighting states.
Fully deterministic. NO LLM. NO RAG.

Rules:
  - intensity = BASE_INTENSITY + (energy × ENERGY_INTENSITY_SCALE)
  - warmth derived from valence
  - color palette selected by emotion label
  - 60% primary / 25% secondary / 15% neutral anchor
  - Consecutive scenes are blended via LIGHTING_BLEND_FACTOR
  - No full-stage single saturated color
"""

from .config_full_context import (
    LIGHTING_BLEND_FACTOR,
    BASE_INTENSITY,
    ENERGY_INTENSITY_SCALE,
    PRIMARY_COLOR_RATIO,
    SECONDARY_COLOR_RATIO,
    ANCHOR_COLOR_RATIO,
)


# =============================================================================
# EMOTION → COLOR PALETTE MAP
# =============================================================================
# Each palette has: primary (60%), secondary (25%), anchor (15%).
# Anchor is always a desaturated neutral to prevent full-stage saturation.
# Hex values chosen for theatrical lighting aesthetics.

EMOTION_PALETTES = {
    # --- Positive high-energy ---
    "joy": {
        "primary":   "#FFB347",  # warm amber
        "secondary": "#FFD700",  # gold
        "anchor":    "#FFF5E1",  # soft cream
    },
    "excitement": {
        "primary":   "#FF6F61",  # coral
        "secondary": "#FFA07A",  # light salmon
        "anchor":    "#FFF0E0",  # peach cream
    },
    "triumph": {
        "primary":   "#DAA520",  # goldenrod
        "secondary": "#FF8C00",  # dark orange
        "anchor":    "#FFFACD",  # lemon chiffon
    },
    "amusement": {
        "primary":   "#FFD166",  # sunflower
        "secondary": "#06D6A0",  # mint
        "anchor":    "#F0F0E8",  # warm white
    },
    "elation": {
        "primary":   "#FFDF00",  # golden yellow
        "secondary": "#FF69B4",  # hot pink
        "anchor":    "#FFFFF0",  # ivory
    },

    # --- Positive low-energy ---
    "tenderness": {
        "primary":   "#FFB6C1",  # light pink
        "secondary": "#DDA0DD",  # plum
        "anchor":    "#FFF0F5",  # lavender blush
    },
    "serenity": {
        "primary":   "#87CEEB",  # sky blue
        "secondary": "#B0E0E6",  # powder blue
        "anchor":    "#F0F8FF",  # alice blue
    },
    "hope": {
        "primary":   "#98FB98",  # pale green
        "secondary": "#FFD700",  # gold
        "anchor":    "#F5FFFA",  # mint cream
    },

    # --- Negative high-energy ---
    "anger": {
        "primary":   "#C0392B",  # dark crimson (NOT pure red)
        "secondary": "#E74C3C",  # softer red
        "anchor":    "#2C2C2C",  # charcoal (prevents full-red stage)
    },
    "fear": {
        "primary":   "#4A235A",  # deep purple
        "secondary": "#1A1A2E",  # midnight blue
        "anchor":    "#3D3D3D",  # dark grey
    },
    "rage": {
        "primary":   "#8B0000",  # dark red
        "secondary": "#DC143C",  # crimson
        "anchor":    "#333333",  # dark charcoal
    },
    "disgust": {
        "primary":   "#556B2F",  # dark olive green
        "secondary": "#6B8E23",  # olive drab
        "anchor":    "#3E3E3E",  # grey
    },

    # --- Negative low-energy ---
    "sadness": {
        "primary":   "#4169E1",  # royal blue
        "secondary": "#6A5ACD",  # slate blue
        "anchor":    "#2F2F3F",  # dark blue-grey
    },
    "melancholy": {
        "primary":   "#5F6A8A",  # muted blue-grey
        "secondary": "#7B68AE",  # muted purple
        "anchor":    "#383848",  # dark slate
    },
    "grief": {
        "primary":   "#2C3E50",  # dark slate blue
        "secondary": "#34495E",  # wet asphalt
        "anchor":    "#1C1C1C",  # near black
    },
    "despair": {
        "primary":   "#1A1A2E",  # midnight
        "secondary": "#2C2C54",  # dark indigo
        "anchor":    "#0D0D0D",  # almost black
    },

    # --- Mid-range / dramatic ---
    "tension": {
        "primary":   "#B8860B",  # dark goldenrod
        "secondary": "#8B4513",  # saddle brown
        "anchor":    "#3B3B3B",  # dark grey
    },
    "suspense": {
        "primary":   "#2E4053",  # dark blue-grey
        "secondary": "#5D6D7E",  # cool grey
        "anchor":    "#1C2833",  # very dark blue
    },
    "mystery": {
        "primary":   "#483D8B",  # dark slate blue
        "secondary": "#6A5ACD",  # slate blue
        "anchor":    "#2C2C38",  # deep grey
    },
    "surprise": {
        "primary":   "#E67E22",  # carrot orange
        "secondary": "#F1C40F",  # sunflower yellow
        "anchor":    "#ECF0F1",  # light grey
    },
    "confusion": {
        "primary":   "#7F8C8D",  # grey
        "secondary": "#95A5A6",  # silver
        "anchor":    "#BDC3C7",  # light silver
    },
    "determination": {
        "primary":   "#E67E22",  # orange
        "secondary": "#D35400",  # pumpkin
        "anchor":    "#F5F5DC",  # beige
    },
    "betrayal": {
        "primary":   "#800020",  # burgundy
        "secondary": "#4A0000",  # very dark red
        "anchor":    "#2C2C2C",  # charcoal
    },

    # --- Comedy / humor ---
    "humor": {
        "primary":   "#FFD166",  # sunflower
        "secondary": "#FF9F43",  # mandarin
        "anchor":    "#FFF5E1",  # soft cream
    },
    "absurdity": {
        "primary":   "#E056A0",  # magenta pink
        "secondary": "#00CEC9",  # teal
        "anchor":    "#FFF3E0",  # warm cream
    },
    "comedic_energy": {
        "primary":   "#FFB550",  # warm orange
        "secondary": "#FF82AB",  # candy pink
        "anchor":    "#FFE99A",  # sunny yellow
    },
    "playful": {
        "primary":   "#FF6B81",  # watermelon
        "secondary": "#7BED9F",  # light green
        "anchor":    "#FFF5E6",  # cream
    },
    "irony": {
        "primary":   "#A29BFE",  # soft purple
        "secondary": "#FD79A8",  # pink
        "anchor":    "#DFE6E9",  # light cool grey
    },

    # --- Romance / warmth ---
    "romantic": {
        "primary":   "#FF6B9D",  # rose pink
        "secondary": "#C44569",  # deep rose
        "anchor":    "#FFF0F5",  # lavender blush
    },
    "love": {
        "primary":   "#FF6B6B",  # soft red
        "secondary": "#EE5A80",  # deep pink
        "anchor":    "#FFF0F0",  # pink white
    },
    "passion": {
        "primary":   "#E84393",  # hot pink
        "secondary": "#FD79A8",  # blush
        "anchor":    "#2C2C34",  # dark backdrop
    },

    # --- Nostalgia / wistful ---
    "nostalgia": {
        "primary":   "#C2956C",  # sepia
        "secondary": "#C27D82",  # dusty rose
        "anchor":    "#FFF5E1",  # warm cream
    },

    # --- Anxiety ---
    "anxiety": {
        "primary":   "#C89600",  # sickly amber
        "secondary": "#82B432",  # nervous green
        "anchor":    "#F0E68C",  # khaki
    },

    # --- Awe / spiritual ----
    "awe": {
        "primary":   "#6495ED",  # cornflower blue
        "secondary": "#8A2BE2",  # blue violet
        "anchor":    "#F0F8FF",  # alice blue
    },

    # --- Jealousy ---
    "jealousy": {
        "primary":   "#228B22",  # forest green
        "secondary": "#C8C800",  # acid yellow
        "anchor":    "#3D3D2F",  # dark olive
    },

    # --- Chaotic ---
    "chaotic_energy": {
        "primary":   "#FF10F0",  # neon pink
        "secondary": "#0082FF",  # electric blue
        "anchor":    "#1A1A2E",  # midnight
    },

    # --- Anticipation ---
    "anticipation": {
        "primary":   "#FFAA32",  # amber glow
        "secondary": "#008080",  # teal
        "anchor":    "#FFF5DC",  # corn silk
    },

    # --- Relief ---
    "relief": {
        "primary":   "#90EE90",  # light green
        "secondary": "#87CEEB",  # sky blue
        "anchor":    "#F5FFFA",  # mint cream
    },

    # --- Neutral / default (WARM, not grey!) ---
    "neutral": {
        "primary":   "#FFF4E5",  # warm white
        "secondary": "#FFE1B4",  # soft amber
        "anchor":    "#C8D2E6",  # pale blue
    },
}


# =============================================================================
# COLOR UTILITIES
# =============================================================================

def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert '#RRGGBB' to (R, G, B) ints."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (R, G, B) ints to '#RRGGBB'."""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def _blend_hex(color_a: str, color_b: str, factor: float) -> str:
    """
    Linearly interpolate two hex colors.
    factor = 1.0 → pure color_b (target).
    factor = 0.0 → pure color_a (previous).
    """
    ra, ga, ba = _hex_to_rgb(color_a)
    rb, gb, bb = _hex_to_rgb(color_b)
    r = ra + (rb - ra) * factor
    g = ga + (gb - ga) * factor
    b = ba + (bb - ba) * factor
    return _rgb_to_hex(r, g, b)


def _color_distance(hex_a: str, hex_b: str) -> float:
    """Euclidean distance in RGB space (0–441.67 max)."""
    ra, ga, ba = _hex_to_rgb(hex_a)
    rb, gb, bb = _hex_to_rgb(hex_b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


# =============================================================================
# PUBLIC API
# =============================================================================

# Synonym mapping for fuzzy emotion matching
EMOTION_SYNONYMS = {
    # Joy family
    "happiness": "joy", "happy": "joy", "elation": "elation", "delight": "joy",
    "cheerful": "joy", "bliss": "joy", "euphoria": "excitement",
    # Sadness family
    "sorrow": "sadness", "mourning": "grief", "heartbreak": "sadness",
    "loneliness": "despair", "longing": "nostalgia", "wistful": "nostalgia", "regret": "melancholy",
    # Fear family
    "terror": "fear", "dread": "fear", "horror": "fear", "panic": "fear",
    "unease": "anxiety", "worry": "anxiety", "nervous": "anxiety",
    "foreboding": "tension",
    # Anger family  
    "rage": "rage", "fury": "rage", "wrath": "rage", "irritation": "anger",
    "frustration": "anger", "resentment": "anger", "outrage": "anger",
    # Comedy family
    "humorous": "humor", "comic": "humor", "funny": "humor", "witty": "humor",
    "sarcasm": "irony", "satire": "irony", "absurd": "absurdity", "ridiculous": "absurdity",
    "silly": "humor", "lighthearted": "amusement", "whimsical": "playful",
    # Romance family
    "affection": "love", "tender": "tenderness", "intimate": "romantic",
    # Positive complex
    "wonder": "awe", "amazement": "awe", "astonishment": "surprise",
    "gratitude": "hope", "peace": "serenity", "calm": "serenity",
    "tranquil": "serenity", "contentment": "serenity", "content": "serenity",
    "courage": "determination", "victory": "triumph", "pride": "triumph",
    "optimism": "hope", "aspiration": "hope",
    # Negative complex
    "contempt": "disgust", "revulsion": "disgust", "loathing": "disgust",
    "shame": "despair", "guilt": "despair", "humiliation": "despair",
    "envy": "jealousy", "paranoia": "anxiety",
    "bewilderment": "confusion", "disorientation": "confusion",
    # Dramatic
    "dramatic": "tension", "intense": "tension", "dark": "mystery",
    "eerie": "mystery", "sinister": "fear", "menacing": "fear",
    "chaotic": "chaotic_energy", "frenetic": "chaotic_energy", "manic": "chaotic_energy",
    "bittersweet": "nostalgia", "poignant": "nostalgia",
    "triumphant": "triumph", "heroic": "triumph", "epic": "triumph",
    "excited": "excitement", "thrilled": "excitement", "eager": "anticipation",
}


def get_emotion_palette(label: str) -> dict:
    """
    Look up the color palette for an emotion label.
    Uses fuzzy synonym matching before falling back to neutral.
    """
    key = label.lower().strip()
    
    # Direct match
    if key in EMOTION_PALETTES:
        return EMOTION_PALETTES[key]
    
    # Synonym match
    canonical = EMOTION_SYNONYMS.get(key)
    if canonical and canonical in EMOTION_PALETTES:
        return EMOTION_PALETTES[canonical]
    
    # Partial match: check if the emotion label is a substring of any palette key
    for palette_key in EMOTION_PALETTES:
        if palette_key in key or key in palette_key:
            return EMOTION_PALETTES[palette_key]
    
    # Last resort: neutral (now warm-toned, not grey)
    return EMOTION_PALETTES["neutral"]


def compute_lighting_state(scene: dict, prev_state: dict = None) -> dict:
    """
    Compute a single lighting state from a scene's emotion vector.

    Args:
        scene:      Scene dict with "emotion" sub-dict (label, energy, valence).
        prev_state: Previous lighting state dict (for blending), or None.

    Returns:
        Lighting state dict with keys:
            scene_id, intensity, warmth, palette (primary/secondary/anchor),
            color_ratios, blended (bool).
    """
    emo = scene["emotion"]
    energy = emo["energy"]
    valence = emo["valence"]
    label = emo["label"]

    # --- Intensity ---
    intensity = round(BASE_INTENSITY + (energy * ENERGY_INTENSITY_SCALE), 2)
    intensity = min(100.0, max(0.0, intensity))

    # --- Warmth ---
    warmth = round(valence, 4)

    # --- Palette ---
    target_palette = get_emotion_palette(label)

    # --- Blend with previous state ---
    blended = False
    if prev_state is not None:
        blended = True
        prev_palette = prev_state["palette"]
        palette = {
            "primary":   _blend_hex(prev_palette["primary"],   target_palette["primary"],   LIGHTING_BLEND_FACTOR),
            "secondary": _blend_hex(prev_palette["secondary"], target_palette["secondary"], LIGHTING_BLEND_FACTOR),
            "anchor":    _blend_hex(prev_palette["anchor"],    target_palette["anchor"],    LIGHTING_BLEND_FACTOR),
        }
    else:
        palette = dict(target_palette)  # copy

    return {
        "scene_id": scene.get("scene_id", "unknown"),
        "intensity": intensity,
        "warmth": warmth,
        "palette": palette,
        "color_ratios": {
            "primary": PRIMARY_COLOR_RATIO,
            "secondary": SECONDARY_COLOR_RATIO,
            "anchor": ANCHOR_COLOR_RATIO,
        },
        "blended": blended,
    }


def generate_all_lighting(scenes: list) -> list:
    """
    Generate lighting states for all scenes with carry-forward blending.

    Args:
        scenes: List of scene dicts (post-smoothing).

    Returns:
        List of lighting state dicts, one per scene.
    """
    states = []
    prev_state = None
    for scene in scenes:
        state = compute_lighting_state(scene, prev_state)
        states.append(state)
        prev_state = state
    return states


def calculate_lighting_continuity_score(states: list) -> float:
    """
    Measure lighting continuity across the sequence.

    Computes average color distance (primary channel) between adjacent states.
    Lower distance = smoother transitions.

    Returns:
        Continuity score as a float (0–100).
        100 = perfectly smooth, 0 = maximally discontinuous.
    """
    if len(states) < 2:
        return 100.0

    MAX_RGB_DIST = 441.67  # sqrt(255² + 255² + 255²)
    total_dist = 0.0
    pairs = len(states) - 1

    for i in range(1, len(states)):
        dist = _color_distance(
            states[i - 1]["palette"]["primary"],
            states[i]["palette"]["primary"],
        )
        total_dist += dist

    avg_dist = total_dist / pairs
    # Normalise to 0-100 (100 = smooth)
    score = round((1.0 - avg_dist / MAX_RGB_DIST) * 100, 2)
    return max(0.0, score)
