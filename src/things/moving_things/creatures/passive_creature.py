from abc import ABC, abstractmethod
from pathlib import Path
import pygame
from .base_creature import Creature, Vec2
from utils.animation import Animation
from utils.sprite_sheet import load_frames

class PassiveCreature(Creature, ABC):
    def __init__(
        self,
        pos: tuple[float, float],
        frames: list[pygame.Surface],
        *,
        species: str,
        health: int,
        thrust: float,
        mass: float,
        fear_radius: float,
        size: int,
        scan_duration: float,
        sprint_multiplier: float = 1.4,
    ) -> None:

        base = pygame.transform.scale(frames[0], (size, size))
        super().__init__(base, pos)

        self.color = (0, 50, 255)

        scaled_frames = [
            pygame.transform.scale(frame, (size, size))
            for frame in frames
        ]
        self.anim = Animation(scaled_frames, fps=8)

        white = pygame.Surface((size, size))
        white.fill((250, 250, 250))
        white.set_alpha(120)
        self._white_flash_image = white

        self._base_image = self.anim.get_image()  # updated each frame
        self.image = self._base_image

        self.fear_radius = fear_radius
        self.mass = mass
        self.thrust = thrust
        self.damage = 0
        self.is_sprinting = False
        self.sprint_multiplier = sprint_multiplier
        self.health = health
        self.max_health = health
        self.species = species
        self.scan_duration = scan_duration

    @abstractmethod
    def _species_marker(self) -> None:
        # keeps PassiveCreature abstract so only real species are spawned
        pass

    def think(self, dt: float, player_pos: Vec2) -> Vec2:      #only passing player pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.fear_radius:
            # flee at full speed
            self.is_sprinting = True
            return self._dir_away(player_pos)
        else:
            # wander at reduced speed (looks natural)
            self.is_sprinting = False
            return self.wander_dir(dt)
        
    def update(self, dt, bound_rect, area_tiles, player_pos):
        if not self.is_dying:
            self.anim.update(dt)
            self._base_image = self.anim.get_image()
            if self.velocity.x < 0:
                self._base_image = pygame.transform.flip(self._base_image, True, False)
        super().update(dt, bound_rect, area_tiles, player_pos)
