"""
Global configurations and constants for Agro-Defender.
All variables are in UPPERCASE to denote constants.
"""

# ==========================================
# DISPLAY CONFIGURATION
# ==========================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60  # Frames per second for the Pygame rendering engine

# ==========================================
# COLORS (RGB)
# ==========================================
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_PLANT_GREEN = (34, 139, 34)
COLOR_ENEMY_RED = (220, 20, 60)
COLOR_CURSOR_BLUE = (65, 105, 225)

# ==========================================
# GAMEPLAY PARAMETERS
# ==========================================
GAME_DURATION_SECONDS = 60
PLAYER_LIVES = 3
ENEMY_SPEED_MIN = 3
ENEMY_SPEED_MAX = 7
SPAWN_RATE_MILLISECONDS = 800

# ==========================================
# COMPUTER VISION CONFIGURATION
# ==========================================
CAMERA_INDEX = 0  # 0 is usually the default built-in webcam
CV_DETECTION_CONFIDENCE = 0.7
CV_TRACKING_CONFIDENCE = 0.7
