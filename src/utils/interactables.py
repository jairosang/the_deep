from abc import ABC, abstractmethod
import pygame

class Interactable(ABC):
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.rect = pygame.Rect(x - width/2, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    @abstractmethod
    def interact(self) -> None:
        pass

class Exit(Interactable):
    def interact(self) -> None:
        pass

class Upgrades(Interactable):
    def interact(self) -> None:
        pass

class Research(Interactable):
    def interact(self) -> None:
        pass

