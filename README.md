# 🌊The Deep
The Deep is a 2D side-view underwater exploration game. You play as a lone researcher dispatched to Kepler, a newly discovered and entirely aquatic alien planet. Sent with limited resources, you must dive into the unknown, research alien marine life, harvest resources, and upgrade your gear to survive the crushing depths and hostile predators.

## 🚀 How to Run
Ensure you have Python and the required dependencies (such as Pygame) installed. To launch the game, run the following command in your terminal:

```Bash
python main.py
```

## 🔄 Core Gameplay Loop
Every dive is a delicate balance of risk, reward, and resource management. The gameplay cycle consists of:

- Dive: Leave the safety of the spaceship and enter the ocean.
- Explore & Research: Navigate hazards and use the scanner to document alien wildlife.
- Survive & Harvest: Fend off hostile predators and harvest resources.
- Return: Get back to the spaceship before oxygen runs out or the pressure crushes you.
- Upgrade: Trade resources at the base to purchase better gear, allowing for deeper exploration on the next run.

## 🌴 File Structure
# The Deep - Project Structure

```
the_deep/
├── assets
├── config.py
├── data
├── main.py
├── README.md
└── src
    ├── entities
    │   ├── base_creature.py
    │   ├── creature_aggressive.py
    │   ├── creature_passive.py
    │   ├── item.py
    │   └── player.py
    ├── game.py
    ├── states
    │   ├── base_state.py
    │   ├── homebase.py
    │   ├── start_screen.py
    │   └── underwater.py
    ├── ui
    │   ├── components
    │   │   └── button.py
    │   ├── hud.py
    │   └── menus
    │       └── base_menu.py
    └── utils
        ├── camera.py
        ├── data_maanger.py
        ├── physics_service.py
        └── tile_map.py
```


- **Entry Point**: `main.py`
- **Game Loop**: `src/game.py` (GameManager class)
- **State Management**: `src/states/` (BaseState, StartScreen, UnderwaterState, HomebaseState)
- **Entities**: `src/entities/` (Creature, Item classes)
- **UI**: `src/ui/components/` (Button component)
