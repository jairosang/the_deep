from src.game import GameManager
from src.states.homebase import HomebaseState
from src.states.underwater import UnderwaterState
from src.states.start_screen import StartScreen
from src.entities.player import Player
import config
import pygame

def initialize():
    pygame.init()
    vid_info = pygame.display.Info()
    vid_dimensions = (vid_info.current_w, vid_info.current_h)

    screen = pygame.display.set_mode(vid_dimensions, pygame.FULLSCREEN)
    pygame.display.set_caption(config.GAME_TITLE)

    player = Player()
    states = {
        "START_SCREEN": StartScreen(vid_dimensions),
        "UNDERWATER": UnderwaterState(vid_dimensions, player),
        "HOMEBASE": HomebaseState(vid_dimensions, player),
    }

    return screen, states


if __name__ == "__main__":
    screen, states = initialize()

    GameManager(screen, states, "START_SCREEN").run()