import pygame

class Button:
    def __init__(self, position, size, color=[100, 100, 100], hover_color=None, func=None, text='', font="Segoe Print", font_size=16, font_color=[0, 0, 0], border_radius=8, border_color=None, border_width=2):
        self.color = color
        self.curcolor = color
        self.size = size
        self.func = func
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_width = border_width

        # Rounded corners
        if border_radius > 0:
            self.surface = pygame.Surface(size, pygame.SRCALPHA)
        else:
            self.surface = pygame.Surface(size)

        self.rect = self.surface.get_rect(center=position)
        self.font = pygame.font.SysFont(font, font_size)
        self.txt = text
        self.font_color = font_color
        self.txt_surf = self.font.render(self.txt, 1, self.font_color)
        self.txt_rect = self.txt_surf.get_rect(center=[wh//2 for wh in self.size])

        if hover_color:
            self.hover_color = hover_color
        else:
            self.hover_color = color

    def draw(self, screen):
        if self.border_radius > 0:
            self.surface.fill((0, 0, 0, 0))
            pygame.draw.rect(self.surface, self.curcolor, self.surface.get_rect(), border_radius=self.border_radius)
        else:
            self.surface.fill(self.curcolor)

        if self.border_color is not None:
            pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), width=self.border_width, border_radius=self.border_radius)

        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def check_mouseover(self, mouse_pos: tuple[int, int]):
        self.curcolor = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curcolor = self.hover_color

    def call_back(self, *args):
        if self.func:
            return self.func(*args)
