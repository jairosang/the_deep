from abc import ABC, abstractmethod
import pygame


class BaseMenu(ABC):
    # Shared interface for any in-game menu that can be opened/closed
    def __init__(self) -> None:
        self.is_open: bool = False

    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def handle_event(self, e: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass
