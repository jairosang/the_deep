import math
from things import Holdable, Player
from config import game as g_config
from .font import get_font
import pygame

# BTW: Must be noted this was Daniel's contribution even if git blame says otherwise. I just had to adjust it a bit 
class HeldInventory:
    # Toolbar style inventory. Draws a row of slots on the lower right side of the screen
    # falls back to a colored square if a tool has no image
    def __init__(self, init_holdables: list[Holdable], slot_size=(100,100), padding=8) -> None:
        self.slot_size = slot_size
        self.padding = padding
        self.selected_index = 0
        self.holdables: list[Holdable] = init_holdables
        self.slot_count = len(init_holdables)

        # Calculate position based on screen size - bottom right corner
        toolbar_width = self.slot_count * self.slot_size[0] + (self.slot_count - 1) * self.padding
        toolbar_x = g_config["SCREEN_SIZE"][0] - toolbar_width - 20
        toolbar_y = g_config["SCREEN_SIZE"][1] - self.slot_size[1] - 30
        self.pos = (toolbar_x, toolbar_y)

        self.label_font = get_font(14)

        # The icons are scaled to size to fit the slot
        self._scaled_icons: dict[int, pygame.Surface] = {}

    def remove_holdable(self, index):
        self.holdables.pop(index)
        self.slot_count -= 1

    def append_holdables(self, new_holdables: list[Holdable]):
        for hold in new_holdables:
            self.holdables.append(hold)
            self.slot_count += 1

    def select(self, index: int) -> None:
        # Ignore invalid indexes so we never point at a slot that isn't shown.
        if 0 <= index < self.slot_count:
            self.selected_index = index

    def handle_event(self, e: pygame.event.Event) -> None:
        # Number keys to swap between slots:
        if e.type == pygame.KEYDOWN:
            if pygame.K_1 <= e.key <= pygame.K_9:
                self.select(e.key - pygame.K_1)
            elif e.key == pygame.K_TAB:
                # cycle through holdables
                if self.slot_count > 0:
                    new_index = (self.selected_index + 1) % self.slot_count
                    self.select(new_index)

    @property
    def selected_holdable(self) -> Holdable | None:
        if 0 <= self.selected_index < len(self.holdables):
            return self.holdables[self.selected_index]
        return None

    def draw(self, screen: pygame.Surface) -> None:
        x0, y0 = self.pos

        for i in range(self.slot_count):
            x = x0 + i * (self.slot_size[0] + self.padding)
            y = y0
            slot_rect = pygame.Rect(x, y, self.slot_size[0], self.slot_size[1])

            pygame.draw.rect(screen, (40, 40, 40), slot_rect)

            # Insert the icon, otherwise it would return to a plain square.
            if i < len(self.holdables):
                tool = self.holdables[i]
                icon_rect = slot_rect.inflate(-10, -10)
                if tool.image is not None:
                    scaled = self._get_scaled_icon(i, tool.image, icon_rect.size)
                    icon_blit_rect = scaled.get_rect(center=icon_rect.center)
                    screen.blit(scaled, icon_blit_rect)
                else:
                    pygame.draw.rect(screen, tool.color, icon_rect)

            # Slot border, its highlited when selected.
            if i == self.selected_index:
                border_color = (245, 220, 90)
                border_width = 3
            else:
                border_color = (180, 180, 180)
                border_width = 1
            pygame.draw.rect(screen, border_color, slot_rect, border_width)

            # Numbers in the corner to display the selected item slot
            num_surf = self.label_font.render(str(i + 1), True, (255, 255, 255))
            screen.blit(num_surf, (x + 4, y + 2))

    '''
    The images of the holdables are generated at a bigger size, so I had to think how to fit it at 50x50 pixels slots efficiently;
    Shrinking the original image so it would fit the slot size 30 times every second is not efficient and slow as it would look the same;
    Every times the slot is drawn, image would shrank and would get the result stored in self._scaled_icons;
    This way, it would just return the cached image from dictionary instead of shrinking it many times.
    '''
    def _get_scaled_icon(self, index: int, image: pygame.Surface, target_size: tuple[int, int]) -> pygame.Surface:
        # Scale once and cache. Preserves aspect ratio so the icon fits inside target_size.
        cached = self._scaled_icons.get(index)
        if cached is not None and cached.get_size() == target_size:
            return cached # Do we have a sclaed image? If yes, return it and pass to line 85

        img_w, img_h = image.get_size()
        target_w, target_h = target_size
        scale = min(target_w / img_w, target_h / img_h) # 50/1024 = 0.049 and 50/570 = 0.088 width and height scale
        new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale))) # multiplies the original width and height by the scale to get the new size
        scaled = pygame.transform.scale(image, new_size) # final resizing of the image with smooth scaling to avoid pixelation
        self._scaled_icons[index] = scaled # Save the scaled image for the next return
        return scaled
    

class PlayerHud:
    # Pixel style health/oxygen HUD 

    HEALTH_LOW_RATIO = 0.25
    OXYGEN_LOW_RATIO = 0.15

    def __init__(self, map_height: int, pos: tuple[int, int] | None = None, size: tuple[int, int] = (300, 35)) -> None:
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        self.gap = 20
        self.size = size
        self.pos = pos if pos is not None else (self.gap, screen_h - (self.size[1] + self.gap) * 2)
        self.map_height = map_height
        self.border = 4
        self.font = get_font(28)
        self.medium_font = get_font(30)
        self._last_health: float | None = None
        # timer for the health bar growth and glow after taking damage.
        self._hit_pulse_timer = 0.0
        self._hit_pulse_duration = 0.22
        self._time = 0.0
        self.current_depth_indicator_pos = (0, 0)
        self.max_depth_indicator_pos = (0, 0)

    def update(self, player, dt: float) -> None:
        self._time += dt
        if self._last_health is None:
            self._last_health = player.health

        # If health dropped since last frame, trigger the hit pulse.
        if player.health < self._last_health:
            self._hit_pulse_timer = self._hit_pulse_duration
        self._last_health = player.health
        self._hit_pulse_timer = max(0.0, self._hit_pulse_timer - dt)

    def draw(self, screen: pygame.Surface, player, map_height: int | None = None) -> None:
        x, y = self.pos
        # oxygen bar blinks when low
        self._draw_depth_counter(screen, player)
        self._draw_bar(screen, pygame.Rect(x, y + self.size[1] + self.gap, *self.size), "OXYGEN", player.oxygen, player.max_oxygen, (40, 145, 235), (10, 35, 80), self.OXYGEN_LOW_RATIO, blink_when_low=True)
        # health bar glows when damaged
        self._draw_bar(screen, pygame.Rect(x, y, *self.size), "HEALTH", player.health, player.max_health, (210, 35, 35), (70, 15, 20), self.HEALTH_LOW_RATIO, pulse_timer=self._hit_pulse_timer, pulse_duration=self._hit_pulse_duration)

    def _draw_depth_fill(self, screen: pygame.Surface, gauge_x: int, gauge_top: int, gauge_width: int, gauge_height: int, filled_height: int) -> None:
        if filled_height <= 0:
            return

        # Draw the filled water column with gradient effect
        fill_rect = pygame.Rect(gauge_x, gauge_top + gauge_height - filled_height, gauge_width, filled_height)
        
        # Solid fill color (orange)
        pygame.draw.rect(screen, (255, 140, 0), fill_rect)

    def _draw_depth_markers(self, screen: pygame.Surface, gauge_x: int, gauge_top: int, gauge_width: int, gauge_height: int, map_height: float) -> None:
        # drawing marker lines at 50m and 100m intervals inside the depth gauge.
        map_height = max(1.0, float(map_height))
        
        depth_m = 0.0  # depth in meters
        while depth_m * 16.0 < map_height:
            # getting the Y position from the bottom of the gauge
            y = gauge_top + gauge_height - (depth_m * 16.0 / map_height) * gauge_height
            
            if gauge_top <= y <= gauge_top + gauge_height:
                if depth_m % 100 == 0 and depth_m > 0:  # 100m marker
                    line_width = int(gauge_width * 0.6)
                    line_color = (230, 120, 0)
                elif depth_m % 50 == 0:  # 50m marker
                    line_width = int(gauge_width * 0.35)
                    line_color = (200, 100, 0)
                else:
                    depth_m += 50.0
                    continue
                
                start_x = gauge_x
                end_x = gauge_x + line_width
                pygame.draw.line(screen, line_color, (start_x, y), (end_x, y), 3)
            
            depth_m += 50.0

    def _draw_depth_counter(self, screen: pygame.Surface, player: Player) -> None:
        screen_h = screen.get_height()
        map_height = max(1.0, float(self.map_height))
        player_depth_px = float(player.rect.centery)
        current_depth_ratio = player_depth_px / map_height
        max_depth_ratio = min(1.0, player.max_depth_limit / map_height)

        # defining the size and location of the gauge
        gauge_height = min(320, int(screen_h * 0.45))
        gauge_width = 48
        gauge_x = self.gap
        gauge_top = self.pos[1] - self.gap - gauge_height
        gauge_rect = pygame.Rect(gauge_x, gauge_top, gauge_width, gauge_height)

        # drawing the shadow and the stuff (got this from the other bars to keep a similar style)
        shadow = gauge_rect.move(5, 5)
        pygame.draw.rect(screen, (6, 8, 15), shadow)
        pygame.draw.rect(screen, (18, 20, 30), gauge_rect)
        pygame.draw.rect(screen, (225, 225, 210), gauge_rect, self.border)
        pygame.draw.rect(screen, (50, 50, 50), gauge_rect.inflate(-self.border * 2, -self.border * 2))
        
        # depth marking lines to make it easier to get a feel for the depth in the gauge
        self._draw_depth_markers(screen, gauge_x + self.border * 2, gauge_top + self.border * 2, gauge_width - self.border * 4, gauge_height - self.border * 4, map_height)

        # calculating how far up the bar should fill depending on the depth
        filled_height = int(gauge_height * current_depth_ratio)
        self._draw_depth_fill(screen, gauge_x + self.border * 2, gauge_top + self.border * 2, gauge_width - self.border * 4, gauge_height - self.border * 4, filled_height)

        # We have sum wobble when the player crosses the depth threshold to emphasize danger
        limit_y = gauge_top + gauge_height - int(gauge_height * max_depth_ratio)
        limit_passed = max_depth_ratio > 0.0 and current_depth_ratio >= max_depth_ratio
        wobble_x = int(4.0 * math.sin(self._time * 28.0)) if limit_passed else 0
        limit_color = (255, 100, 100) if limit_passed else (220, 200, 90)

        # the line that represents the max_depth_limit for the player and turns red once you go past it
        pygame.draw.line(screen, limit_color, (gauge_x - 8 + wobble_x, limit_y), (gauge_x + gauge_width + 8 + wobble_x, limit_y), 3)

        pointer_x = gauge_x + gauge_width + 14 + wobble_x
        pointer_y = gauge_top + gauge_height - int(gauge_height * current_depth_ratio)
        pointer_color = (255, 100, 100) if limit_passed else (245, 220, 90)

        # triangle that shows the current depth of the player
        pygame.draw.polygon(screen, pointer_color, [(pointer_x, pointer_y), (pointer_x + 10, pointer_y - 6), (pointer_x + 10, pointer_y + 6)])

        depth_text = f"{player_depth_px / 16.0:.1f} m"
        depth_color = (255, 100, 100) if limit_passed else (230, 230, 230)
        depth_surf = self.medium_font.render(depth_text, True, depth_color)
        depth_text_x = pointer_x + 14
        depth_text_y = pointer_y - depth_surf.get_height() // 2

        if limit_passed:
            depth_text_x += int(2.0 * math.sin(self._time * 48.0))
            depth_text_y += int(2.0 * math.cos(self._time * 36.0))

        screen.blit(depth_surf, (depth_text_x, depth_text_y))

        # depth label for the bar
        label_surf = self.font.render("DEPTH", True, (150, 170, 190))
        screen.blit(label_surf, (gauge_x, gauge_top - label_surf.get_height() - 6))

        self.current_depth_indicator_pos = (pointer_x, pointer_y)
        self.max_depth_indicator_pos = (gauge_x + gauge_width // 2 + wobble_x, limit_y)


    def _draw_bar(self, screen: pygame.Surface, rect: pygame.Rect, label: str, value: float, maximum: float, fill_color: tuple[int, int, int], dark_color: tuple[int, int, int], low_ratio: float, pulse_timer: float = 0.0, pulse_duration: float = 1.0, blink_when_low: bool = False) -> None:
        
        ratio = 0 if maximum <= 0 else max(0.0, min(1.0, value / maximum))
        is_low = ratio <= low_ratio
        blink_on = True
        if blink_when_low and is_low:
            blink_on = int(self._time * 8) % 2 == 0

        pulse = 0.0 if pulse_duration <= 0 else pulse_timer / pulse_duration
        scale = 1.0 + 0.10 * pulse
        draw_rect = pygame.Rect(0, 0, int(rect.width * scale), int(rect.height * scale))
        draw_rect.midleft = rect.midleft
        shadow = draw_rect.move(5, 5)
        pygame.draw.rect(screen, (6, 8, 15), shadow)
        pygame.draw.rect(screen, (18, 20, 30), draw_rect)
        pygame.draw.rect(screen, (225, 225, 210), draw_rect, self.border)
        pygame.draw.rect(screen, dark_color, draw_rect.inflate(-self.border * 2, -self.border * 2))
        inner = draw_rect.inflate(-self.border * 4, -self.border * 4)
        inner.width = max(0, int(inner.width * ratio))

        if blink_on and inner.width > 0:
            pygame.draw.rect(screen, fill_color, inner)
            highlight = inner.copy()
            highlight.height = max(3, inner.height // 4)
            pygame.draw.rect(screen, tuple(min(255, c + 45) for c in fill_color), highlight)

        if pulse > 0:
            glow_alpha = int(130 * pulse)
            glow_rect = draw_rect.inflate(14, 14)
            glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*fill_color, glow_alpha), glow.get_rect(), 4)
            screen.blit(glow, glow_rect)

        if is_low:
            # maybe add something like screen tint or flashing idk
            pass

        label_surf = self.font.render(label, False, (245, 245, 230))
        value_surf = self.medium_font.render(f"{max(0, value):.0f}/{maximum:.0f}", False, (245, 245, 230))

        label_y = draw_rect.centery - label_surf.get_height() // 2 # centers the text in the middle of the bars
        screen.blit(label_surf, (draw_rect.x + 10, label_y))
        screen.blit(value_surf, (draw_rect.right + 12, draw_rect.centery - value_surf.get_height() // 2))