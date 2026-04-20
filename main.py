from config import game as g_config
from pathlib import Path
import pygame
import sys

# Removing src from imports within src
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from game import GameManager
from states import GameOverState, HomebaseState, StartScreen, UnderwaterState
from things import Player

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
        "GAME_OVER": GameOverState()
    }

    return screen, states


if __name__ == "__main__":
    screen, states = initialize()

    GameManager(screen, states, "START_SCREEN").run()