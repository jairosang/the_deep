import pygame
import random
from abc import ABC,abstractmethod
Vec2 = pygame.math.Vector2

class Creature(ABC):
    def __init__(self, pos: tuple[float, float], size: int = 20, speed: float = 90.0) -> None:
        self.pos = Vec2(pos)
        self.vel = Vec2(0, 0)

        self.size = size
        self.speed = speed
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), size, size)

        # wander behaviour
        self._wander_dir = Vec2(1, 0)
        self._wander_timer = 0.0
        self._wander_interval = random.uniform(0.6, 1.4)

    def update(self, dt: float, player_pos, bounds: pygame.Rect | None = None) -> None:
        self.think(dt, player_pos)

        self.pos += self.vel * dt

        if bounds is not None:
        # stay within the screen
            self.pos.x = max(bounds.left, min(self.pos.x, bounds.right - self.size))
            self.pos.y = max(bounds.top,  min(self.pos.y, bounds.bottom - self.size))

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
    @abstractmethod
    def think(self, dt: float, player_pos:Vec2) -> None:    #changed to an abstract class, the subclass must implement this
        pass

    def distance_to_player(self, player) -> float:
        return self.pos.distance_to(self._player_pos(player))

    def _dir_towards(self, target: Vec2) -> Vec2:
        d = target - self.pos
        if d.length_squared() == 0:
            return Vec2(0, 0)
        return d.normalize()
    
    def _dir_away(self, target: Vec2) -> Vec2:
        d = self.pos - target
        if d.length_squared() == 0:
            return Vec2(0, 0)
        return d.normalize()
    
    def wander_dir(self, dt: float) -> Vec2:
        #Returns a changing random direction
        self._wander_timer += dt
        if self._wander_timer >= self._wander_interval:
            self._wander_timer = 0.0
            self._wander_interval = random.uniform(0.6, 1.4)

            self._wander_dir = Vec2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self._wander_dir.length_squared() == 0:
                self._wander_dir = Vec2(1, 0)
            else:
                self._wander_dir = self._wander_dir.normalize()

        return self._wander_dir

    def draw(self, screen: pygame.Surface, color=(30, 30, 30)) -> None:
        pygame.draw.rect(screen, color, self.rect)