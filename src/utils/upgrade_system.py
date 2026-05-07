class UpgradeSystem:
    # Owns all upgrade data and logic
    def __init__(self, player) -> None:
        self.player = player
        self.order = ["weapon", "scanner", "suit"]
        self.labels = {"weapon": "WEAPON", "scanner": "SCANNER", "suit": "SUIT"}
        self.costs = {
            "weapon": [200, 350, 550, 800, 1100],
            "scanner": [200, 350, 550, 800, 1100],
            "suit": [200, 350, 550, 800, 1100],
        }
        self.max_level = 5
        self._ensure_state()
        self.apply_effects()

    def get_preview(self, key: str) -> dict:
        level = self.player.upgrade_levels.get(key, 0)
        capped_level = min(level, self.max_level)
        can_upgrade = capped_level < self.max_level
        next_level = capped_level + 1 if can_upgrade else capped_level
        cost = self.costs[key][capped_level] if can_upgrade else 0
        money = self.player.inventory.get("pesos", 0)

        if key == "weapon":
            current_value = self._weapon_damage_for_level(capped_level)
            next_value = self._weapon_damage_for_level(next_level)
            description = f"Damage: {current_value} -> {next_value}" if can_upgrade else f"Damage: {current_value} (MAX)"
        elif key == "scanner":
            current_value = self._scanner_rate_for_level(capped_level)
            next_value = self._scanner_rate_for_level(next_level)
            description = f"Scan speed: x{current_value:.2f} -> x{next_value:.2f}" if can_upgrade else f"Scan speed: x{current_value:.2f} (MAX)"
        else:
            current_value = self._suit_depth_for_level(capped_level) // 16
            next_value = self._suit_depth_for_level(next_level) // 16
            description = f"Depth limit: {current_value}m -> {next_value}m" if can_upgrade else f"Depth limit: {current_value}m (MAX)"

        return {
            "key": key,
            "label": self.labels[key],
            "level": capped_level,
            "next_level": next_level,
            "cost": cost,
            "pesos": money,
            "can_upgrade": can_upgrade,
            "description": description,
        }

    def buy(self, key: str) -> str:
        preview = self.get_preview(key)
        if not preview["can_upgrade"]:
            return "Already max level"
        if preview["pesos"] < preview["cost"]:
            return "Not enough $"

        self.player.inventory["pesos"] -= preview["cost"]
        self.player.upgrade_levels[key] += 1
        self.apply_effects()
        return f"{self.labels[key]} upgraded!"

    def apply_effects(self) -> None:
        weapon_level = self.player.upgrade_levels.get("weapon", 0)
        scanner_level = self.player.upgrade_levels.get("scanner", 0)
        suit_level = self.player.upgrade_levels.get("suit", 0)

        # Stored on the player so underwater can apply these values to holdables on enter
        self.player.weapon_upgrade_damage = self._weapon_damage_for_level(weapon_level)
        self.player.scanner_upgrade_rate = self._scanner_rate_for_level(scanner_level)
        self.player.max_depth_limit = self._suit_depth_for_level(suit_level)

    def _ensure_state(self) -> None:
        if not hasattr(self.player, "upgrade_levels"):
            self.player.upgrade_levels = {key: 0 for key in self.order}
        if "pesos" not in self.player.inventory:
            self.player.inventory["pesos"] = 0

    def _weapon_damage_for_level(self, level: int) -> int:
        return 10 + level * 4

    def _scanner_rate_for_level(self, level: int) -> float:
        return 1.0 + level * 0.20

    def _suit_depth_for_level(self, level: int) -> int:
        # 16 pixels = 1 meter, Level 0 = 100m, +30m per level
        return (100 + level * 30) * 16
