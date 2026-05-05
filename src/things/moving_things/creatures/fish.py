from pathlib import Path
from utils.sprite_sheet import load_frames
from .passive_creature import PassiveCreature

FISH_FRAMES = None


def get_fish_frames():
    global FISH_FRAMES

    if FISH_FRAMES is None:
        FISH_FRAMES = load_frames(Path("assets/sprites/fish.png"), 32, 32, 4,)
    return FISH_FRAMES


class Fish(PassiveCreature):
    def __init__(
        self,
        pos: tuple[float, float],
        size: int = 18,
        fear_radius: float = 200,
    ) -> None:
        super().__init__(
            pos,
            get_fish_frames(),
            species="fish",
            health=25,
            thrust=180,
            mass=15,
            fear_radius=fear_radius,
            size=size,
            scan_duration=4.0,
        )

    def _species_marker(self) -> None:
        pass