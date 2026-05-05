class ResearchDatabase:

    def __init__(self):
        # {species: {'alive': progress_percent, 'dead': progress_percent}}
        self.research_data: dict[str, dict[str, float]] = {}

    def get_scan_progress(self, creature_species: str, is_alive: bool) -> float:
        if creature_species not in self.research_data:
            return 0.0
        state_key = 'alive' if is_alive else 'dead'
        return self.research_data[creature_species][state_key]

    def update_scan_progress(self, creature_species: str, is_alive: bool, progress: float) -> None:
        if creature_species not in self.research_data:
            self.research_data[creature_species] = {'alive': 0.0, 'dead': 0.0}
        state_key = 'alive' if is_alive else 'dead'
        max_progress = 100.0 if is_alive else 50.0
        progress = min(progress, max_progress)
        current = self.research_data[creature_species][state_key]
        self.research_data[creature_species][state_key] = max(current, progress)

    def get_total_species_progress(self, creature_species: str) -> float:
        if creature_species not in self.research_data:
            return 0.0
        data = self.research_data[creature_species]
        progress = max(data['alive'], data['dead'])
        # cap at 50% until an alive creature of this species has been scanned
        if data['alive'] == 0.0:
            progress = min(progress, 50.0)
        return progress

    def get_all_species(self) -> list[str]:
        return list(self.research_data.keys())


    def is_species_complete(self, species: str) -> bool:
        return self.get_total_species_progress(species) >= 100.0


    def get_completion_percentage(self, required_species: list[str]) -> float:
        if not required_species:
            return 0.0

        completed = 0
        for s in required_species:
            if self.is_species_complete(s):
                completed += 1

        return (completed / len(required_species)) * 100.0
