from things import Holdable
from config import game as g_config
import pygame

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

        self.label_font = pygame.font.SysFont("Segoe Print", 14)

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
        scaled = pygame.transform.smoothscale(image, new_size) # final resizing of the image with smooth scaling to avoid pixelation
        self._scaled_icons[index] = scaled # Save the scaled image for the next return
        return scaled
    

class PlayerHud:
    # Pixel style health/oxygen HUD 

    HEALTH_LOW_RATIO = 0.25
    OXYGEN_LOW_RATIO = 0.15

    def __init__(self, pos: tuple[int, int] | None = None, size: tuple[int, int] = (400, 50)) -> None:
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        self.pos = pos if pos is not None else (24, screen_h - 130)
        self.size = size
        self.gap = 16
        self.border = 4
        self.font = pygame.font.Font(None, 28)
        self.medium_font = pygame.font.Font(None, 30)
        self._last_health: float | None = None
        # timer for the health bar growth and glow after taking damage.
        self._hit_pulse_timer = 0.0
        self._hit_pulse_duration = 0.22
        self._time = 0.0

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
        if map_height is not None:
            self._draw_depth(screen, player, map_height, x, y - 35)
        # oxygen bar blinks when low
        self._draw_bar(screen, pygame.Rect(x, y + self.size[1] + self.gap, *self.size), "OXYGEN", player.oxygen, player.max_oxygen, (40, 145, 235), (10, 35, 80), self.OXYGEN_LOW_RATIO, blink_when_low=True)
        # health bar glows when damaged
        self._draw_bar(screen, pygame.Rect(x, y, *self.size), "HEALTH", player.health, player.max_health, (210, 35, 35), (70, 15, 20), self.HEALTH_LOW_RATIO, pulse_timer=self._hit_pulse_timer, pulse_duration=self._hit_pulse_duration)

    def _draw_depth(self, screen: pygame.Surface, player, map_height: int, x: int, y: int) -> None:
        depth = max(0, int(player.rect.centery))
        text = self.medium_font.render(f"DEPTH: {depth} m", False, (245, 245, 230))
        screen.blit(text, (x, y))


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