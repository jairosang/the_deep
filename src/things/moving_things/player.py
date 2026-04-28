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

        self.animations = {
            "idle": Animation(load_frames(SPRITES / "player-idle.png", 80, 80, 6), fps=6),
            "swim": Animation(load_frames(SPRITES / "player-swiming.png", 80, 80, 7), fps=8),
            "fast": Animation(load_frames(SPRITES / "player-fast.png", 80, 80, 5), fps=10),
            "rush": Animation(load_frames(SPRITES / "player-rush.png", 80, 80, 7), fps=10),
            "hurt": Animation(load_frames(SPRITES / "player-hurt.png", 80, 80, 5), fps=8, loop=False),
            "shoot": Animation(load_frames(SPRITES / "player-shoot.png", 80, 80, 6), fps=8, loop=False),
            "walk": Animation(load_frames(SPRITES / "player-walk.png", 80, 80, 4), fps=8, loop=False)
        }
 
        self._current_anim = self.animations["idle"]
        self._base_image = self._current_anim.get_image()
        self.image = self._base_image

        self.rect = pygame.Rect(0, 0, 16, 40)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Movement
        self.thrust = p_config["THRUST"]
        self.mass = p_config["MASS"]
        self.input_direction = pygame.math.Vector2(0, 0)
        self._shoot_facing_vector: pygame.math.Vector2 | None = None
        self.is_sprinting = False
        self.sprint_multiplier = p_config["SPRINT_MULTIPLIER"]
        self.movement_axis = pygame.math.Vector2(1, 1)  # (x, y) 1 allows the p_config to move on that axis
        self._movement_keys = {
            pygame.K_w: False,
            pygame.K_a: False,
            pygame.K_s: False,
            pygame.K_d: False,
        }

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
        self._left_click_pressed: bool = False

        # for the colour change efffect:
        self.flash_timer = 0.0
        self.flash_duration = 0.4

    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.flash_timer <= 0:
            self.image = self._base_image  # Return to original color/state (For now color until there is an img)

        super().update(dt, bound_rect, area_tiles)
        if self.current_holdable is not None:
            self.current_holdable.update(dt, bound_rect, self.rect.center)
        self._update_oxygen()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in self._movement_keys:
                self._movement_keys[event.key] = True
                self._refresh_input_direction()
            elif event.key == pygame.K_SPACE:
                self.is_sprinting = True
        elif event.type == pygame.KEYUP:
            if event.key in self._movement_keys:
                self._movement_keys[event.key] = False
                self._refresh_input_direction()
            elif event.key == pygame.K_SPACE:
                self.is_sprinting = False

        if self.current_holdable is not None and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            holdable = self.current_holdable
            fired = holdable.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and holdable._last_mouse_pos:
                self._left_click_pressed = True
                aim_vector = pygame.math.Vector2(holdable._last_mouse_pos) - pygame.math.Vector2(self.rect.center)
                if aim_vector.length_squared() > 0:
                    self._shoot_facing_vector = aim_vector
                elif self.velocity.length_squared() > 0:
                    self._shoot_facing_vector = self.velocity.copy()
                else:
                    self._shoot_facing_vector = pygame.math.Vector2(1, 0)

                should_start_anim = fired or holdable.continuous
                if should_start_anim:
                    if not holdable.continuous:
                        holdable.is_active = True

                    self.animations["shoot"].reset()
                    self._current_anim = self.animations["shoot"]
                    self._base_image = self._current_anim.get_image()
                    self._apply_facing_rotation(self._shoot_facing_vector)

                    # Recoil Mechanics
                    recoil_direction = self._shoot_facing_vector.normalize()
                    self.velocity -= recoil_direction * holdable.shoot_recoil

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._left_click_pressed = False

    def draw(self, surface: pygame.Surface):
        # Draw sprite centered on collision rect center
        image_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, image_rect)
        # COMMENTED OUT TO TEST USING THE ARROW FOR SHOOTING
        # if self.velocity.length_squared() > 0: 
        #     center = pygame.math.Vector2(self.rect.center)
        #     velocity_scaled = self.velocity / 15    # Controls how far the arrow extends

        #     dir_v = velocity_scaled.normalize()
        #     radius = 40       # Fixed radius instead of using rect.height
        #     end_point = center + velocity_scaled + dir_v * radius
            
        #     # Drawing an arc in the direction of velocity
        #     arc_points = []
        #     for angle in range(-20, 21, 3): # Controls how wide the arc is
        #         arc_points.append(center + dir_v.rotate(angle) * (radius * 0.95))
        #     if len(arc_points) > 1:
        #         pygame.draw.lines(surface, (60, 108, 153), False, arc_points, 2)
            
        #     # Draw arrow
        #     pygame.draw.polygon(surface, (60, 108, 153), [end_point] + arc_points[4:-4])

        if self.current_holdable is not None:
            self.current_holdable.draw(surface)

    def set_holdable(self, holdable: Holdable | None) -> None:
        if self.current_holdable is not None and self.current_holdable is not holdable:
            self.current_holdable.reset_input_state()
        self.current_holdable = holdable

    def update_depth_damage(self):
        pass

    def heal(self):
        pass

    def interact(self):
        pass

    def revert(self):
        self.velocity *= 0
        self.input_direction *= 0
        for key in self._movement_keys:
            self._movement_keys[key] = False
        self.is_sprinting = False
        self._left_click_pressed = False
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.health = self.max_health
        self.oxygen = self.max_oxygen
        if self.current_holdable is not None:
            self.current_holdable.reset_input_state()
        self.current_holdable = None

    def get_damaged(self, ammt):
        self.health -= ammt
        self.animations["hurt"].reset()
        self._current_anim = self.animations["hurt"]

        tinted = self._base_image.copy()
        tinted.fill((180, 0, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.image = tinted    # red tint on hit

    # ====== The caves of functions ======


    def _refresh_input_direction(self):
        self.input_direction.x = 0
        self.input_direction.y = 0

        if self._movement_keys[pygame.K_w]:
            self.input_direction.y -= 1
        if self._movement_keys[pygame.K_s]:
            self.input_direction.y += 1
        if self._movement_keys[pygame.K_a]:
            self.input_direction.x -= 1
        if self._movement_keys[pygame.K_d]:
            self.input_direction.x += 1

        # Removes movement on axis if its turned off
        self.input_direction.x *= self.movement_axis.x
        self.input_direction.y *= self.movement_axis.y

        if self.input_direction.length_squared() > 0:
            self.input_direction = self.input_direction.normalize()

    def _update_hitbox(self, angle):
        old_center = self.rect.center
        # Keep a consistent collision rect size to prevent camera jitter
        # The sprite rotation doesn't need to change the actual hitbox
        self.rect.size = (32, 32)
        self.rect.center = old_center

    def _swim_anim(self, speed: float):
        if speed < 2:
            return self.animations["idle"]
        if self.is_sprinting and speed > 80:
            return self.animations["rush"]
        if self.is_sprinting:
            return self.animations["fast"]
        return self.animations["swim"]

    def update_animation_underwater(self, dt):
        speed = self.velocity.length()
        hurt_anim = self.animations["hurt"]
        shoot_anim = self.animations["shoot"]
        holdable = self.current_holdable
        is_held_continuous = self._left_click_pressed and holdable is not None and holdable.continuous

        # If player is hurt this should be priority
        if self._current_anim is hurt_anim and not hurt_anim.finished:
            pass
        # If the current held is continous the anim loops while left_click is held
        elif is_held_continuous:
            if self._current_anim is not shoot_anim or shoot_anim.finished:
                shoot_anim.reset()
            self._current_anim = shoot_anim
        # If the current held is NOT continuous and the animation is not finished we let if finish
        elif self._current_anim is shoot_anim and not shoot_anim.finished:
            pass
        # Priority 4: movement — clean up shoot state if we just finished
        else:
            # Clean the shooting if it's done
            if self._current_anim is shoot_anim and holdable is not None:
                holdable.is_active = False
                self._shoot_facing_vector = None
            self._current_anim = self._swim_anim(speed)

        self._current_anim.update(dt)
        self._base_image = self._current_anim.get_image()
        self.image = self._base_image

        # The player should face the aim direction while shooting or holding and the velocity direction if none
        is_shooting = self._current_anim is shoot_anim
        needs_rotation = is_shooting or is_held_continuous or self.velocity.length_squared() > 0

        if needs_rotation:
            if is_held_continuous:
                facing_vector = holdable.aim_direction.copy()
            elif is_shooting and self._shoot_facing_vector is not None:
                facing_vector = self._shoot_facing_vector
            else:
                facing_vector = self.velocity
            self._apply_facing_rotation(facing_vector)
        else:
            self._update_hitbox(None)

    def update_animation_homebase(self, dt):
        speed = self.velocity.length()
        if self._current_anim.finished:
            self._current_anim.reset()

        # Clean the shooting if it's done
        self._current_anim.update(dt)

        self._base_image = self._current_anim.get_image()
        self.image = self._base_image

        if self.velocity.length() > 0:
            facing_vector = self.velocity.normalize()
            self._apply_facing_rotation(facing_vector)

    def _apply_facing_rotation(self, facing_vector: pygame.math.Vector2):
        if facing_vector.length_squared() == 0:
            facing_vector = pygame.math.Vector2(1, 0)

        is_going_left = facing_vector.x < 0
        angle = facing_vector.angle_to(pygame.math.Vector2(1, 0))
        # Flip sign so rotation matches direction when going left
        angle = angle * -1 if is_going_left else angle
        snapped = round(angle / 15) * 15
        transformed_image = pygame.transform.rotate(self._base_image.convert_alpha(), snapped)
        if is_going_left:
            transformed_image = pygame.transform.flip(transformed_image, False, True)
        self.image = transformed_image
        self._update_hitbox(snapped)

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