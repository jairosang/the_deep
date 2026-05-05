from pathlib import Path

from utils.sprite_sheet import load_frames
from .aggressive_creature import AggressiveCreature


FISH_BIG_FRAMES = None


def get_fish_big_frames():
    global FISH_BIG_FRAMES

    if FISH_BIG_FRAMES is None:
        FISH_BIG_FRAMES = load_frames(Path("assets/sprites/fish-big.png"), 54, 49, 4,)

    return FISH_BIG_FRAMES


class FishBig(AggressiveCreature):
    def __init__(
        self,
        pos: tuple[float, float],
        size: int = 26,
        chase_radius: float = 200,
    ) -> None:
        super().__init__(
            pos,
            get_fish_big_frames(),
            species="fish-big",
            health=40,
            damage=10,
            thrust=150,
            mass=35,
            chase_radius=chase_radius,
            size=size,
            scan_duration=6.0,
        )

    def _species_marker(self) -> None:
        pass