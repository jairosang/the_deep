from src.entities.base_entity import Entity
from src.entities.item import Item
from config import game as g_config, player as p_config
import pygame

class Player(Entity):
    def __init__(self) -> None:
        super().__init__(pygame.Surface(p_config["SIZE"]), p_config["START_POS"])
        # THIS IS TEMPORARY
        self.image.fill((255,255,255))

        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

        # Movement
        self.speed = p_config["SPEED"]
        self.velocity = pygame.math.Vector2(0, 0)
        self.current_speed = 0.0
        self.acceleration = self.speed * p_config["ACCELERATION"]
        self.deceleration = self.speed * p_config["DECELERATION"]
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


    def update(self, dt):
        self.update_oxygen()
        self.get_input()
        self._update_velocity(dt)
        self.move(dt)

        self.rect.topleft = (int(self.pos.x), int(self.pos.y)) # sincronize the position after moving

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.pos)


    def get_input(self):
        keys = pygame.key.get_pressed()
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


    def _update_velocity(self, dt):
        # Calculate how fast we wanna go
        target_speed = self.speed * (self.sprint_multiplier if self.is_sprinting else 1)
        target_velocity = self.input_direction * target_speed

        # Is a direction button pressed or not?
        change_rate = self.acceleration * dt if self.input_direction.length_squared() > 0 else self.deceleration * dt

        # How much do we gotta change the velocity by
        delta_velocity = target_velocity - self.velocity

        # Smooth acceleration and deceleration
        if delta_velocity.length() <= change_rate:
            self.velocity = target_velocity
        else:
            self.velocity += delta_velocity.normalize() * change_rate

        self.current_speed = self.velocity.length()


    def move(self, dt):
        self.pos += self.velocity * dt

    def update_oxygen(self):
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
        self.health = self.max_health
        self.oxygen = self.max_oxygen