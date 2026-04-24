from .base_holdable import Holdable

class Harpoon(Holdable):
    def __init__(self) -> None:
        self.name = "Harpoon"
        self.description = "Fast projectile for close range defense and gathering"
        self.color = (80, 160, 220)
        self.image_path = None
        self.projectile_speed = 1.5
        self.range = 96
        self.cooldown_s = 0.5
        self.is_available = False

        super().__init__()

    def shoot(self, pos: tuple[int, int]) -> None:
        pass