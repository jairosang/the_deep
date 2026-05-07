class ShopSystem:
    # Counts creatures in player's buffer_inventory and sells them for pesos
    def __init__(self, player) -> None:
        self.player = player
        self.prices = {
            "fish": 8,
            "blue-fish": 14,
            "fish-dart": 18,
            "fish-big": 28,
            "anglerfish": 55,
        }
        self.labels = {
            "fish": "Small Fish",
            "blue-fish": "Blue Fish",
            "fish-dart": "Dart Fish",
            "fish-big": "Big Fish",
            "anglerfish": "Anglerfish",
        }
        if "pesos" not in self.player.inventory:
            self.player.inventory["pesos"] = 0

    def get_listings(self) -> list[dict]:
        # Group items in buffer inventory by name and returns display information
        counts: dict[str, int] = {}
        for item in self.player.buffer_inventory:
            counts[item.name] = counts.get(item.name, 0) + 1

        listings = []
        for species, count in counts.items():
            price = self.prices.get(species, 5)
            listings.append({
                "species": species,
                "label": self.labels.get(species, species),
                "amount": count,
                "price": price,
                "total": price * count,
            })
        listings.sort(key=lambda entry: entry["label"])
        return listings

    def get_total_value(self) -> int:
        return sum(listing["total"] for listing in self.get_listings())

    def get_wallet(self) -> int:
        return self.player.inventory.get("pesos", 0)

    def sell_all(self) -> str:
        listings = self.get_listings()
        if not listings:
            return "Nothing to sell."

        total_value = self.get_total_value()
        total_count = sum(listing["amount"] for listing in listings)

        self.player.inventory["pesos"] = self.get_wallet() + total_value
        self.player.buffer_inventory.clear()

        return f"Sold {total_count} item(s) for ${total_value}."
