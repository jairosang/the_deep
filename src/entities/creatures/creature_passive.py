import pygame
from src.entities.creatures.base_creature import Creature, Vec2
from config import passive_creatures as pc_config

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, size: int = 18) -> None:  #removed kwargs 
        super().__init__(pygame.Surface((20,20)), pos)
        self.image.fill((0,0,150))         # THIS IS TEMPORARY  

        self.fear_radius = fear_radius
        self.mass = pc_config["MASS"]
        self.thrust = pc_config["THRUST"]
        self.is_sprinting = False
        self.sprint_multiplier = 1.4

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
