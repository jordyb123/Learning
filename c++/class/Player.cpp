#include "Player.h"

Player::Player(std::string n, int h) {
    name = n;
    health = h;
}

void Player::takeDamage(int damage) {
    health -= damage;
    if (health < 0) {
        health = 0;
    }
}

bool Player::isAlive() const {
    return health > 0;
}

std::string Player::getName() const {
    return name;
}

int Player::getHealth() const {
    return health;
}