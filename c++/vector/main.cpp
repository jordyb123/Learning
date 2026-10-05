#include <iostream>
#include <vector>

int main() {
    std::vector<int> enemyHealth = {100, 50, 25};
    enemyHealth.push_back(80);
    enemyHealth.push_back(30);

    for (int health : enemyHealth) {
        std::cout << health << "\n";
    }

    return 0;
}