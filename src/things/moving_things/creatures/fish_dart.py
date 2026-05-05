from pathlib import Path

from utils.sprite_sheet import load_frames
from .aggressive_creature import AggressiveCreature


FISH_DART_FRAMES = None


def get_fish_dart_frames():
    global FISH_DART_FRAMES

    if FISH_DART_FRAMES is None:
        FISH_DART_FRAMES = load_frames(Path("assets/sprites/fish-dart.png"), 39, 20, 4,)

    return FISH_DART_FRAMES


class FishDart(AggressiveCreature):
    def __init__(
        self,
        pos: tuple[float, float],
        size: int = 22,
        chase_radius: float = 220,
    ) -> None:
        super().__init__(
            pos,
            get_fish_dart_frames(),
            species="fish-dart",
            health=20,
            damage=5,
            thrust=220,
            mass=20,
            chase_radius=chase_radius,
            size=size,
            scan_duration=5.0,
            # sprint_multiplier=1.5,
        )

    def _species_marker(self) -> None:
        pass