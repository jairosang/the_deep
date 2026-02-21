# Changelog

[v0.1.0] - M1: Foundation Complete 
[X]-[C1] Define creature species
[X]-[C2] Define depth progression difficulty
[X]-[C3] Define research progression
[ ]-[C4] Define economy and upgrade costs
[X]-[P1] Underwater state and game loop
[ ]-[P2] Core player functionality {
        [X] - Player can move
        [X] - Player can sprint
        [] - Player has holdables (weapon, research gun, harpoon)
        [] - Player can switch between holdables
        [] - Holdables can do things
}
[ ]-[G1] GUI placeholder assets
[] - Fix: entity abstract class is weird. better call it a thing from which items, player and creatures inherit. Then also have an abstract class called MovingThings from which only player and creatures inherit and get their movement from there.
[] - Fix: Class diagram architecture is not reflecting codebase, as expected, would be nice if we fix it to avoid confusions and include the definitive methods and attributes that are already there. 



[v0.2.0] - M2: Main Systems Complete 
[ ]-[P3] Camera system
[ ]-[P4] Oxygen system
[ ]-[P6] Depth tracking system
[ ]-[P14] Inventory system
[ ]-[G3] Passive creature sprites
[ ]-[G4] Hostile creature sprites
[ ]-[G5] Environment assets
[ ]-[P7] Passive creature functionality
[ ]-[G2] Player sprite & animations




[v0.3.0] - M3: Economy & States Complete 
[ ]-[P15] Economy system
[ ]-[P16] Homebase state
[ ]-[P5] Health system
[ ]-[G6] HUD assets





[v0.4.0] - M4: Creatures & Research Complete 
[ ]-[P8] Hostile creature functionality
[ ]-[P9] Creature health and elimination
[ ]-[P10] Research scanning functionality
[ ]-[P11] Research persistence
[ ]-[P17] Upgrade system
[ ]-[P20] Integrate UI functionality





[v0.5.0] - M5: Combat Complete 
[ ]-[P12] Harpoon functionality
[ ]-[P13] Combat weapon functionality
[ ]-[P19] Save/load functionality
[ ]-[S1] Underwater ambient soundtrack
[ ]-[S2] Tool sound effects
[ ]-[S3] Creature sound effects
[ ]-[S4] UI sound effects





[v0.6.0] - M6: Integration & Submission 
[ ]-[P21] Integrate Sound functionality
[ ]-[Testing] Final testing and bug fixes