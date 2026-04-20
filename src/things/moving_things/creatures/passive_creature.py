import pygame
from .base_creature import Creature, Vec2
from config import passive_creatures as pc_config

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, size: int = 18) -> None:  #removed kwargs 
        super().__init__(pygame.Surface((size, size)), pos)     # Temporarily creating a colored surface from the size of the creature but later on intead of size we will inject the creatures with the path to their image and create their surface from that image, then adjust that image to their size
        self.color = (0,50,255)         # THIS IS TEMPORARY  

        self.fear_radius = fear_radius
        self.mass = pc_config["MASS"]
        self.thrust = pc_config["THRUST"]
        self.is_sprinting = False
        self.sprint_multiplier = 1.4
        self.health = pc_config["HEALTH"]
        self.max_health = pc_config["HEALTH"]

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
