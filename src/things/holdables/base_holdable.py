from abc import ABC, abstractmethod
from ..thing import Thing
from pathlib import Path
import math
import pygame

class Holdable(Thing, ABC):
    continuous: bool = False  # if True keeps shooting while left click is held
    is_available: bool
    name: str
    description: str
    color: tuple[int, int, int]
    image_path: Path | None
    range: float
    cooldown_s: float
    shoot_recoil: int

    def __init__(self) -> None:
        self.image_path: Path | None = getattr(self, "image_path", None)
        self._is_active = False
        self._is_left_click_down = False
        self._last_mouse_pos: tuple[int, int] | None = None
        self.aim_direction = pygame.math.Vector2(1, 0)
        self.orbit_radius = 25
        self.is_already_shot = False
        self.shootables: list = []

        if self.image_path is not None:
            loaded = pygame.image.load(str(self.image_path)).convert_alpha()
            loaded.set_colorkey((0, 0, 0))
            self.image = loaded
        else:
            self.image = pygame.Surface((16, 16))
            self.image.fill((255, 255, 255))

        self.base_image = self.image.copy()
        super().__init__(self.image)
        self.player_center = pygame.math.Vector2(self.rect.center)

    @property
    def is_active(self) -> bool:
        if self.continuous:
            return self._is_left_click_down
        return self._is_active

    @is_active.setter
    def is_active(self, val: bool) -> None:
        self._is_active = val

    def get_shootables(self) -> list:
        return self.shootables

    def remove_shootables(self, to_remove: list) -> None:
        for s in to_remove:
            if s in self.shootables:
                self.shootables.remove(s)

    @property
    def get_image(self) -> pygame.Surface:
        return self.image

    @abstractmethod
    def shoot(self, pos: tuple[int, int]) -> bool:
        pass

    def update(self, dt, bound_rect: pygame.Rect, player_pos) -> None:
        self.player_center.update(player_pos)

        if self._last_mouse_pos is not None and self.continuous == True:
            self._update_aim(self._last_mouse_pos)

        holdable_center = self.player_center + self.aim_direction * self.orbit_radius
        self.rect.center = (int(holdable_center.x), int(holdable_center.y))
        if bound_rect is not None:
            self.rect.clamp_ip(bound_rect)

        angle = -math.degrees(math.atan2(self.aim_direction.y, self.aim_direction.x))
        angle = angle if self.aim_direction.x > 0 else angle * -1
        rotated_image = pygame.transform.rotate(self.base_image, angle)
        if self.aim_direction.x < 0:
            rotated_image = pygame.transform.flip(rotated_image, False, True)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos.update(self.rect.x, self.rect.y)


    # I know this is wrong because I will just keep adding arguments for all the classes that need them but it's too late to refactor now :()
    @abstractmethod
    def update_shootables(self, dt: float, creatures: list, world_rect=None, get_tiles=None) -> tuple[list, list]:
        pass

    def draw(self, surface) -> None:
        surface.blit(self.image, self.rect)

    # Optional function to print projectiles or other things spawned by the holdable
    def draw_things_on_screen(self, surface):
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._on_left_click_down()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._on_left_click_up()
        return False

    def reset_input_state(self) -> None:
        self._is_left_click_down = False
        self._last_mouse_pos = None

    def _on_left_click_down(self) -> bool:
        self._is_left_click_down = True
        if self._last_mouse_pos:
            self._update_aim(self._last_mouse_pos)
            fired = self.shoot(self._last_mouse_pos)
            if fired and not self.continuous:
                self.is_already_shot = True
            return fired
        return False

    def _on_left_click_up(self) -> None:
        self._is_left_click_down = False
        self.is_already_shot = False

    def _update_aim(self, mouse_pos: tuple[int, int]) -> None:
        aim_vec = pygame.math.Vector2(mouse_pos) - self.player_center
        if aim_vec.length_squared() > 0:
            self.aim_direction = aim_vec.normalize()