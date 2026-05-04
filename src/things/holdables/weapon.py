from .base_holdable import Holdable
from ..shootables.projectile import Projectile
from pathlib import Path
import utils as phy

class Weapon(Holdable):
    def __init__(self) -> None:
        self.name = "Weapon"
        self.description = "Ranged weapon against hostile creatures"
        self.color = (200, 60, 60)
        self.image_path = Path("./assets/holdables/weapon_asset.png")
        self.damage = 10
        self.ammo = 10
        self.range = 500
        self.cooldown_s = 0.5
        self.shoot_recoil = 30
        self.is_available = False
        self.shot_dt = 0.0
        self.thrust = 500
        self.shot_cycle_max = 1
        super().__init__()

    def update(self, dt, bound_rect, player_pos) -> None:
        self.shot_dt += dt
        super().update(dt, bound_rect, player_pos)

    def update_shootables(self, dt: float, creatures: list, world_rect=None, get_tiles=None) -> tuple[list, list]:
        if world_rect and get_tiles:
            for s in self.shootables:
                area_tiles = get_tiles(s.rect.centerx, s.rect.centery, (5, 5))
                s.update(dt, world_rect, area_tiles)
        return phy.resolve_projectile_creature_collisions(self.get_shootables(), creatures)

    def shoot(self, pos: tuple[int, int]) -> bool:
        if self.shot_dt < self.cooldown_s:
            return False
        self.shot_dt = 0.0
        self.shootables.append(Projectile(self.rect.center, self.thrust, target_pos=pos, max_range=self.range, damage=self.damage))
        return True

    def draw(self, surface) -> None:
        super().draw(surface)

    def draw_things_on_screen(self, surface):
        for projectile in self.shootables:
            projectile.draw(surface)
