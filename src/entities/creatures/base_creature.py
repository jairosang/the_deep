import pygame
import random
from abc import abstractmethod, ABC
from src.entities.base_moving_thing import MovingThing
import src.utils.physics_service as phy
from config import game as g_config
Vec2 = pygame.math.Vector2

class Creature(MovingThing, ABC):
    def __init__(self, image: pygame.Surface, pos, thrust=90.0):
        super().__init__(image, pos)

        # wander behaviour
        self._wander_dir = Vec2(1, 0)
        self._wander_timer = 0.0
        self._wander_interval = random.uniform(0.6, 1.4)

    def update(self, dt, bound_rect: pygame.Rect, area_tiles, player_pos):
        self.input_direction.x = 0
        self.input_direction.y = 0
        
        self.input_direction = self.think(dt, player_pos)

        super().update(dt, bound_rect, area_tiles)
        
    @abstractmethod
    def think(self, dt: float, player_pos:Vec2) -> Vec2:    #changed to an abstract class, the subclass must implement this
        pass

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