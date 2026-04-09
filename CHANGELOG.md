# Changelog

[v0.1.0] - M1: Foundation Complete 
[X]-[C1] Define creature species (David)
[X]-[C2] Define depth progression difficulty (David)
[X]-[C3] Define upgrade progression (Jairo)
[ ]-[C4] Define economy and upgrade costs (Daniel)
[X]-[P1] Underwater state and game loop (Jairo)
[X]-[P2] Core player functionality {
        [X] - Player can move (Jairo)
        [X] - Player can sprint (Jairo)
        [X] - Player movement physics simulate the environment with acceleration and drag (Jairo)
}
[ ]-[G1] GUI placeholder assets (Daniel)
[X]-[G5] Environment assets (Jairo)
[X] - Fix: entity abstract class is weird. better call it a thing from which items, player and creatures inherit. Then also have an abstract class called MovingThings from which only player and creatures inherit and get their movement from there. (Jairo)
[X] - Fix: Class diagram architecture is not reflecting codebase, as expected, would be nice if we fix it to avoid confusions and include the definitive methods and attributes that are already there. (Jairo)
[X] - (Will actively work on it every week) Fix: Tasks and their timelines are poorly designed (Some are short and multiple could be combined into 1 but take "1 week"), others are a big part of the project but apparently are missing (Physics Service Hello??), would be good to fix this before continuing with the project. (Everyone)



[v0.2.0] - M2: Main Systems Complete 
[X]-[NONE] Tilemap loading system {
        [X] - Program adding static map without collisions. (Jairo)
        [] - Implement collision checking with the physics service(Jairo)
        [X] - fix: avoid rendering the whole map every second. We need to implement render distance. Performance hoooorrible with the bigger map now. (Jairo)
}
[ ]- [NONE] Collision handling {
        [] - Creating physics service
        [] - Handling player collisions with map
        [] - Handling creature collisions with map
        [] - Handling player-creature collision
}

[X]-[P3] Camera system (Jairo)
[X]-[P4] Oxygen system (Jairo)
[ ]-[P6] Depth tracking system
[ ]-[P14] Inventory system
[]-[G3] Passive creature sprites {
        [X] - Standstill image (David)
        [] - Animations
}
[]-[G4] Hostile creature sprites {
        [X] - Standstill image (David)
        [] - Animations
}
[X]-[P7] General creature functionality {
        [X] - All creatures can move (David)
        [X] - Passive and aggresive creatures work differently (David)
        [] - Fix: Update class diagram to use a factory design pattern as it makes more sense for creature spawning in the long run.
        [] - Fix: Implement the factory in code.
        [] - Fix: Update the creature's movement to have thrust and acceleration, using the general drag flag from settings.
}
[ ]-[G2] Player sprite & animations

[]-Fix: Current code does not reflect class diagram, please update the current entities to use Thing and MovingThing.
[]-Fix: It's kind of wrong that the player is handling his own physics when moving, would be nice that if calculated in the PhysicsService instead of there so the player has no need to access it's drag, this will also applies to all things that move.
[X]-Bug: Camera zoom absolutely destroys performance. Needs fixing (Jairo)
[X]-Bug: Edges have a little gap when the player moves. This is very easy to fix, just extend how much map is being blitted by like 5 px on all edges. This is happening because a of floating number mistmatches between the player position and the camera. Jairo left this task for anyone else who wants to take is as a test of whether someone ever reads the CHANGELOG or not. (Jairo) Ok so I fixed it myself by accident while fixing the zoom in the camera. No idea as to why but if it works it works.
[]-Fix: Inconsistency in inheritance and classes that must be cleared up in entities. All entities should apply the same movement and thrust and drag and such. Also, all Entities should have a mass and such attributes initialized in the base_entity even if its empty and later overwritten by what is in the config in the classes that inherit this.


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