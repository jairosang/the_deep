import pygame

class Item():
    def __init__(self, pos) -> None:
        self.pos = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), 18, 18)

    def interact(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 120, 120), self.rect)