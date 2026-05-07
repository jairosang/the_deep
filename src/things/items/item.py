import pygame

class Item():
    def __init__(self, pos, name = "creature_loot", image = None, inventory_image = None) -> None:
        self.name = name
        self.inventory_image = inventory_image.copy() if inventory_image is not None else None
        self.pos = pygame.math.Vector2(pos)
        self.pickup_timer = 2.0 # time before being able to pick up item

        if image is not None:
            self.image = image.copy()
            # add a dark blue-grey tint so it looks dead/washed out
            self.image.fill((0, 30, 60, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))
        else:
            # fallback gray square if no image given
            self.image = pygame.Surface((18, 18))
            self.image.fill((120, 120, 120))
            self.rect = self.image.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

    def interact(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)