#pragma once
#include "raylib.h"
#include "GameTypes.h"

void UpdateEnemies(GameState& game, float deltaTime);
void UpdateBullets(GameState& game, float deltaTime);
void UpdatePlayer(GameState& game, float deltaTime);
void UpdateWeapons(GameState& game, float deltaTime, const Camera2D& camera);
void UpdateObjectives(GameState& game);
void InitGame(GameState& game, Camera2D& camera);