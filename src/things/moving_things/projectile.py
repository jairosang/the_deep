from pygame import Surface
import pygame
import utils as phy
from .moving_thing import MovingThing


class Projectile(MovingThing):
    def __init__(self, pos: tuple[int, int], thrust: int, target_pos: tuple[int, int] | None = None, image: Surface | None = None, max_range: float = 64, damage: int = 1) -> None:
        if image is None:
            image = pygame.Surface((4, 4), pygame.SRCALPHA)
            image.fill((100,100,100))
        super().__init__(image, pos)

        direction = pygame.math.Vector2(1, 0)
        if target_pos is not None:
            target = pygame.math.Vector2(target_pos)
            shot = target - pygame.math.Vector2(pos)
            if shot.length_squared() > 0:
                direction = shot.normalize()

        self.velocity = direction * thrust
        self.damage = damage
        self.max_range = max_range
        self.spawn_pos = pygame.math.Vector2(pos)
        self.is_destroyed = False

        angle = -direction.angle_to(pygame.math.Vector2(1, 0))
        current_center = self.rect.center
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=current_center)
        self.pos.update(self.rect.x, self.rect.y)

    # Destructor
    def __del__(self):
        print(f"Destrying projectile at pos: {self.pos}")

    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        if self.is_destroyed:
            return

        self._move_x(dt)
        if phy.get_colliding_tiles(area_tiles, self.rect):
            phy.resolve_map_collision_on_x_axis(self, area_tiles)
            self.velocity.x *= -0.1

        self._move_y(dt)
        if phy.get_colliding_tiles(area_tiles, self.rect):
            phy.resolve_map_collision_on_y_axis(self, area_tiles)
            self.velocity.y *= -0.1

        self._update_velocity(dt)
        self.rect.clamp_ip(bound_rect)
        self.pos.update(self.rect.x, self.rect.y)

        if not bound_rect.colliderect(self.rect):
            self.destroy()
        elif self.velocity.length() <= 20:
            self.destroy()
        
    def destroy(self):
        self.is_destroyed = True