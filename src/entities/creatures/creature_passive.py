import pygame
from src.entities.creatures.base_creature import Creature, Vec2
from config import passive_creatures as pc_config

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, size: int = 18) -> None:  #removed kwargs 
        super().__init__(pos, size, pc_config["THRUST"])
        self.fear_radius = fear_radius
        self.mass = pc_config["MASS"]

    def think(self, dt: float, player_pos: Vec2) -> None:      #only passing player pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.fear_radius:
            # flee at full speed
            self.thrust = pc_config["THRUST"]
            return self._dir_away(player_pos)
        else:
            # wander at reduced speed (looks natural)
            self.thrust = pc_config["THRUST"] * 0.6
            return self.wander_dir(dt)

    def draw(self, screen: pygame.Surface) -> None:
        # Blue = passive
        super().draw(screen, color=(50, 120, 255))
