import pygame

class Camera:

    def __init__(self, size: tuple[int, int], map_rect: pygame.Rect):

        self.pos = pygame.math.Vector2(0,0)
        self.target = pygame.math.Vector2(0,0)
        self.size = size
        self.map_rect = map_rect
        self.rect = pygame.Rect(0,0, size[0], size[1])
        self.zoom = 2

        self.rect.clamp_ip(self.map_rect)


    def update(self, dt, new_target: pygame.Rect):
        # To account for zoom
        visual_w = max(1, int(self.size[0] / self.zoom))
        visual_h = max(1, int(self.size[1] / self.zoom))
        self.rect.size = (visual_w, visual_h)

        # Updating what I want to be the new center and 
        self.target.update(new_target.centerx, new_target.centery)
        self.rect.topleft = (
            int(self.target.x - visual_w / 2),
            int(self.target.y - visual_h / 2),
        )
        self.rect.clamp_ip(self.map_rect)


    def draw(self, surface: pygame.Surface, destSurface:pygame.Surface):
        # clip so we dont try to draw more than necessary
        destSurface.set_clip((self.pos[0], self.pos[1], self.size[0], self.size[1]))
        # fill camera to reset from previous frame
        destSurface.fill((0, 0, 0))

        # top-left point in the camera
        x = self.rect.left * self.zoom
        y = self.rect.top * self.zoom

        # scaling in case we change zoom
        scaled_surface = pygame.transform.scale(surface, (surface.get_width() * self.zoom, surface.get_height() * self.zoom))

        # drawing the world
        destSurface.blit(scaled_surface, self.pos, (x, y, self.size[0], self.size[1]))
        # reset the clipping
        destSurface.set_clip(None)