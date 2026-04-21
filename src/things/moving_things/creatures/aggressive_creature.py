from .base_creature import Creature, Vec2
from config import aggresive_creatures as ac_config
import pygame
from utils.sprite_sheet import load_frames
from utils.animation import Animation
from pathlib import Path

FISH_BIG_FRAMES = None
FISH_DART_FRAMES = None

def get_fish_big_frames():
    global FISH_BIG_FRAMES
    if FISH_BIG_FRAMES is None:
        FISH_BIG_FRAMES = load_frames(Path("assets/sprites/fish-big.png"), 54, 49, 4)
    return FISH_BIG_FRAMES
 
def get_fish_dart_frames():
    global FISH_DART_FRAMES
    if FISH_DART_FRAMES is None:
        FISH_DART_FRAMES = load_frames(Path("assets/sprites/fish-dart.png"), 39, 20, 4)
    return FISH_DART_FRAMES

class AggressiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], chase_radius: float = 260.0, size: int = 18, sprite: str = "fish-big") -> None: #also removed kwargs
    
        if sprite == "fish-dart":
            frames = get_fish_dart_frames()
        else:
            frames = get_fish_big_frames()
        base = pygame.transform.scale(frames[0], (size, size))
        super().__init__(base, pos)
        self.color = (255, 0, 0)   # THIS IS   no longer    TEMPORARY  

        scaled_frames = [pygame.transform.scale(f, (size, size)) for f in frames]
        self.anim = Animation(scaled_frames, fps=8)
 
        white = pygame.Surface((size, size))
        white.fill((250, 250, 250))
        white.set_colorkey(None)
        self._white_flash_image = white


        self._base_image = self.anim.get_image()
        self.image = self._base_image


        self.chase_radius = chase_radius
        self.mass = ac_config["MASS"]
        self.thrust = ac_config["THRUST"]
        self.is_sprinting = False
        self.sprint_multiplier = 1.3
        self.health = ac_config["HEALTH"]
        self.max_health = ac_config["HEALTH"]

    def think(self, dt: float, player_pos) -> Vec2:                             #is now only passing player_pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.chase_radius:
            # chase at full speed
            self.is_sprinting = True
            return self._dir_towards(player_pos)
        else:
            # patrol/wander at half thrust
            self.is_sprinting = False
            return self.wander_dir(dt)
        
    def update(self, dt, bound_rect, area_tiles, player_pos):
        if not self.is_dying:
            self.anim.update(dt)
            self._base_image = self.anim.get_image()
        super().update(dt, bound_rect, area_tiles, player_pos)