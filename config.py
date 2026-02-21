import pygame

# === WINDOW & DISPLAY ===
GAME_TITLE = "The Deep"
FPS = 30
TILE_SIZE = 32  # Standard tile size for 2D games, align with assets later


# Player initialization constants
player = {
    "SIZE": (40, 70),
    "START_POS": (50, 50),
    "SPEED": 400,
    "SPRINT_MULTIPLIER": 1.5,
    
    "BASE_STATS": {
        "MAX_HEALTH": 50,
        "MAX_OXYGEN": 50,
        "OXYGEN_DEPLETION_RATE": 1.0,
        "MAX_DEPTH_LIMIT": 100,
        "INVENTORY_CAPACITY": 5,
    },

}
