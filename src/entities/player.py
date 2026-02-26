from src.entities.base_entity import Entity
from src.entities.item import Item
from config import player, FPS
import pygame

class Player(Entity):
    def __init__(self) -> None:
        super().__init__(pygame.Surface(player["SIZE"]), player["START_POS"])
        # THIS IS TEMPORARY
        self.image.fill((255,255,255))

        # Movement
        self.speed = player["SPEED"]
        self.velocity = pygame.math.Vector2(0,0)
        self.is_sprinting = False
        self.sprint_multiplier = player["SPRINT_MULTIPLIER"]
        self.movement_axis = pygame.math.Vector2(1, 1)  # (x, y) 1 allows the player to move on that axis

        # Stats (FOR NOW PULLS BASE DATA FROM CONFIG, WHEN THERE IS PERSISTANCE THIS SHOULD BE PULLED FROM THE DATA MANAGER WHICH WILL DETERMINE IF TO USE BASE STATS OR LOADED STATS)
        self.health = player["BASE_STATS"]["MAX_HEALTH"]
        self.max_health = player["BASE_STATS"]["MAX_HEALTH"]
        self.oxygen = player["BASE_STATS"]["MAX_OXYGEN"]
        self.max_oxygen = player["BASE_STATS"]["MAX_OXYGEN"]
        self.oxygen_depletion_rate = player["BASE_STATS"]["OXYGEN_DEPLETION_RATE"]
        self.depth: float = 0.0
        self.max_depth_limit = player["BASE_STATS"]["MAX_DEPTH_LIMIT"]
        self.buffer_inventory:list[Item] = []
        self.buffer_inventory_capacity = player["BASE_STATS"]["INVENTORY_CAPACITY"]
        # Missing harpoon, weapon and research gun


    def update(self, dt):
        self.update_oxygen()
        self.get_input()
        self.move(dt)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.pos)


    def get_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_w]:
            self.velocity.y = -1
        if keys[pygame.K_s]:
            self.velocity.y = 1
        if keys[pygame.K_a]:
            self.velocity.x = -1
        if keys[pygame.K_d]:
            self.velocity.x = 1

        self.is_sprinting = keys[pygame.K_SPACE]

        # Removes movement on axis if its turned off
        self.velocity.x *= self.movement_axis.x
        self.velocity.y *= self.movement_axis.y

        if self.velocity.length() != 0:
            self.velocity = self.velocity.normalize()

    def move(self, dt):
        current_speed = self.speed * (self.sprint_multiplier if self.is_sprinting else 1.0)
        self.pos += self.velocity * current_speed * dt


    def update_oxygen(self):
        # This thing will have implemented the game over thing when the oxygen is 0
        if self.oxygen <= 0:
            pass

        # This is the thing that checks how to update the oxygen thing if you are sprinting or not
        if self.oxygen > 0:
            if self.is_sprinting == False:
                self.oxygen -= self.oxygen_depletion_rate/FPS
            if self.is_sprinting == True:
                self.oxygen -= self.oxygen_depletion_rate*2/FPS
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