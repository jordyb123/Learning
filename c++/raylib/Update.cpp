#include "raylib.h"
#include "raymath.h"
#include "Update.h"

void UpdateEnemies(GameState& game, float deltaTime) {
    game.damageCooldown -= deltaTime;
    
    if (game.damageCooldown < 0) {
    game.damageCooldown = 0;
    }


    for (Enemy& enemy : game.enemies) {
            if (!enemy.alive) continue;

            if (CheckCollisionRecs({game.player.x, game.player.y, 50, 50}, {enemy.x, enemy.y, 40, 40}) && game.damageCooldown <= 0) {
                game.player.health -= 10;
                game.damageCooldown = 1.0f;
            }

            if (game.player.health <= 0) {
                game.player.health = 0;
            }
        }

    for (Enemy& enemy : game.enemies) {
            if (!enemy.alive) continue;
            if (enemy.x < game.player.x) {
                enemy.x += enemy.speed * deltaTime;
            }
            if (enemy.x > game.player.x) {
                enemy.x -= enemy.speed * deltaTime;
            }
            if (enemy.y < game.player.y) {
                enemy.y += enemy.speed * deltaTime;
            }
            if (enemy.y > game.player.y) {
                enemy.y -= enemy.speed * deltaTime;
            }

        }
}

void UpdateBullets(GameState& game, float deltaTime) {
    for (Bullet& bullet : game.bullets) {
            if (bullet.active) {
                bullet.x += bullet.velocityX * bullet.speed * deltaTime;
                bullet.y += bullet.velocityY * bullet.speed * deltaTime;

                if (bullet.x < -1000 ||
                    bullet.x > 2000 ||
                    bullet.y < -1000 ||
                    bullet.y > 2000) {
                    bullet.active = false;
                }
            }
        }

    for (Bullet& bullet : game.bullets) {
        if (!bullet.active) continue;
        
        for (Enemy& enemy : game.enemies) {
            if (!enemy.alive) continue;

            if (CheckCollisionRecs({bullet.x, bullet.y, 10, 10}, {enemy.x, enemy.y, 40, 40})) {
                bullet.active = false;
                enemy.health -= bullet.damage;
                if (enemy.health <= 0) {
                    enemy.alive = false;
                    game.score += 100;
                }
            }
        }
    }

    for (int i = game.bullets.size() - 1; i >= 0; i--) {
        if (!game.bullets[i].active) {
            game.bullets.erase(game.bullets.begin() + i);
        }
    }
}

void UpdatePlayer(GameState& game, float deltaTime) {
    Vector2 movement = { 0.0f, 0.0f };

    // player movement
    if (IsKeyDown(KEY_D)) {
        movement.x += 1.0f;
    }
    if (IsKeyDown(KEY_A)) {
        movement.x -= 1.0f;
    }
    if (IsKeyDown(KEY_W)) {
        movement.y -= 1.0f;
    }
    if (IsKeyDown(KEY_S)) {
        movement.y += 1.0f;
    }

    if (movement.x != 0.0f || movement.y != 0.0f) {
        movement = Vector2Normalize(movement);
    }

    game.player.x += movement.x * game.player.speed * deltaTime;
    game.player.y += movement.y * game.player.speed * deltaTime;
}

void UpdateWeapons(GameState& game, float deltaTime, const Camera2D& camera) {
    for (WeaponPickup& pickup : game.weaponPickups) {
        if (!pickup.active) continue;

        if (CheckCollisionRecs({game.player.x, game.player.y, 50, 50}, {pickup.x, pickup.y, 24, 24}) && IsKeyPressed(KEY_E)) {
            game.inventory.push_back(pickup.weapon);
            pickup.active = false;
        }
    }

    if (IsKeyPressed(KEY_ONE) && game.inventory.size() > 1) {
        game.activeWeaponIndex = 1;
        game.isReloading = false;
    }

    if (IsKeyPressed(KEY_TWO) && game.inventory.size() > 2) {
        game.activeWeaponIndex = 2;
        game.isReloading = false;
    }

    if (IsKeyPressed(KEY_G) && game.activeWeaponIndex != 0) {
        game.weaponPickups.push_back({game.player.x, game.player.y, game.inventory[game.activeWeaponIndex], true});
        game.inventory.erase(game.inventory.begin() + game.activeWeaponIndex);

        if (game.activeWeaponIndex >= game.inventory.size()) {
            game.activeWeaponIndex = game.inventory.size() - 1;
        }
        game.isReloading = false;
    }
    Weapon& activeWeapon = game.inventory[game.activeWeaponIndex];

    game.shootCooldown -= deltaTime;

 
    if (game.shootCooldown < 0) {
        game.shootCooldown = 0;
    }

    if (IsKeyDown(KEY_SPACE) && game.shootCooldown <= 0.0f && activeWeapon.currentAmmo > 0 && !game.isReloading) {

    Vector2 mouseWorld = GetScreenToWorld2D(GetMousePosition(), camera);

    Vector2 playerCenter = {
        game.player.x + 25, game.player.y + 25
    };

    Vector2 direction = Vector2Normalize(
        Vector2Subtract(mouseWorld, playerCenter)
    );
    
    game.bullets.push_back({playerCenter.x, playerCenter.y, activeWeapon.bulletSpeed, true, direction.x, direction.y, activeWeapon.damage});
    activeWeapon.currentAmmo --;
    game.shootCooldown = activeWeapon.fireCooldown;

    }

    if (IsKeyPressed(KEY_R) && activeWeapon.currentAmmo < activeWeapon.magazineSize && !game.isReloading) {
        game.isReloading = true;
        game.reloadTimer = activeWeapon.reloadDuration;
    }

    if (game.isReloading) {
        game.reloadTimer -= deltaTime;

        if (game.reloadTimer <= 0.0f) {
            activeWeapon.currentAmmo = activeWeapon.magazineSize;
            game.isReloading = false;
        }
    }
}

void UpdateObjectives(GameState& game) {
     for (Pickup& pickup : game.pickups) {
            if (pickup.active) {

                if (CheckCollisionRecs({game.player.x, game.player.y, 50, 50}, {pickup.x, pickup.y, 20, 20})) {
                    pickup.active = false;
                    game.suppliesCollected += 1;
                }
            }
        }

    bool touchingExtraction = CheckCollisionRecs({game.player.x, game.player.y, 50, 50}, {850, 700, 100, 100});
    if (touchingExtraction && game.suppliesCollected > 0) {
        game.runComplete = true; 
    }
}

void InitGame(GameState& game, Camera2D& camera) {
    Weapon unarmed{"Unarmed", 0.0f, 0, 0, 0.0f, 0.0f};
    Weapon pistol{"Pistol", 300.0f, 1, 12, 0.2f, 1.2f};
    Weapon rifle{"Rifle", 450.0f, 2, 30, 0.1f, 2.0f};

    game.inventory = {unarmed, pistol};
    game.activeWeaponIndex = 1;

    camera.target = { game.player.x, game.player.y };
    camera.offset = { 400, 225 };
    camera.zoom = 1.0f;

    int randomX = GetRandomValue(500, 700);
    int randomY = GetRandomValue(250, 400);

    game.enemies.push_back({300, 300, true, 30.0f, 3});
    game.enemies.push_back({500, 150, true, 30.0f, 3});
    game.enemies.push_back({700, 400, true, 30.0f, 3});

    game.pickups.push_back({600, 250, true});

    game.weaponPickups.push_back({static_cast<float>(randomX), static_cast<float>(randomY), rifle, true});
}