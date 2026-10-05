#pragma once
#include <string>

class Player {
private:
    std::string name;
    int health;

public:
    Player(std::string n, int h);

    void takeDamage(int damage);
    bool isAlive() const;
    std::string getName() const;
    int getHealth() const;
};