#include <iostream>
#include <string>

class Player {
private: 
    std::string name;
    int health;

public:
    Player(std::string n, int h) {
        name = n;
        health = h;
    }

    void takeDamage(int damage) {
        health -= damage;
        if (health < 0) {
            health = 0;
        }
    }

    bool isAlive() const {
        return health > 0;
    }

    std::string getName() const {
        return name;
    }

    int getHealth() const {
        return health;
    }
};

int main() {
    Player player("Alpha", 100);

    std::cout << player.getName() << " health: " << player.getHealth() << "\n";

    player.takeDamage(25);

    std::cout << player.getName() << " health: " << player.getHealth() << "\n";

    if (player.isAlive()) {
        std::cout << "Alive\n";
    } else {
        std::cout << "dead\n";
    }

    Player playerTwo("Bravo", 100);

    std::cout << playerTwo.getName() << " health: " << playerTwo.getHealth() << "\n";

    playerTwo.takeDamage(100);

    std::cout << playerTwo.getName() << " health: " << playerTwo.getHealth() << "\n";



    if (playerTwo.isAlive()) {
        std::cout << "Alive\n";
    } else {
        std::cout << "dead\n";
    }

    return 0;
}