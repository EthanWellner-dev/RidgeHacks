"""
config.py - Game configuration and settings.
"""

# Display settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
WINDOW_TITLE = "Dynamic ChemEngine"

# Color scheme
COLORS = {
    'background': (240, 245, 250),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
}

# Flask settings
FLASK_WIDTH = 300
FLASK_HEIGHT = 500
FLASK_X = 50
FLASK_Y = 100

# UI settings
DROPPER_WIDTH = 60
DROPPER_HEIGHT = 80
THERMOMETER_WIDTH = 50
THERMOMETER_HEIGHT = 300
HOTPLATE_WIDTH = 60
HOTPLATE_HEIGHT = 60

# Chemistry settings
DEFAULT_FLASK_VOLUME = 1.0  # Liters
DEFAULT_INITIAL_TEMP = 293.15  # Kelvin (20°C)
BOILING_POINT = 373.15  # Kelvin (100°C)

# Particle settings
PARTICLE_LIFETIME = 2.0  # Seconds
PARTICLE_RADIUS = 2.0  # Pixels
PARTICLE_GRAVITY = 100.0  # pixels/s^2

# Challenge settings
CHALLENGES = [
    "Color Shift",
    "Gas Burst",
    "Equilibrium Balance"
]

# Debug settings
DEBUG = False
SHOW_FPS = True
