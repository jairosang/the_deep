from src.game import GameManager
from src.states.homebase import HomebaseState
from src.states.underwater import UnderwaterState
from src.states.start_screen import StartScreen
import pygame

def initialize():
    pygame.init()
    pygame_info = pygame.display.Info()
    screen = pygame.display.set_mode((pygame_info.current_w, pygame_info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("The Deep")

    states = {
        "START_SCREEN": StartScreen((pygame_info.current_w, pygame_info.current_h)),
        "UNDERWATER": UnderwaterState((pygame_info.current_w, pygame_info.current_h)),
        "HOMEBASE": HomebaseState((pygame_info.current_w, pygame_info.current_h)),
    }

    return screen, states


if __name__ == "__main__":
    screen, states = initialize()

    GameManager(screen, states, "START_SCREEN").run()