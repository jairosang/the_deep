import pygame
from src.entities.creatures.base_creature import Creature, Vec2
from config import aggresive_creatures as ac_config

class AggressiveCreature(Creature):
    def __init__(self, pos: tuple[float, float], chase_radius: float = 260.0, size: int = 18) -> None: #also removed kwargs
        super().__init__(pos, size, ac_config["THRUST"])
        self.chase_radius = chase_radius
        self.mass = ac_config["MASS"]
        self.health = ac_config["HEALTH"]
        self.max_health = ac_config["HEALTH"]

    def think(self, dt: float, player_pos) -> None:                             #is now only passing player_pos
        dist = self.pos.distance_to(player_pos)

        if dist <= self.chase_radius:
            # chase at full speed
            self.thrust = ac_config["THRUST"]
            return self._dir_towards(player_pos)
        else:
            # patrol/wander at half thrust
            self.thrust = ac_config["THRUST"] * 0.5
            return self.wander_dir(dt)

    def draw(self, screen: pygame.Surface) -> None:
        # Red = hostile
        super().draw(screen, color=(220, 50, 50))