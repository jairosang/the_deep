from pathlib import Path
from .research_database import ResearchDatabase


class ResearchCatalog:
    # Stores creature information and calls the database whether each species scan is completed
    def __init__(self, research_database: ResearchDatabase | None) -> None:
        self.research_database = research_database
        self.entries = {
            "fish": {
                "name": "Small Fish",
                "category": "PassiveCreature",
                "sprite": Path("assets/sprites/fish.png"),
                "frame_size": (32, 32),
                "description": "A calm swimmer that moves in groups.",
            },
            "blue-fish": {
                "name": "Blue Fish",
                "category": "PassiveCreature",
                "sprite": Path("assets/sprites/fish_no_bg.png"),
                "frame_size": (512, 512),
                "description": "A larger passive fish that keeps distance.",
            },
            "fish-dart": {
                "name": "Dart Fish",
                "category": "AggressiveCreature",
                "sprite": Path("assets/sprites/fish-dart.png"),
                "frame_size": (39, 20),
                "description": "Small but fast predator with dashes.",
            },
            "fish-big": {
                "name": "Big Fish",
                "category": "AggressiveCreature",
                "sprite": Path("assets/sprites/fish-big.png"),
                "frame_size": (54, 49),
                "description": "Big hunter that deals plenty of damage upon contact.",
            },
            "anglerfish": {
                "name": "Anglerfish",
                "category": "AggressiveCreature",
                "sprite": Path("assets/sprites/anglerfish.png"),
                "frame_size": (350, 350),
                "description": "A serious threat in the depths with high endurance.",
            },
        }
        self.order = list(self.entries.keys())

    def get_order(self) -> list[str]:
        return self.order

    def get_entry(self, species: str) -> dict:
        return self.entries[species]

    def is_species_complete(self, species: str) -> bool:
        if self.research_database is None:
            return False
        return self.research_database.is_species_complete(species)
