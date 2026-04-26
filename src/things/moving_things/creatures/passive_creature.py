import pygame
from .base_creature import Creature, Vec2
from config import passive_creatures as pc_config
from utils.sprite_sheet import load_frames
from utils.animation import Animation
from pathlib import Path

FISH_FRAMES = None

def get_fish_frames():
    global FISH_FRAMES
    if FISH_FRAMES is None:
        FISH_FRAMES = load_frames(Path("assets/sprites/fish.png"), 32, 32, 4)
    return FISH_FRAMES

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, size: int = 18) -> None:  #removed kwargs 

        frames = get_fish_frames()

        base = pygame.transform.scale(frames[0], (size, size))
        super().__init__(base, pos)

        # REMOVED       Temporarily creating a colored surface from the size of the creature but later on intead of size we will inject the creatures with the path to their image and create their surface from that image, then adjust that image to their size
        self.color = (0,50,255)         # THIS IS   no longer    TEMPORARY  

        scaled_frames = [pygame.transform.scale(f, (size, size)) for f in frames]
        self.anim = Animation(scaled_frames, fps=8)

        white = pygame.Surface((size, size))
        white.fill((250, 250, 250))
        white.set_colorkey(None)
        self._white_flash_image = white

        self._base_image = self.anim.get_image()  # updated each frame
        self.image = self._base_image

        self.fear_radius = fear_radius
        self.mass = pc_config["MASS"]
        self.thrust = pc_config["THRUST"]
        self.is_sprinting = False
        self.sprint_multiplier = 1.4
        self.health = pc_config["HEALTH"]
        self.max_health = pc_config["HEALTH"]
        self.species = "passive"
        self.scan_duration = 4.0

    def think(self, dt: float, player_pos: Vec2) -> Vec2:      #only passing player pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.fear_radius:
            # flee at full speed
            self.is_sprinting = True
            return self._dir_away(player_pos)
        else:
            # wander at reduced speed (looks natural)
            self.is_sprinting = False
            return self.wander_dir(dt)
        
    def update(self, dt, bound_rect, area_tiles, player_pos):
        if not self.is_dying:
            self.anim.update(dt)
            self._base_image = self.anim.get_image()
            if self.velocity.x < 0:
                self._base_image = pygame.transform.flip(self._base_image, True, False)
        super().update(dt, bound_rect, area_tiles, player_pos)
