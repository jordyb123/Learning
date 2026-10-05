#pragma once
#include <vector>
#include "Weapon.h"

struct Player {
    float x;
    float y;
    int health;
    float speed;
};

struct Bullet {
    float x;
    float y;
    float speed;
    bool active;
    float velocityX;
    float velocityY;
    int damage;
};

struct Enemy {
    float x;
    float y;
    bool alive;
    float speed;
    int health;
};

struct Pickup {
    float x;
    float y;
    bool active;
};

constexpr int mapWidth = 20;
constexpr int mapHeight = 20;
constexpr int tileSize = 100;

enum class TileType {
    Ground,
    Wall
};

struct TileMap {
    TileType tiles[mapHeight][mapWidth]{};
};

struct GameState {
    Player player{400, 225, 100, 200.f};
    std::vector<Enemy> enemies;
    std::vector<Bullet> bullets;
    std::vector<Pickup> pickups;
    std::vector<WeaponPickup> weaponPickups;
    std::vector<Weapon> inventory;
    int activeWeaponIndex = 0;
    int score = 0;
    int suppliesCollected = 0;
    float damageCooldown = 0.0f;
    float shootCooldown = 0.0f;
    bool isReloading = false;
    float reloadTimer = 0.0f;
    bool runComplete = false;
    TileMap map;
};

