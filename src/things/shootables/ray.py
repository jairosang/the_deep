import math
import pygame


class Ray:
    start_width = 8  # how wide the beam is at the player
    cone_angle = 30  # full spread angle in degrees

    def __init__(self, origin, range: float, beam_color=(0, 255, 100)) -> None:
        self.origin = pygame.math.Vector2(origin)
        self.end_pos = pygame.math.Vector2(origin)
        self.range = range
        self.beam_color = beam_color

    @property
    def end_width(self) -> float:
        # how wide the beam is at its far end
        return self.start_width + 2 * self.range * math.tan(math.radians(self.cone_angle / 2))

    def update(self, origin, target_pos) -> None:
        direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(origin)
        if direction.length() <= 0:
            return
        dir_unit = direction.normalize()
        self.origin.update(pygame.math.Vector2(origin) + dir_unit * 25)
        direction.scale_to_length(self.range)
        self.end_pos = self.origin + direction

    def get_creatures_in_beam(self, creatures: list) -> list:
        direction = self.end_pos - self.origin
        beam_length = direction.length()
        if beam_length <= 0:
            return []
        dir_unit = direction / beam_length
        start_half = self.start_width / 2
        end_half = self.end_width / 2
        inside = []
        for c in creatures:
            offset = pygame.math.Vector2(c.rect.center) - self.origin
            proj = offset.dot(dir_unit)  # how far forward along the beam
            if proj < 0 or proj > beam_length:
                continue
            side_dist = abs(offset.x * dir_unit.y - offset.y * dir_unit.x)  # how far off center
            half_width = start_half + (end_half - start_half) * (proj / beam_length)
            if side_dist <= half_width:
                inside.append(c)
        return inside

    def draw(self, surface) -> None:
        dir_x = self.end_pos[0] - self.origin[0]
        dir_y = self.end_pos[1] - self.origin[1]
        beam_length = (dir_x**2 + dir_y**2) ** 0.5
        if beam_length <= 0:
            return

        unit_x = dir_x / beam_length
        unit_y = dir_y / beam_length
        normal_x, normal_y = -unit_y, unit_x
        r, g, b = self.beam_color
        end_width = self.end_width

        # 4 corners of the beam trapezoid
        p1 = (int(self.origin[0] + normal_x * self.start_width / 2),
              int(self.origin[1] + normal_y * self.start_width / 2))
        p2 = (int(self.origin[0] - normal_x * self.start_width / 2),
              int(self.origin[1] - normal_y * self.start_width / 2))
        p3 = (int(self.end_pos[0] - normal_x * end_width / 2),
              int(self.end_pos[1] - normal_y * end_width / 2))
        p4 = (int(self.end_pos[0] + normal_x * end_width / 2),
              int(self.end_pos[1] + normal_y * end_width / 2))

        beam_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(beam_surface, (r, g, b, 100), [p1, p2, p3, p4])
        surface.blit(beam_surface, (0, 0))
