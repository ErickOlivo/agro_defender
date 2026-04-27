"""
Mathematical utility functions for Agro-Defender.
"""

def map_coordinates(normalized_x: float, normalized_y: float, screen_width: int, screen_height: int) -> tuple[int, int]:
    """
    Maps MediaPipe normalized coordinates (0.0 to 1.0) to screen pixel coordinates.
    Ensures the mapped coordinates do not exceed the window boundaries.
    """
    x = int(normalized_x * screen_width)
    y = int(normalized_y * screen_height)
    
    # Clamp values to keep them strictly inside the window
    x = max(0, min(x, screen_width))
    y = max(0, min(y, screen_height))
    
    return x, y
