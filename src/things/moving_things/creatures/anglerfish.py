from pathlib import Path

from utils.sprite_sheet import load_frames
from .aggressive_creature import AggressiveCreature
from .fish_big import get_fish_big_frames


ANGLERFISH_FRAMES = None


def get_anglerfish_frames():
    global ANGLERFISH_FRAMES

    if ANGLERFISH_FRAMES is None:
        path = Path("assets/sprites/anglerfish.png")

        if path.exists():
            ANGLERFISH_FRAMES = load_frames(path, 350, 350, 4)
        else:
            ANGLERFISH_FRAMES = get_fish_big_frames()

    return ANGLERFISH_FRAMES


class Anglerfish(AggressiveCreature):
    def __init__(
        self,
        pos: tuple[float, float],
        size: int = 30,
        chase_radius: float = 240,
    ) -> None:
        super().__init__(
            pos,
            get_anglerfish_frames(),
            species="anglerfish",
            health=60,
            damage=15,
            thrust=130,
            mass=50,
            chase_radius=chase_radius,
            size=size,
            scan_duration=8.0,
            # sprint_multiplier=1.2,
            flip_sprite=True,
        )

    def _species_marker(self) -> None:
        pass