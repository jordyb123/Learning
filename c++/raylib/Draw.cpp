#include "raylib.h"
#include "Draw.h"

void DrawWorld(const GameState& game) {

    DrawRectangle(-1000, -1000, 2000, 2000, DARKGREEN);
    DrawRectangle(100, 100, 100, 100, BLUE);
    DrawRectangle(game.player.x, game.player.y, 50, 50, RED);
    DrawRectangle(850, 700, 100, 100, LIGHTGRAY);
    

    for (const Bullet& bullet : game.bullets) {
        if (bullet.active) {
            DrawRectangle(bullet.x, bullet.y, 10, 10, BLACK);
        }
    }

    for (const Enemy& enemy : game.enemies) {
        if (enemy.alive) {
            DrawRectangle(enemy.x, enemy.y, 40, 40, PURPLE);
            DrawText(TextFormat("%d", enemy.health), enemy.x, enemy.y - 20, 18, WHITE);
        }
    }

    for (const Pickup& pickup : game.pickups) {
        if (pickup.active) {
            DrawRectangle(pickup.x, pickup.y, 20, 20, GOLD);
        }
    }

    for (const WeaponPickup& pickup : game.weaponPickups) {
        if (pickup.active) {
            DrawRectangle(pickup.x, pickup.y, 24 ,24, ORANGE);
        }
    }
}

void DrawHud(const GameState& game) {
    DrawText(TextFormat("Weapon: %s", game.inventory[game.activeWeaponIndex].name), 20, 160, 20, BLACK);
    DrawText(TextFormat("Health: %d", game.player.health), 20, 20 , 20, BLACK);
    DrawText(TextFormat("Score: %d", game.score), 20, 110, 20, BLACK);
    DrawText(TextFormat("Supplies: %d", game.suppliesCollected), 20, 130, 20, BLACK);

    if (game.isReloading) {
        DrawText("Reloading...", 20, 80, 20, ORANGE);
    }
    DrawText (TextFormat("Ammo: %d / %d", game.inventory[game.activeWeaponIndex].currentAmmo, game.inventory[game.activeWeaponIndex].magazineSize), 20, 50, 20, BLACK);
    if (game.player.health <= 0) {
        DrawText("GAME OVER", 300, 200, 40, RED);
    }

    if (game.runComplete) {
        DrawText("Extracted!!!", 300, 200, 40, RED);
    }
}