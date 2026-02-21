from src.entities.base_entity import Entity
from src.entities.item import Item
import pygame

class Player(Entity):
    def __init__(self) -> None:
        super().__init__(pygame.Surface((20, 20)), (30, 30))
        # THIS IS TEMPORARY
        self.image.fill((255,255,255))

        # Movement
        self.speed = 200
        self.velocity = pygame.math.Vector2(0,0)
        self.is_sprinting = False
        self.sprint_multiplier: float = 1.5
        self.movement_axis = pygame.math.Vector2(1, 1)  # (x, y) 1 allows the player to move on that axis

        # Stats
        self.health = 50
        self.max_health = 50
        self.oxygen = 50
        self.max_oxygen = 50
        self.oxygen_depletion_rate = 1
        self.depth: float
        self.max_depth_limit = 100

        self.buffer_inventory:list[Item] = []
        self.buffer_inventory_capacity = 5
        # Missing harpoon, weapon and research gun


    def update(self, dt):
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
        pass

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