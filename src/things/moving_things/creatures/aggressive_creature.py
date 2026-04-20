from .base_creature import Creature, Vec2
from config import aggresive_creatures as ac_config
import pygame

class AggressiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], chase_radius: float = 260.0, size: int = 18) -> None: #also removed kwargs
        super().__init__(pygame.Surface((size, size)), pos)     # Temporarily creating a colored surface from the size of the creature but later on intead of size we will inject the creatures with the path to their image and create their surface from that image, then adjust that image to their size 
        self.color = (255,0,0)         # THIS IS TEMPORARY  

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