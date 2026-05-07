import pygame
from config import game as g_config
from utils import ResearchCatalog
from .base_menu import BaseMenu
from ..components.button import Button


class ResearchMenu(BaseMenu):
    # Research menu with dimmed silhouettes of fish here for viewing, data will be unlocked upon completion
    def __init__(self, catalog: ResearchCatalog, on_close) -> None:
        super().__init__()
        self.catalog = catalog
        self.on_close = on_close
        self.selected_index = 0

        self.title_font = pygame.font.SysFont("Segoe Print", 40)
        self.heading_font = pygame.font.SysFont("Segoe Print", 30)
        self.body_font = pygame.font.SysFont("Segoe Print", 24)
        self.small_font = pygame.font.SysFont("Segoe Print", 20)

        self.icons = self._load_icons()
        self._build_buttons()

    def _load_icons(self) -> dict[str, pygame.Surface | None]:
        icons: dict[str, pygame.Surface | None] = {}
        for species in self.catalog.get_order():
            entry = self.catalog.get_entry(species)
            path = entry["sprite"]
            if not path.exists():
                icons[species] = None
                continue

            try:
                sheet = pygame.image.load(path.as_posix()).convert_alpha()
            except pygame.error:
                icons[species] = None
                continue

            frame_w, frame_h = entry["frame_size"]
            if sheet.get_width() >= frame_w and sheet.get_height() >= frame_h:
                frame = sheet.subsurface((0, 0, frame_w, frame_h)).copy()
            else:
                frame = sheet.copy()
            icons[species] = frame
        return icons

    def _build_buttons(self) -> None:
        sw, sh = g_config["SCREEN_SIZE"]
        cx = sw / 2
        cy = sh / 2
        self.prev_button = Button((64, cy), (56, 56), (52, 66, 84), (74, 92, 116), text="<", font_size=32, font_color=(238, 246, 255), border_radius=10, border_color=(120, 140, 170))
        self.next_button = Button((sw - 64, cy), (56, 56), (52, 66, 84), (74, 92, 116), text=">", font_size=32, font_color=(238, 246, 255), border_radius=10, border_color=(120, 140, 170))
        self.close_button = Button((cx, sh - 52), (220, 56), (84, 88, 98), (105, 112, 125), text="Close", font_size=26, font_color=(232, 238, 246), border_radius=10, border_color=(145, 155, 170), func=self._close)
        self.buttons = [self.prev_button, self.next_button, self.close_button]

    def _clamp_selection(self) -> None:
        order = self.catalog.get_order()
        if not order:
            self.selected_index = 0
            return
        self.selected_index = max(0, min(self.selected_index, len(order) - 1))

    def open(self) -> None:
        self.is_open = True
        self._clamp_selection()
        self._build_buttons()

    def close(self) -> None:
        self.is_open = False

    def _close(self) -> None:
        self.close()
        self.on_close()

    def _next_entry(self) -> None:
        order = self.catalog.get_order()
        if not order:
            return
        self.selected_index = (self.selected_index + 1) % len(order)

    def _prev_entry(self) -> None:
        order = self.catalog.get_order()
        if not order:
            return
        self.selected_index = (self.selected_index - 1) % len(order)

    def _make_silhouette(self, icon: pygame.Surface) -> pygame.Surface:
        # Make a dark silhouette while preserving alpha edges.
        silhouette = icon.copy().convert_alpha()
        silhouette.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
        silhouette.fill((40, 40, 40, 255), special_flags=pygame.BLEND_RGB_ADD)
        return silhouette

    def handle_event(self, e: pygame.event.Event) -> None:
        if not self.is_open:
            return

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self._close()
            elif e.key == pygame.K_LEFT:
                self._prev_entry()
            elif e.key == pygame.K_RIGHT:
                self._next_entry()
            return

        if e.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_mouseover(e.pos)
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.prev_button.rect.collidepoint(e.pos):
                self._prev_entry()
            elif self.next_button.rect.collidepoint(e.pos):
                self._next_entry()
            elif self.close_button.rect.collidepoint(e.pos):
                self.close_button.call_back()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        sw, sh = g_config["SCREEN_SIZE"]
        cx = sw / 2

        overlay = pygame.Surface((int(sw), int(sh)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        gallery_rect = pygame.Rect(60, 90, sw - 120, 180)
        details_rect = pygame.Rect(160, 300, sw - 320, sh - 390)

        pygame.draw.rect(surface, (20, 30, 46), gallery_rect, border_radius=12)
        pygame.draw.rect(surface, (86, 130, 170), gallery_rect, width=2, border_radius=12)
        pygame.draw.rect(surface, (26, 42, 58), details_rect, border_radius=14)
        pygame.draw.rect(surface, (96, 144, 184), details_rect, width=2, border_radius=14)

        title = self.title_font.render("Research Database", True, (236, 246, 255))
        surface.blit(title, title.get_rect(center=(cx, 52)))

        order = self.catalog.get_order()
        self._clamp_selection()

        species = order[self.selected_index]
        entry = self.catalog.get_entry(species)

        slot_w = max(120, int((gallery_rect.width - 30) / len(order)))
        slot_y = gallery_rect.centery
        start_x = gallery_rect.left + 15 + slot_w // 2

        for idx, slot_species in enumerate(order):
            slot_center_x = start_x + idx * slot_w
            slot_rect = pygame.Rect(0, 0, slot_w - 14, 145)
            slot_rect.center = (slot_center_x, slot_y)

            is_selected = idx == self.selected_index
            is_complete = self.catalog.is_species_complete(slot_species)

            slot_fill = (46, 65, 88) if is_selected else (34, 50, 68)
            slot_border = (255, 224, 138) if is_selected else (98, 132, 165)
            pygame.draw.rect(surface, slot_fill, slot_rect, border_radius=10)
            pygame.draw.rect(surface, slot_border, slot_rect, width=2, border_radius=10)

            icon = self.icons.get(slot_species)
            if icon is None:
                continue

            draw_icon = pygame.transform.smoothscale(icon, (92, 92))
            if not is_complete:
                draw_icon = self._make_silhouette(draw_icon)
            surface.blit(draw_icon, draw_icon.get_rect(center=(slot_rect.centerx, slot_rect.centery - 12)))

        selected_complete = self.catalog.is_species_complete(species)
        detail_name = entry["name"] if selected_complete else "Unknown Species"
        detail_desc = entry["description"] if selected_complete else "Complete this scan to unlock full data."

        name_surf = self.heading_font.render(detail_name, True, (255, 223, 138))
        surface.blit(name_surf, name_surf.get_rect(center=(cx, details_rect.top + 45)))

        type_label = entry["category"] if selected_complete else "Classified"
        type_surf = self.body_font.render(type_label, True, (212, 235, 255))
        surface.blit(type_surf, type_surf.get_rect(center=(cx, details_rect.top + 82)))

        big_icon = self.icons.get(species)
        if big_icon is not None:
            draw_big_icon = pygame.transform.smoothscale(big_icon, (170, 170))
            if not selected_complete:
                draw_big_icon = self._make_silhouette(draw_big_icon)
            surface.blit(draw_big_icon, draw_big_icon.get_rect(center=(cx, details_rect.top + 190)))

        desc = self.small_font.render(detail_desc, True, (216, 230, 240))
        surface.blit(desc, desc.get_rect(center=(cx, details_rect.top + 300)))

        status_label = "Status: Complete" if selected_complete else "Status: Incomplete"
        status_surf = self.body_font.render(status_label, True, (204, 255, 186))
        surface.blit(status_surf, status_surf.get_rect(center=(cx, details_rect.bottom - 34)))

        for button in self.buttons:
            button.draw(surface)
