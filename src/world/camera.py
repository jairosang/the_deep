from config import game as g_config
import pygame

class Camera:

    def __init__(self, map_rect: pygame.Rect, zoom: float = 2):

        self.pos = pygame.math.Vector2(0,0)         # pos doesnt hold the camera position in the map, it holds the camera position in the screen from the top left. So it will always be (0,0). Might as well be able to change it just in case idk
        self.target = pygame.math.Vector2(0,0)
        self.size = g_config["SCREEN_SIZE"]
        self.map_rect = map_rect
        self.rect = pygame.Rect(0,0, self.size[0], self.size[1])
        self.zoom = zoom
        self.camera_surface: pygame.Surface | None = None

        self.rect.clamp_ip(self.map_rect)


    def update(self, dt, new_target: pygame.Rect):
        # To account for zoom
        visual_w = max(1, int(self.size[0] / self.zoom))
        visual_h = max(1, int(self.size[1] / self.zoom))
        self.rect.size = (visual_w, visual_h)

        # Updating what I want to be the new center and clamping the camera to the map rectangle
        self.target.update(new_target.centerx, new_target.centery)
        self.rect.topleft = (
            int(self.target.x - visual_w / 2),
            int(self.target.y - visual_h / 2),
        )
        self.rect.clamp_ip(self.map_rect)


    def draw(self, world_surface: pygame.Surface, screen_surface:pygame.Surface):
        # NEW APPROACH: Instead of trying to scale the world surface which is huge, and contains the creatures, into an even bigger size to then only show what is in the screen; make a new surface which is smaller than the screen and only includes what is in the camera rect, then we scale that up to the size of the screen. This fixed all the performance issues. I don't know how it slipped by before :)
        if self.camera_surface is None:
            self.camera_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # Cookie cutting the world surface with the camera rect and blitting that into the camera surface
        self.camera_surface.blit(world_surface, (0, 0), self.rect)

        screen_surface.set_clip((int(self.pos.x), int(self.pos.y), self.size[0], self.size[1]))

        # If the cammera is the same as the screen size ok, if not scale it uppppp
        if self.rect.size == self.size:
            screen_surface.blit(self.camera_surface, self.pos)
        else:
            scaled_view = pygame.transform.scale(self.camera_surface, self.size)
            screen_surface.blit(scaled_view, self.pos)

        screen_surface.set_clip(None)
        # I don't think clipping is needed anymore because the camera is cookie cut and then transformed exactly to the screen size. But I leave it bc it doesn't hurt anyone and it works and I dont want to think about it more because of the haskell exam.