import pygame

Vec2 = pygame.math.Vector2

class Creature:
    def __init__(self, pos: tuple[float, float], size: int = 20) -> None:
        self.pos = Vec2(pos)
        self.size = size
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), size, size)

    def update(self, dt: float) -> None:
        # no movement yet
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (30, 30, 30), self.rect)