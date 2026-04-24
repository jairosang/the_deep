from .moving_thing import MovingThing
from ..items.item import Item
from ..holdables.base_holdable import Holdable
from config import game as g_config, player as p_config
import pygame
from pathlib import Path
from utils.sprite_sheet import load_frames
from utils.animation import Animation

SPRITES = Path("assets/sprites")

class Player(MovingThing):
    def __init__(self) -> None:
        super().__init__(pygame.Surface(p_config["SIZE"]))
        # THIS IS    no longer    TEMPORARY

        self.anim_idle    = Animation(load_frames(SPRITES / "player-idle.png",    80, 80, 6), fps=6)
        self.anim_swim    = Animation(load_frames(SPRITES / "player-swiming.png", 80, 80, 7), fps=8)
        self.anim_fast    = Animation(load_frames(SPRITES / "player-fast.png",    80, 80, 5), fps=10)
        self.anim_rush    = Animation(load_frames(SPRITES / "player-rush.png",    80, 80, 7), fps=10)
        self.anim_hurt    = Animation(load_frames(SPRITES / "player-hurt.png",    80, 80, 5), fps=8, loop=False)
 
        self._current_anim = self.anim_idle
        self._base_image = self._current_anim.get_image()
        self.image = self._base_image

        self.rect = pygame.Rect(0, 0, 16, 40)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Movement
        self.thrust = p_config["THRUST"]
        self.mass = p_config["MASS"]
        self.input_direction = pygame.math.Vector2(0, 0)
        self.is_sprinting = False
        self.sprint_multiplier = p_config["SPRINT_MULTIPLIER"]
        self.movement_axis = pygame.math.Vector2(1, 1)  # (x, y) 1 allows the p_config to move on that axis

        # Stats (FOR NOW PULLS BASE DATA FROM CONFIG, WHEN THERE IS PERSISTANCE THIS SHOULD BE PULLED FROM THE DATA MANAGER WHICH WILL DETERMINE IF TO USE BASE STATS OR LOADED STATS)
        self.health = p_config["BASE_STATS"]["MAX_HEALTH"]
        self.max_health = p_config["BASE_STATS"]["MAX_HEALTH"]
        self.oxygen = p_config["BASE_STATS"]["MAX_OXYGEN"]
        self.max_oxygen = p_config["BASE_STATS"]["MAX_OXYGEN"]
        self.oxygen_depletion_rate = p_config["BASE_STATS"]["OXYGEN_DEPLETION_RATE"]
        self.depth: float = 0.0
        self.max_depth_limit = p_config["BASE_STATS"]["MAX_DEPTH_LIMIT"]
        self.buffer_inventory:list[Item] = []
        self.buffer_inventory_capacity = p_config["BASE_STATS"]["INVENTORY_CAPACITY"]
        self.inventory: dict[str, int] = {} #intended to store a thing and the amount of that thing
        self.current_holdable: Holdable | None = None
        # Missing harpoon, weapon and research gun

    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        super().update(dt, bound_rect, area_tiles)
        if self.current_holdable is not None:
            self.current_holdable.update(dt, bound_rect, self.rect.center)
        self._update_oxygen()
        self.update_animation(dt)


    def update_animation(self, dt):
        speed = self.velocity.length()
 
        # hurt animation plays until finished, then it goes back to normal
        if self._current_anim is self.anim_hurt and not self.anim_hurt.finished:
            pass
        elif speed < 1:
            self._current_anim = self.anim_idle
        elif self.is_sprinting and speed > 80:
            self._current_anim = self.anim_rush
        elif self.is_sprinting:
            self._current_anim = self.anim_fast
        else:
            self._current_anim = self.anim_swim
 
        self._current_anim.update(dt)
        self._base_image = self._current_anim.get_image()
        self.image = self._base_image

        if self.velocity.length_squared() > 0:
            # removed the logic we had before, added new one so we snap to a direction every 15 degrees.
            # get the angle of movement, snap it to nearest 15 degrees.
            angle = self.velocity.angle_to(pygame.math.Vector2(1, 0)) 
            snapped = round(angle / 15) * 15
            self.image = pygame.transform.rotate(self._base_image.convert_alpha(), snapped)
            self._update_hitbox(snapped)
        else:
            self._update_hitbox(None)



    def handle_inputs(self, keys, mouse_pos: tuple[int, int] | None = None):
        self.input_direction.x = 0
        self.input_direction.y = 0

        if keys[pygame.K_w]:
            self.input_direction.y = -1
        if keys[pygame.K_s]:
            self.input_direction.y = 1
        if keys[pygame.K_a]:
            self.input_direction.x = -1
        if keys[pygame.K_d]:
            self.input_direction.x = 1

        self.is_sprinting = keys[pygame.K_SPACE]

        # Removes movement on axis if its turned off
        self.input_direction.x *= self.movement_axis.x
        self.input_direction.y *= self.movement_axis.y

        if self.input_direction.length_squared() > 0:
            self.input_direction = self.input_direction.normalize()

        if self.current_holdable is not None and mouse_pos is not None:
            self.current_holdable.handle_inputs(mouse_pos)

    def set_holdable(self, holdable: Holdable | None) -> None:
        self.current_holdable = holdable

    def _update_hitbox(self, angle):
        old_center = self.rect.center
        # Keep a consistent collision rect size to prevent camera jitter
        # The sprite rotation doesn't need to change the actual hitbox
        self.rect.size = (32, 32)
        self.rect.center = old_center

    def draw(self, surface: pygame.Surface):
        # Draw sprite centered on collision rect center
        image_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, image_rect)
        if self.velocity.length_squared() > 0: 
            center = pygame.math.Vector2(self.rect.center)
            velocity_scaled = self.velocity / 15    # Controls how far the arrow extends

            dir_v = velocity_scaled.normalize()
            radius = 40       # Fixed radius instead of using rect.height
            end_point = center + velocity_scaled + dir_v * radius
            
            # Drawing an arc in the direction of velocity
            arc_points = []
            for angle in range(-20, 21, 3): # Controls how wide the arc is
                arc_points.append(center + dir_v.rotate(angle) * (radius * 0.95))
            if len(arc_points) > 1:
                pygame.draw.lines(surface, (60, 108, 153), False, arc_points, 2)
            
            # Draw arrow
            pygame.draw.polygon(surface, (60, 108, 153), [end_point] + arc_points[4:-4])

        if self.current_holdable is not None:
            self.current_holdable.draw(surface)
                    

    def _update_oxygen(self):
        # This thing will have implemented the game over thing when the oxygen is 0
        if self.oxygen <= 0:
            pass

        # This is the thing that checks how to update the oxygen thing if you are sprinting or not
        if self.oxygen > 0:
            if self.is_sprinting == False:
                self.oxygen -= self.oxygen_depletion_rate/g_config["FPS"]
            if self.is_sprinting == True:
                self.oxygen -= self.oxygen_depletion_rate*2/g_config["FPS"]
        # You have to divide the thing by the FPS to not have it go crazy ofc

    def update_depth_damage(self):
        pass

    def heal(self):
        pass

    def interact(self):
        pass

    def revert(self):
        self.velocity *= 0
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.health = self.max_health
        self.oxygen = self.max_oxygen

    def get_damaged(self, ammt):
        self.health -= ammt
        self.anim_hurt.reset()
        self._current_anim = self.anim_hurt