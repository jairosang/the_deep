from abc import ABC,abstractmethod
import pygame

class BaseState(ABC):
    def __init__(self, screen_size) -> None:
        self.screen_size = screen_size
        self.is_done: tuple[bool, None|str] = (False, None)
        self.is_quitting = False

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def handle_event(self, e: pygame.event.Event):
        pass
        
    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def exit(self):
        pass