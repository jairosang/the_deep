from .base_holdable import Holdable

class ResearchGun(Holdable):
    def __init__(self) -> None:
        self.name = "Research Gun"
        self.description = "Scanner used to analyze underwater creatures"
        self.color = (90, 200, 160)
        self.image_path = None
        self.scan_rate = 1.0
        self.range = 128
        self.cooldown_s = 0.25
        self.is_available = False

        super().__init__()
        
    def shoot(self, pos: tuple[int, int]):
        pass