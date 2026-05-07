from pathlib import Path
import pygame

# === WINDOW & DISPLAY ===
game = {
    "GAME_TITLE" : "The Deep",
    "FPS" : 30,
    "SCREEN_SIZE": (0,0),
    "UNDERWATER_TILEMAP_PATH" : Path("assets/underwater/tilemap/dark_underwater_map.tmj"),
    "HOMEBASE_TILEMAP_PATH" : Path("assets/homebase/tilemap/homebase_map.tmj"),
    "DRAG": 0.9,
    "PRIMARY_FONT": Path("assets/fonts/Exo_2/Exo2-VariableFont_wght.ttf"),
    "SECONDARY_FONT": Path("assets/fonts/Michroma/Michroma-Regular.ttf"),
}

# Player initialization constants
player = {
    "SIZE": (32, 64),
    "UNDERWATER_START_POS": (70, 70),
    "HOMEBASE_START_POS": (300, 400),
    "SPRINT_MULTIPLIER": 1.5,
    "THRUST": 180,
    "MASS": 100,
    # Terminal velocity of every thing will be their thrust/drag
    
    "BASE_STATS": {
        "MAX_HEALTH": 50,
        "MAX_OXYGEN": 50,
        "OXYGEN_DEPLETION_RATE": 0.5,
        "MAX_DEPTH_LIMIT": 100 * 16,    # Every 16 pixels is one meter
        "INVENTORY_CAPACITY": 5,
    },
}

aggresive_creatures = {
    "MASS": 30,
    "THRUST": 160,
    "HEALTH": 30,
    "CONTACT_DAMAGE": 1,
}

passive_creatures = {
    "MASS": 15,
    "THRUST": 180,
    "HEALTH": 25,
}