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

    screen = pygame.display.set_mode(g_config["SCREEN_SIZE"], pygame.FULLSCREEN)
    pygame.display.set_caption(g_config["GAME_TITLE"])

    player = Player()
    states = {
        "START_SCREEN": StartScreen(vid_info),
        "UNDERWATER": UnderwaterState(vid_info, player),
        "HOMEBASE": HomebaseState(vid_info, player),
        "GAME_OVER": GameOverState(vid_info)
    }

    return screen, states


if __name__ == "__main__":
    screen, states = initialize()

    GameManager(screen, states, "START_SCREEN").run()