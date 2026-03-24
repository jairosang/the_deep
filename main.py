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
    vid_info = pygame.display.Info()
    g_config["SCREEN_SIZE"] = (vid_info.current_w, vid_info.current_h)

    screen = pygame.display.set_mode(g_config["SCREEN_SIZE"], pygame.SCALED + pygame.NOFRAME + pygame.FULLSCREEN, 32, vsync=1)
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