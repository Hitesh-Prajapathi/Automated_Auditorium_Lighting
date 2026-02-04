"""
Color utility functions for visualization
"""

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB to hex color
    
    Args:
        r, g, b: RGB values (0-255)
        
    Returns:
        Hex color string (e.g., "#FF0000")
    """
    return f"#{r:02x}{g:02x}{b:02x}"

def get_color_name(r: int, g: int, b: int) -> str:
    """
    Get human-readable color name from RGB
    
    Args:
        r, g, b: RGB values (0-255)
        
    Returns:
        Color name string
    """
    # Brightness
    brightness = (r + g + b) / 3
    
    # Check for grayscale
    if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
        if brightness < 50:
            return "Black"
        elif brightness < 120:
            return "Dark Gray"
        elif brightness < 180:
            return "Gray"
        elif brightness < 230:
            return "Light Gray"
        else:
            return "White"
    
    # Dominant color
    max_val = max(r, g, b)
    
    if max_val == r:
        if g > 100 and b < 50:
            return "Orange" if g < 200 else "Yellow"
        elif b > 100:
            return "Magenta" if b > g else "Pink"
        else:
            return "Red"
    elif max_val == g:
        if r > 100:
            return "Yellow" if r > 200 else "Lime"
        elif b > 100:
            return "Cyan" if b > r else "Teal"
        else:
            return "Green"
    else:  # max_val == b
        if r > 100:
            return "Magenta" if r > g else "Purple"
        elif g > 100:
            return "Cyan" if g > r else "Sky Blue"
        else:
            return "Blue"

def dmx_to_percent(dmx_value: int) -> int:
    """
    Convert DMX value (0-255) to percentage (0-100)
    
    Args:
        dmx_value: DMX value (0-255)
        
    Returns:
        Percentage (0-100)
    """
    return int((dmx_value / 255) * 100)

def get_intensity_label(percent: int) -> str:
    """
    Get human-readable intensity label
    
    Args:
        percent: Intensity percentage (0-100)
        
    Returns:
        Label string
    """
    if percent == 0:
        return "Off"
    elif percent < 20:
        return "Very Dim"
    elif percent < 40:
        return "Dim"
    elif percent < 60:
        return "Medium"
    elif percent < 80:
        return "Bright"
    else:
        return "Very Bright"