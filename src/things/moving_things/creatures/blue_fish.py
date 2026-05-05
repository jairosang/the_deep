from pathlib import Path
import pygame
from .fish import get_fish_frames
from .passive_creature import PassiveCreature


BLUE_FISH_FRAMES = None


def get_blue_fish_frames():
    global BLUE_FISH_FRAMES

    if BLUE_FISH_FRAMES is None:
        path = Path("assets/sprites/blue-fish.png")

        if path.exists():
            first_frame = pygame.image.load(path).convert_alpha()
            first_frame = first_frame.subsurface((0, 0, 512, 512))

            frames = [first_frame, first_frame, first_frame, first_frame,]

            cleaned_frames = []

            for frame in frames:
                frame = frame.copy().convert_alpha()

                for x in range(frame.get_width()):
                    for y in range(frame.get_height()):
                        r, g, b, a = frame.get_at((x, y))

                        if r > 240 and g > 240 and b > 240:
                            frame.set_at((x, y), (0, 0, 0, 0))

                cleaned_frames.append(frame)

            BLUE_FISH_FRAMES = cleaned_frames
        else:
            BLUE_FISH_FRAMES = get_fish_frames()

    return BLUE_FISH_FRAMES


class BlueFish(PassiveCreature):
    def __init__(
        self,
        pos: tuple[float, float],
        size: int = 26,
        fear_radius: float = 220,
    ) -> None:
        super().__init__(
            pos,
            get_blue_fish_frames(),
            species="blue-fish",
            health=35,
            thrust=150,
            mass=22,
            fear_radius=fear_radius,
            size=size,
            scan_duration=5.0,
        )

    def _species_marker(self) -> None:
        pass