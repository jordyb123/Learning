# C++ and Raylib Learning Plan

## Goal
Build a 2D top-down shooter with an open-world extraction feel, then move toward 3D later.

## Current Progress
- [x] Variables and basic types
- [x] Console input and output
- [x] `if` and `else`
- [x] `while` and `for` loops
- [x] Functions
- [x] `bool`
- [x] `std::vector`
- [x] `struct`
- [x] References
- [x] Small health and player exercises

## Phase 1: Practical C++
- [x] Improve the health project (damage, armor, healing clamps)
- [x] Use vectors of players and enemies
- [x] Write functions that modify structs
- [x] Learn `enum` for weapons and game states
- [x] Learn `switch` statements
- [x] Learn classes (fields, methods, constructors, `const` methods)
- [x] Learn encapsulation (private fields, public getters)
- [x] Organize code into multiple files (`Player.h` / `Player.cpp`)
- [x] Combine classes with `std::vector`
- [ ] Save and load basic data
- [ ] Practice debugging (deferred, revisit as needed)

**Project:** Text-based combat game with a player, enemies, weapons, health, damage, and a simple inventory. (Core combat loop done; save/load still pending.)

## Phase 2: Raylib Basics
- [x] Install and configure raylib
- [x] Open a window
- [x] Draw shapes
- [x] Understand the game loop
- [x] Read keyboard input
- [x] Move a player
- [x] Practice player boundaries
- [x] Add a camera
- [x] Draw multiple enemies
- [x] Add collision
- [x] Add bullets with mouse aiming
- [x] Use `GetFrameTime()` for movement
- [x] Normalize movement to keep diagonal speed consistent

**Project:** Basic top-down shooter prototype.

## Phase 3: Core Game Systems
- [x] Player and enemy health
- [x] Damage and damage cooldown
- [x] Weapon cooldowns
- [x] Ammunition and timed reload
- [x] Basic UI for health, ammo, reload status, enemy health, and score
- [x] Basic enemy behavior (chasing the player)
- [x] Supply pickups and a collected-supplies counter
- [~] Weapon pickups, pickup/drop interaction, and a basic carried-weapon vector
- [ ] Separate carried inventory from two reassignable equipped weapon slots
- [ ] Build a menu to assign carried weapons to the equipped slots
- [ ] Tile-based maps
- [ ] Multiple areas

**Project:** Single-map survival/extraction prototype. Waves are optional, not a required direction. The carried inventory can hold multiple weapons; two equipped slots are separate from it and are not permanently tied to specific weapon types.

## Phase 4: First Vertical Slice
Build one short extraction run:

- [~] One test map
- [x] One player
- [x] One basic weapon
- [x] One basic enemy type
- [~] Loot (supply and weapon pickup prototypes)
- [~] Inventory (weapon list prototype; equipment slots and menu remain)
- [x] Health and ammo
- [x] One objective (collect supplies)
- [x] Extraction point and success state
- [ ] Save and load

## Phase 5: Larger C++ Concepts
Learn these when the projects need them:

- [x] Classes
- [ ] Pointers
- [ ] Smart pointers
- [x] Header and source files
- [ ] Game states
- [ ] Resource management
- [x] Larger project structure (`GameState`, headers, and separate draw/update source files)

## Phase 6: 3D Later
After becoming comfortable with 2D:

- [ ] 3D coordinates and vectors
- [ ] 3D camera
- [ ] Models and textures
- [ ] Lighting
- [ ] Physics and collision
- [ ] 3D level design

## Lesson Pattern
Each lesson should follow this order:

1. Learn one concept.
2. Make one small code change.
3. Compile and run it.
4. Test the result.
5. Explain what happened.
6. Continue to the next concept.

## Immediate Next Step
Refine the weapon data model so carried weapons are distinct from two equipped slots. Either equipped slot can hold any carried weapon; neither slot is permanently a pistol or rifle. After the model works, build a menu for assigning and swapping weapons between inventory and those slots. Do not add a Q-key cycle as the intended selection system.
