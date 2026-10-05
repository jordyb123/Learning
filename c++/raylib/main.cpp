#include "Draw.h"
#include "raylib.h"
#include "raymath.h"
#include "GameTypes.h"
#include "Weapon.h"
#include "Update.h"
#include <vector>


int main() {
    InitWindow(800, 450, "My First Window");

    GameState game;
    Camera2D camera = { 0 };
    InitGame(game, camera);

    while (!WindowShouldClose()) {

        float deltaTime = GetFrameTime();
        
        if (!game.runComplete && game.player.health > 0) {

        UpdatePlayer(game, deltaTime);
        UpdateWeapons(game, deltaTime, camera);
        UpdateObjectives(game);
        UpdateBullets(game, deltaTime);
        UpdateEnemies(game, deltaTime);

        camera.target = { game.player.x + 25, game.player.y + 25 };

        }   
        BeginDrawing();
        ClearBackground(RAYWHITE);

        BeginMode2D(camera);
        DrawWorld(game);
        EndMode2D();

        DrawHud(game);
        EndDrawing(); 
    }

    CloseWindow();

    return 0;
} 