from things import Holdable
from config import game as g_config
import pygame

class HeldInventory:
    # Toolbar style inventory. Draws a row of slots on the lower right side of the screen
    # falls back to a colored square if a tool has no image
    def __init__(self, init_holdables: list[Holdable], slot_size=(60, 60), padding=8) -> None:
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