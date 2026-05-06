from abc import ABC, abstractmethod
from pathlib import Path
import pygame
from .base_creature import Creature, Vec2
from utils.animation import Animation
from utils.sprite_sheet import load_frames

class PassiveCreature(Creature, ABC):
    def __init__(self, pos: tuple[float, float], frames: list[pygame.Surface], *, species: str, health: int, thrust: float, mass: float, fear_radius: float, size: int, scan_duration: float, sprint_multiplier: float = 1.4) -> None:

        base = pygame.transform.scale(frames[0], (size, size))

        self.color = (0, 50, 255)

        super().__init__(base, frames, pos, size)

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

