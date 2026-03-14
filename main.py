from src.game import GameManager
from src.states.homebase import HomebaseState
from src.states.underwater import UnderwaterState
from src.states.start_screen import StartScreen
from src.states.game_over import GameOverState
from src.entities.player import Player
from config import game as g_config
import pygame

def initialize():
    pygame.init()
    # (0,0) lets pygame pick the native resolution, then get_size() reads the actual size.
    # Avoids display artifacts caused by resolution mismatch when using display.Info() before set_mode.
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    g_config["SCREEN_SIZE"] = screen.get_size()
    pygame.display.set_caption(g_config["GAME_TITLE"])

    player = Player()
    states = {
        "START_SCREEN": StartScreen(),
        "UNDERWATER": UnderwaterState(player),
        "HOMEBASE": HomebaseState(player),
        #"GAME_OVER": GameOverState()
    }

    return screen, states


if __name__ == "__main__":
    screen, states = initialize()

    GameManager(screen, states, "START_SCREEN").run()