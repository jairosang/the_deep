from .base_holdable import Holdable
from ..moving_things.projectile import Projectile
from pathlib import Path
import utils as phy

class Weapon(Holdable):
    def __init__(self) -> None:
        self.name = "Weapon"
        self.description = "Ranged weapon against hostile creatures"    # short text, kept for menus for later
        self.color = (200, 60, 60)
        self.image_path = Path("./assets/holdables/weapon_asset.png")
        self.damage = 10
        self.ammo = 10 # Not used for now
        self.range = 500
        self.cooldown_s = 0.5
        self.shoot_recoil = 200
        self.is_available = False
        self.projectiles = []
        self.shot_dt = 0.0

        self.thrust = 500 # Must be configurable later on so upgrades increase it, it will increase the speed of the projectiles
        super().__init__()

    def update(self, dt, bound_rect, player_pos) -> None:
        self.shot_dt += dt
        super().update(dt, bound_rect, player_pos)

    def shoot(self, pos: tuple[int, int]) -> bool:
        if self.shot_dt < self.cooldown_s:
            return False

        self.shot_dt = 0.0
        spawn_pos = self.rect.center
        self.projectiles.append(Projectile(spawn_pos, self.thrust, target_pos=pos, max_range=self.range, damage=self.damage))
        return True

    def get_projectiles(self) -> list[Projectile]:
        return self.projectiles

    def remove_projectiles(self, projectiles: list[Projectile]):
        for p in projectiles:
            self.projectiles.remove(p)

    def draw(self, surface) -> None:
        super().draw(surface)

    def draw_things_on_screen(self, surface):
        for projectile in self.projectiles:
            projectile.draw(surface)
         
    # Must spawn a projectile