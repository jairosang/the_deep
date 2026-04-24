from pygame import Surface

from .moving_thing import MovingThing


class Projectile(MovingThing):
    def __init__(self, image: Surface, pos: tuple[int, int]) -> None:
        super().__init__(image, pos)
        
    def destroy(self):
        pass