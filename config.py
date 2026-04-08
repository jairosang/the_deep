from pathlib import Path
import pygame

# === WINDOW & DISPLAY ===
game = {
    "GAME_TITLE" : "The Deep",
    "FPS" : 30,
    "SCREEN_SIZE": (0,0),
    "TILEMAP_PATH" : Path("assets/tilemap/dark_underwater_map.tmj"),
    "DRAG": 0.9,
}

# Player initialization constants
player = {
    "SIZE": (32, 64),
    "START_POS": (70, 70),
    "SPRINT_MULTIPLIER": 1.5,
    "THRUST": 180,
    # Terminal velocity of every thing will be their thrust/drag
    
    "BASE_STATS": {
        "MAX_HEALTH": 50,
        "MAX_OXYGEN": 50,
        "OXYGEN_DEPLETION_RATE": 0.5,
        "MAX_DEPTH_LIMIT": 100,
        "INVENTORY_CAPACITY": 5,
    },

}
