import pygame
import pygame_menu
from pygame_menu import themes
import sys
import math
import random
from first_inventory_trial import InventoryMenu
from first_upgrades_trial import UpgradesMenu

# Init
pygame.init()
info = pygame.display.Info()
s_width = info.current_w
s_height = info.current_h
surface = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Deep Dive Hub")
clock = pygame.time.Clock()

# Static background layers are rendered once

"""Deep-ocean colour"""
def make_gradient():
    surf = pygame.Surface((s_width, s_height))
    for y in range(s_height):
        t = y / s_height
        surf.fill((int(2 + t * 4), int(8 + t * 20), int(38 + t * 50)), rect=(0, y, s_width, 1))
    return surf

"""seafloor silhouette"""
def make_terrain():
    rng  = random.Random(42) # fixed shape every run
    surf = pygame.Surface((s_width, s_height), pygame.SRCALPHA)
    pts = [(0, s_height)]
    x   = 0
    while x < s_width + 80:
        step = rng.randint(40, 100)
        peak = rng.randint(s_height - 160, s_height - 25)
        pts.append((x + step // 2, peak))
        pts.append((x + step, s_height - rng.randint(5, 50)))
        x += step
    pts.append((s_width, s_height))
    pygame.draw.polygon(surf, (3, 8, 22, 255), pts)

    # Coral- rock lines
    for c in range(35):
        cx = rng.randint(0, s_width)
        cy = s_height - rng.randint(10, 100)
        for c in range(rng.randint(2, 5)):
            angle  = math.radians(rng.randint(240, 300))
            length = rng.randint(10, 48)
            ex = int(cx + math.cos(angle) * length)
            ey = int(cy + math.sin(angle) * length)
            col = rng.choice([(90, 25, 65), (20, 90, 75), (70, 50, 20)])
            pygame.draw.line(surf, col, (cx, cy), (ex, ey), 2)
    return surf

"""Rectangular dark border"""
def make_vignette():
    
    surf = pygame.Surface((s_width, s_height), pygame.SRCALPHA) # .SRCALPHA - makes it support transparency so anything that is not drawn on it stays transparent
    depth = min(s_width, s_height) // 5
    for i in range(depth):
        t = i / depth
        alpha = int(170 * (1 - t) ** 1.8)
        pygame.draw.rect(surf, (0, 0, 0, alpha), (i, i, s_width - 2 * i, s_height - 2 * i), 1)
    return surf

gradient_surf = make_gradient()
terrain_surf = make_terrain()
vignette_surf = make_vignette()

# Light beam (base pre-rendered, shimmer animated)
bx = s_width // 2
top_w = s_width // 14
bot_w = s_width // 5

beam_base = pygame.Surface((s_width, s_height), pygame.SRCALPHA)
pygame.draw.polygon(beam_base, (20, 90, 200, 10), [(bx - top_w, 0), (bx + top_w, 0), (bx + bot_w, s_height), (bx - bot_w, s_height)])

shimmer_surf = pygame.Surface((s_width, s_height), pygame.SRCALPHA)

def draw_beam(surf, t):
    surf.blit(beam_base, (0, 0))
    shimmer_surf.fill((0, 0, 0, 0))
    for i in range(4):
        phase = (t * 0.35 + i * 0.25) % 1.0
        sy = int(phase * s_height)
        lw = int(top_w + (bot_w - top_w) * phase)
        pygame.draw.line(shimmer_surf, (100, 180, 255, 14), (bx - lw, sy), (bx + lw, sy), 1)
    surf.blit(shimmer_surf, (0, 0))

# Bubbles animation
class Bubble:
    def __init__(self):
        self.spawn()
    '''Each time the bubble appaears it picks the random value for each of the variabels below:'''
    def spawn(self):
        self.x = random.uniform(0, s_width)
        self.y = random.uniform(s_height, s_height + 200)
        self.r = random.randint(2, 8)
        self.speed = random.uniform(0.5, 2.2)
        self.phase = random.uniform(0, math.tau)
        self.wfreq = random.uniform(0.02, 0.06)
        self.alpha = random.randint(45, 120)
        # allocateed a small surface for this bubble
        d = self.r * 2 + 6
        self.surf = pygame.Surface((d, d), pygame.SRCALPHA)
        c = d // 2
        # light blue with tranpency, .alpha controls the amount of transparency
        pygame.draw.circle(self.surf, (160, 230, 255, self.alpha), (c, c), self.r, 2)
        hl_r = max(1, self.r // 4)
        hl_alpha = min(self.alpha + 60, 200)
        pygame.draw.circle(self.surf, (255, 255, 255, hl_alpha), (c - max(1, self.r // 3), c - max(1, self.r // 3)), hl_r)

    def update(self):
        self.y -= self.speed
        self.phase += self.wfreq
        self.x += math.sin(self.phase) * 0.7
        if self.y < -self.r:
            self.spawn()

    def draw(self, surf):
        c = self.surf.get_width() // 2
        surf.blit(self.surf, (int(self.x) - c, int(self.y) - c))

bubbles = [Bubble() for _ in range(70)]

# Menu metrics
inventory = InventoryMenu(s_width, s_height)
upgrades  = UpgradesMenu(s_width, s_height)

def start_the_game():
    pass

def open_inventory():
    inventory.get_menu().mainloop(surface)

def open_upgrades():
    upgrades.get_menu().mainloop(surface)

def quit_game():
    pygame.quit()
    sys.exit()

# Menu setup
menu_w = int(s_width  * 0.38)
menu_h = int(s_height * 0.72)

hub_theme = themes.THEME_DARK.copy()
hub_theme.background_color = (5, 15, 40, 210)
hub_theme.title_background_color = (0, 25, 70, 240)
hub_theme.title_font_color = (0, 210, 255)
hub_theme.title_font_size = max(28, s_height // 22)
hub_theme.widget_font_size = max(20, s_height // 32)
# sets the visual effect around the hovered item
hub_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
    border_width =2 , margin_x = 18, margin_y = 8
)
hub_theme.selection_color = (0, 210, 255)

mainmenu = pygame_menu.Menu('Welcome to Hub', menu_w, menu_h, theme=hub_theme)
mainmenu.add.text_input('Name: ', default='username', maxchar=20)
mainmenu.add.button('Start the Dive', start_the_game)
mainmenu.add.button('Inventory', open_inventory)
mainmenu.add.button('Upgrades', open_upgrades)
mainmenu.add.button('Quit', quit_game)

# Main loop
time = 0.0
while True:
    dt = clock.tick(60) / 1000.0
    time += dt

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            quit_game()

    # Scene layers in back-to-front order
    surface.blit(gradient_surf, (0, 0))   # - ocean gradient
    draw_beam(surface, time)              # - animated light
    for b in bubbles:                      # - bubbles
        b.update()
        b.draw(surface)
    surface.blit(terrain_surf, (0, 0))    # - seafloor silhouette
    surface.blit(vignette_surf, (0, 0))   # - edge vignette

    if mainmenu.is_enabled():
        mainmenu.update(events)
        mainmenu.draw(surface)             # - top menu panel

    pygame.display.flip()
