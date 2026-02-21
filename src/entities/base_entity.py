from abc import ABC, abstractmethod
import pygame

class Entity(ABC):
    def __init__(self, image: pygame.Surface, pos: tuple[int, int]) -> None:
        self.image = image
        self.pos = pygame.math.Vector2(pos)
        self.rect: pygame.Rect

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass
