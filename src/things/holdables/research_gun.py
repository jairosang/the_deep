import pygame
from .base_holdable import Holdable
from ..shootables.ray import Ray
from things import Creature
from utils import ResearchDatabase
from pathlib import Path

class ResearchGun(Holdable):

    def __init__(self, research_database: ResearchDatabase | None = None) -> None:
        self.name = "Research Gun"
        self.description = "Scanner used to analyze underwater creatures"
        self.color = (90, 200, 160)
        self.image_path = Path("./assets/holdables/research_gun_asset.png")
        self.scan_rate = 1.0
        self.range = 200
        self.cooldown_s = 0.25
        self.is_available = False
        self.continuous = True
        self.shoot_recoil = 20

        self.research_database = research_database
        self.scan_timers: dict = {}  # creature -> how long we've been scanning it
        self.beam_creatures: set = set()  # creatures currently in the beam

        super().__init__()

    def set_research_database(self, research_database):
        self.research_database = research_database

    def shoot(self, pos: tuple[int, int]) -> bool:
        if not self.shootables:
            self.shootables.append(Ray(self.player_center, self.range))
        return True

    def update_shootables(self, dt: float, creatures: list, world_rect=None, get_tiles=None) -> tuple[list, list]:
        if not self.is_active:
            # gun turned off — kill the beam and save any partial scan progress
            for ray in self.shootables:
                ray.is_spent = True
            for c in list(self.scan_timers):
                self._save_progress(c)
            self.scan_timers.clear()
            self.beam_creatures = set()
            return [], [ray for ray in self.shootables if ray.is_spent]

        ray = self.shootables[0] if self.shootables else None
        if ray is None:
            return [], []

        target_pos = self._last_mouse_pos or self.player_center
        ray.update(self.rect.center, target_pos)

        in_beam = ray.get_creatures_in_beam(creatures)

        # only scan the closest creature of each species
        nearest_per_species: dict = {}
        for c in in_beam:
            dist_sq = (pygame.math.Vector2(c.rect.center) - self.player_center).length_squared()
            if c.species not in nearest_per_species or dist_sq < nearest_per_species[c.species][1]:
                nearest_per_species[c.species] = (c, dist_sq)
        beam_set = {c for c, _ in nearest_per_species.values()}
        self.beam_creatures = beam_set

        # save progress for creatures that left the beam
        for c in list(self.scan_timers):
            if c not in beam_set:
                self._save_progress(c)
                del self.scan_timers[c]

        # tick scan timers for creatures still in beam
        for c in beam_set:
            if c not in self.scan_timers:
                self.scan_timers[c] = self._get_saved_time(c)
            self.scan_timers[c] += dt
            self._check_scan_done(c)

        return [], []

    def _get_saved_time(self, creature: Creature) -> float:
        # converts stored progress % back to seconds so scanning feels continuous
        if self.research_database is None:
            return 0.0
        is_alive = creature.health > 0
        saved = self.research_database.get_scan_progress(creature.species, is_alive)
        return saved / 100.0 * creature.scan_duration

    def _save_progress(self, creature: Creature) -> None:
        # called when a creature leaves the beam or gun turns off
        if self.research_database is None:
            return
        elapsed = self.scan_timers.get(creature, 0.0)
        if elapsed <= 0:
            return
        is_alive = creature.health > 0
        progress = min(100.0, elapsed / creature.scan_duration * 100.0)
        if not is_alive:
            progress = min(50.0, progress)  # dead scans cap at 50%
        self.research_database.update_scan_progress(creature.species, is_alive, progress)

    def _check_scan_done(self, creature: Creature) -> None:
        if self.research_database is None:
            return
        species = creature.species
        is_alive = creature.health > 0
        duration = creature.scan_duration
        if self.scan_timers.get(creature, 0.0) >= duration:
            progress = 50.0 if not is_alive else 100.0
            self.research_database.update_scan_progress(species, is_alive, progress)
            self.scan_timers.pop(creature)

    def draw_things_on_screen(self, surface) -> None:
        if self.is_active:
            for ray in self.shootables:
                ray.draw(surface)

        for creature in self.beam_creatures:
            is_complete = (
                self.research_database is not None and
                self.research_database.get_total_species_progress(creature.species) >= 100.0
            )
            if is_complete:
                self._draw_check(surface, creature.rect)
            else:
                timer = self.scan_timers.get(creature, 0.0)
                progress = min(100.0, timer / creature.scan_duration * 100.0)
                if creature.health <= 0:
                    progress = min(50.0, progress)
                self._draw_scan_bar(surface, creature.rect, progress)

    def _draw_check(self, surface, target_rect) -> None:
        cx = target_rect.centerx
        cy = int(target_rect.top - 19)
        size = 7
        p1 = (cx - size, cy)
        p2 = (cx - size // 3, cy + size - 2)
        p3 = (cx + size, cy - size + 2)
        pygame.draw.lines(surface, (0, 255, 100), False, [p1, p2, p3], 3)

    def _draw_scan_bar(self, surface, target_rect, progress: float) -> None:
        bar_width, bar_height = 60, 12
        bar_x = int(target_rect.centerx - bar_width / 2)
        bar_y = int(target_rect.top - 25)
        pygame.draw.rect(surface, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 100),
                         (bar_x, bar_y, int(progress / 100.0 * bar_width), bar_height))
        pygame.draw.rect(surface, (0, 255, 150), (bar_x, bar_y, bar_width, bar_height), 2)
