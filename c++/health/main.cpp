#include <iostream>

int applyDamage(int health, int damage) {

    health = health - damage;

    if (health < 0) {
        health = 0;
    }
    return health;
}

int main() {
    int health;
    int damage;

    
    std::cout << "What is your current health?\n";
    std::cin >> health;
    std::cout << "Current health: " << health << "\n";
    std::cout << "How much damage did you take ? \n";
    std::cin >> damage;

    health = applyDamage(health, damage);

    if (health <= 0) {
        std::cout << "You died!\n";
        
    } else {
        std::cout << "Health left: " << health << "\n";
        if (health <= 20){
            std::cout << "Critical\n";
        }
    }

    return 0;
}