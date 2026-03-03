from pathlib import Path
import pygame

# === WINDOW & DISPLAY ===
game = {
    "GAME_TITLE" : "The Deep",
    "FPS" : 30,
    "TILEMAP_PATH" : Path("assets/tilemap/underwater_tilemap.tmj")
}

# Player initialization constants
player = {
    "SIZE": (40, 70),
    "START_POS": (50, 50),
    "SPEED": 400,
    "SPRINT_MULTIPLIER": 1.5,
    "ACCELERATION": 1.4,
    "DECELERATION": 1.3,
    
    "BASE_STATS": {
        "MAX_HEALTH": 50,
        "MAX_OXYGEN": 50,
        "OXYGEN_DEPLETION_RATE": 0.5,
        "MAX_DEPTH_LIMIT": 100,
        "INVENTORY_CAPACITY": 5,
    },

}
