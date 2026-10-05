#include <iostream>
#include <vector>
#include "Player.h"

int main() {

    std::vector<Player> players;

    players.push_back(Player("Alpha", 100));
    players.push_back(Player("Bravo", 80));
    players.push_back(Player("Charlie", 60));

    for (Player& player : players) {
        player.takeDamage(30);
        std::cout << player.getName() << " health: " << player.getHealth() << "\n";

        if (player.isAlive()) {
            std::cout << player.getName() << " is alive\n";
        } else {
            std::cout << player.getName() << " is dead\n";
        }
    }
    
    return 0;
}