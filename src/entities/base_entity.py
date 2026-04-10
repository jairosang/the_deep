from abc import ABC, abstractmethod
import pygame

class Entity(ABC):
    def __init__(self, image: pygame.Surface, pos: tuple[int, int] = (0,0)) -> None:
        self.image = image
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

        # the physical attributes, can be overwritten later
        self.velocity = pygame.math.Vector2(0, 0)
        self.mass = 0
        self.thrust = 0
    @abstractmethod
    def update(self, dt, bound_rect: pygame.Rect):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass
