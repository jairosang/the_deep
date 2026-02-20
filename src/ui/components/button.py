import pygame

class Button:
    def __init__(self, position, size, color=[100, 100, 100], hover_color=None, func=None, text='', font="Segoe Print", font_size=16, font_color=[0, 0, 0]):
        self.color = color
        self.size = size
        self.func = func
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
        self.mouseover()

        self.surface.fill(self.curcolor)
        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def mouseover(self):
        self.curcolor = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curcolor = self.hover_color
            
    def call_back(self, *args):
        if self.func:
            return self.func(*args)
