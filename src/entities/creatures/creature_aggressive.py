import pygame
from src.entities.creatures.base_creature import Creature, Vec2

class AggressiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], chase_radius: float = 260.0, **kwargs) -> None:
        super().__init__(pos, **kwargs)
        self.chase_radius = chase_radius

    def think(self, dt: float, player) -> None:
        player_pos = Vec2(player.rect.center)
        dist = self.pos.distance_to(player_pos)

        if dist <= self.chase_radius:
            # chase at full speed
            direction = self._dir_towards(player_pos)
            self.vel = direction * self.speed
        else:
            # patrol/wander at reduced speed
            direction = self.wander_dir(dt)
            self.vel = direction * (self.speed * 0.5)

    def draw(self, screen: pygame.Surface) -> None:
        # Red = hostile
        super().draw(screen, color=(220, 50, 50))