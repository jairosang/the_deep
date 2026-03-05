import pygame
from src.entities.creatures.base_creature import Creature, Vec2

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, size: int = 18, speed: float = 140.0) -> None:  #removed kwargs 
        super().__init__(pos, size, speed)
        self.fear_radius = fear_radius

    def think(self, dt: float, player_pos: Vec2) -> None:      #only passing player pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.fear_radius:
            # flee at full speed
            direction = self._dir_away(player_pos)
            self.vel = direction * self.speed
        else:
            # wander at reduced speed (looks natural)
            direction = self.wander_dir(dt)
            self.vel = direction * (self.speed * 0.6)

    def draw(self, screen: pygame.Surface) -> None:
        # Blue = passive
        super().draw(screen, color=(50, 120, 255))
