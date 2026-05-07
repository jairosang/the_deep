import pygame
from config import game as g_config

cache: dict[tuple[int, str, bool], pygame.font.Font] = {}

def get_font(size: int, font_type: str = "primary", bold: bool = False) -> pygame.font.Font:
    # Font type primary or secondary
    key = (size, font_type, bold)
    if key not in cache:
        if font_type == "primary":
            font = pygame.font.Font(str(g_config["PRIMARY_FONT"]), size)
            if bold:
                font.set_bold(True)
            cache[key] = font
        elif font_type == "secondary":
            font = pygame.font.Font(str(g_config["SECONDARY_FONT"]), size)
            if bold:
                font.set_bold(True)
            cache[key] = font
    return cache[key]
