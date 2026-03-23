from abc import ABC,abstractmethod
import pygame

class BaseState(ABC):
    def __init__(self) -> None:
        self.is_done: tuple[bool, None|str] = (False, None)
        self.is_quitting = False

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def handle_event(self, e: pygame.event.Event):
        pass
        
    @abstractmethod
    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self, screen, is_debug_on):
        pass

    @abstractmethod
    def exit(self):
        pass