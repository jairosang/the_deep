import pygame
from src.entities.creatures.base_creature import Creature, Vec2

class PassiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], fear_radius: float = 150.0, **kwargs) -> None:
        super().__init__(pos, **kwargs)
        self.fear_radius = fear_radius

    def think(self, dt: float, player) -> None:
        player_pos = Vec2(player.rect.center)
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
