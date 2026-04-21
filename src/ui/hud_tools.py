import pygame
from src.entities.tool import Tool

class Inventory:
    # Toolbar style inventory. Draws a row of slots at a given screen position
    # falls back to a colored square if a tool has no image
    def __init__(self, position, slot_count=3, slot_size=(60, 60), padding=8) -> None:
        self.position = position
        self.slot_count = slot_count
        self.slot_size = slot_size
        self.padding = padding
        self.selected_index = 0

        self.label_font = pygame.font.SysFont("Segoe Print", 14)

        # The icons are scaled to size to fit the slot
        self._scaled_icons: dict[int, pygame.Surface] = {}

    def select(self, index: int) -> None:
        # Ignore invalid indexes so we never point at a slot that isn't shown.
        if 0 <= index < self.slot_count:
            self.selected_index = index

    def handle_event(self, e: pygame.event.Event) -> None:
        # Number keys to swap between slots:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                self.select(0)
            elif e.key == pygame.K_2:
                self.select(1)
            elif e.key == pygame.K_3:
                self.select(2)

    def draw(self, screen: pygame.Surface, tools: list[Tool]) -> None:
        x0, y0 = self.position

        for i in range(self.slot_count):
            x = x0 + i * (self.slot_size[0] + self.padding)
            y = y0
            slot_rect = pygame.Rect(x, y, self.slot_size[0], self.slot_size[1])

            pygame.draw.rect(screen, (40, 40, 40), slot_rect)

            # Insert the icon, otherwise it would return to a plain square.
            if i < len(tools):
                tool = tools[i]
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
    The images of the tools are generated at a bigger size, so I had to think how to fit it at 50x50 pixels slots efficiently;
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
