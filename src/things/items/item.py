import pygame

class Item():
    def __init__(self, pos, name = "creature_loot") -> None:
        self.name = name
        self.pos = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), 18, 18)
        self.pickup_timer = 2.0 # time before being able to pick up item

    def interact(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 120, 120), self.rect)