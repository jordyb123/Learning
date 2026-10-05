#pragma once

struct Weapon {
    const char* name;
    float bulletSpeed;
    int damage;
    int magazineSize;
    float fireCooldown;
    float reloadDuration;
    int currentAmmo = magazineSize;
};

struct WeaponPickup {
    float x;
    float y;
    Weapon weapon;
    bool active;
};