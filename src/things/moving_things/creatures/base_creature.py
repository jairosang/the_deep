from ..moving_thing import MovingThing
from abc import abstractmethod, ABC
import pygame
import random
from utils.sprite_sheet import load_frames
from utils.animation import Animation
from pathlib import Path
Vec2 = pygame.math.Vector2


DEATH_FRAMES = None

def get_death_frames():
    global DEATH_FRAMES
    if DEATH_FRAMES is None:
        DEATH_FRAMES = load_frames(Path("assets/sprites/enemy-death.png"), 52, 53, 6)
    return DEATH_FRAMES


class Creature(MovingThing, ABC):
    def __init__(self, image: pygame.Surface, pos, thrust=90.0):
        super().__init__(image, pos)
        self.color: tuple[int, int, int]

        self.health = 0
        self.max_health = 0

        # for the colour change efffect:
        self.flash_timer = 0.0
        self.flash_duration = 0.2

        # wander behaviour
        self._wander_dir = Vec2(1, 0)
        self._wander_timer = 0.0
        self._wander_interval = random.uniform(0.6, 1.4)

        # death animation 
        self.death_anim = Animation(get_death_frames(), fps=8, loop=False)
        self.is_dying = False  # true once health hits 0, stays True 

    def update(self, dt, bound_rect: pygame.Rect, area_tiles, player_pos):

        if self.is_dying:
            self.death_anim.update(dt)
            return
        
        self.input_direction.x = 0
        self.input_direction.y = 0
        
        self.input_direction = self.think(dt, player_pos)

        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.flash_timer <= 0:
            self.image = self._base_image  # Return to original color/state (For now color until there is an img)

        super().update(dt, bound_rect, area_tiles)

    def draw(self, surface: pygame.Surface):
        if self.is_dying:
            death_frame = pygame.transform.scale(self.death_anim.get_image(), (self.rect.width, self.rect.height))
            surface.blit(death_frame, self.rect)
        else:
            surface.blit(self.image, self.rect)

        
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
    
    def get_damaged(self, amount):
        self.health -= amount
        tinted = self._base_image.copy()
        tinted.fill((180, 0, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.image = tinted    # red tint on hit

    def is_dead(self):
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.death_anim.reset()
        return self.is_dying and self.death_anim.finished