import pygame

GAME_FONT_NAME = "Comic Sans MS"

cache: dict[tuple[int, bool], pygame.font.Font] = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in cache:
        cache[key] = pygame.font.SysFont(GAME_FONT_NAME, size, bold=bold)
    return cache[key]
