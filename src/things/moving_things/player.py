from .moving_thing import MovingThing
from ..items.item import Item
from config import game as g_config, player as p_config
import pygame

class Player(MovingThing):
    def __init__(self) -> None:
        super().__init__(pygame.Surface(p_config["SIZE"]))
        # THIS IS TEMPORARY
        self.image.fill((255,255,255))

        self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

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
        # Missing harpoon, weapon and research gun


    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        super().update(dt, bound_rect, area_tiles)
        self._update_oxygen()

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
        super().draw(surface)
        if self.velocity.length_squared() > 0: 
            center = pygame.math.Vector2(self.rect.center)
            velocity_scaled = self.velocity / 15    # Controls how far the arrow extends

            dir_v = velocity_scaled.normalize()
            radius = self.rect.height * 3 / 4       # Controls how far from the center the arc is
            end_point = center + velocity_scaled + dir_v * radius
            
            # Drawing an arc in the direction of velocity
            arc_points = []
            for angle in range(-20, 21, 3): # Controls how wide the arc is
                arc_points.append(center + dir_v.rotate(angle) * (radius * 0.95))
            if len(arc_points) > 1:
                pygame.draw.lines(surface, (60, 108, 153), False, arc_points, 2)
            
            # Draw arrow
            print(f"{arc_points}\n")
            pygame.draw.polygon(surface, (60, 108, 153), [end_point] + arc_points[4:-4])
                    

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