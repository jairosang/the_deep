from abc import ABC, abstractmethod
from pathlib import Path
import pygame
from .base_creature import Creature, Vec2
from utils.animation import Animation
from utils.sprite_sheet import load_frames

class AggressiveCreature(Creature, ABC):
    def __init__(self, pos: tuple[float, float], frames: list[pygame.Surface], *, species: str, health: int, damage: int, thrust: float, mass: float, chase_radius: float, size: int, scan_duration: float, sprint_multiplier: float = 1.3, flip_sprite: bool = False) -> None: #also removed kwargs
    
        base = pygame.transform.scale(frames[0], (size, size))

        super().__init__(base, frames, pos, size)

        if flip_sprite:
            frames = [pygame.transform.flip(frame, True, False) for frame in frames]

        
        self.chase_radius = chase_radius
        self.mass = mass
        self.thrust = thrust
        self.damage = damage
        self.is_sprinting = False
        self.sprint_multiplier = sprint_multiplier
        self.health = health
        self.max_health = health
        self.species = species
        self.scan_duration = scan_duration

    @abstractmethod
    def _species_marker(self) -> None:
        # keeps AggressiveCreature abstract so only real species are spawned
        pass

    def think(self, dt: float, player_pos) -> Vec2:                             #is now only passing player_pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.chase_radius:
            # chase at full speed
            self.is_sprinting = True
            return self._dir_towards(player_pos)
        else:
            # patrol/wander at half thrust
            self.is_sprinting = False
            return self.wander_dir(dt)
