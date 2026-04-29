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
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 4
SPAWN_RATE_MILLISECONDS = 800

# ==========================================
# COMPUTER VISION CONFIGURATION
# ==========================================
CAMERA_INDEX = 0  # 0 is usually the default built-in webcam
CV_DETECTION_CONFIDENCE = 0.7
CV_TRACKING_CONFIDENCE = 0.7

# --- AUDIO CONFIG ---
MUSIC_VOLUME = 0.3  # Volumen de la música (0.0 a 1.0)
SFX_VOLUME = 0.6    # Volumen de los efectos (0.0 a 1.0)
