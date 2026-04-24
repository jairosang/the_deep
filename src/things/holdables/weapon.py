from .base_holdable import Holdable
from pathlib import Path

class Weapon(Holdable):
    def __init__(self) -> None:
        self.name = "Weapon"
        self.description = "Ranged weapon against hostile creatures"    # short text, kept for menus for later
        self.color = (200, 60, 60)
        self.image_path = Path("./assets/holdables/weapon_asset.png")
        self.damage = 5
        self.ammo = 5
        self.range = 64
        self.cooldown_s = 1
        self.is_available = False

        super().__init__()

    def shoot(self, pos: tuple[int, int]):
        return 
    # Must spawn a projectile