from src.entities.base_entity import Entity
from src.entities.item import Item
from src.utils import physics_service as phy
from config import game as g_config, player as p_config
import pygame

class Player(Entity):
    def __init__(self) -> None:
        super().__init__(pygame.Surface(p_config["SIZE"]), p_config["START_POS"])
        # THIS IS TEMPORARY
        self.image.fill((255,255,255))

        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

        # Movement
        self.velocity = pygame.math.Vector2(0, 0)
        self.thrust = p_config["THRUST"]
        self.mass = p_config["MASS"]
        self.acceleration = 0
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
        # Missing harpoon, weapon and research gun


    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        self._update_oxygen()
        # ===== Movement update logic =======
        self._move_x(dt)                             # Player moves on one axis
        phy.check_collisions_x(self, area_tiles)    # Physics react
        self._move_y(dt)
        phy.check_collisions_y(self, area_tiles)
        # ====================================
        self._update_velocity(dt)
        self.rect.clamp_ip(bound_rect)              # Applying clamping
        self.pos.update(self.rect.x, self.rect.y)   # Updating to use the clamping

    def handle_inputs(self, keys):
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

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def _update_velocity(self, dt):
        # Apply extra thrust if the player is sprinting
        current_thrust = self.thrust * (self.sprint_multiplier if self.is_sprinting else 1)
        
        # Adjust acceleration and velocity according to thrust and adding slowdown with the drag
        self.acceleration = self.input_direction * current_thrust - (g_config["DRAG"] * self.velocity)
        self.velocity += self.acceleration * dt

        # Avoid floating point numbers staying there and keeping the player moving when standing
        if self.velocity.length_squared() < 1:
            self.velocity = pygame.math.Vector2(0, 0)

    # Calculate movement on the x axis
    def _move_x(self, dt):
        self.pos.x += self.velocity.x * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))  # sincronize the position after moving

    # Calculate movement on the y axis
    def _move_y(self, dt):
        self.pos.y += self.velocity.y * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))  # sincronize the position after moving

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
        self.pos = pygame.math.Vector2(30, 30)
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.health = self.max_health
        self.oxygen = self.max_oxygen