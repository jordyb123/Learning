#include <iostream>
#include <string>
#include <vector>

enum class Weapon {
    Pistol,
    Rifle,
    Shotgun
};

struct Player {
    std::string name;
    int health;
    int ammo;
    int armor;
    Weapon currentWeapon;
};

void damagePlayer(Player& player, int damage) {
    int actualDamage = damage - player.armor;

    if (actualDamage < 0) {
        actualDamage = 0;
    }

    player.health -= actualDamage;

    if (player.health < 0) {
        player.health = 0;
    }
}

bool isAlive(const Player& player) {
    return player.health > 0;
}

std::string getWeaponName(Weapon weapon) {
    switch (weapon) {
        case Weapon::Pistol:
            return "Pistol";
        
        case Weapon::Rifle:
            return "Rifle";

        case Weapon::Shotgun:
            return "Shotgun";
    }

    return "Unknown";
}

void printStatus(const Player& player) {
    std::cout << player.name
                << " health: " << player.health
                << " armor: " << player.armor << "\n"
                << " ammo:: " << player.ammo << "\n";

    std::cout << "Weapon: "
                << getWeaponName(player.currentWeapon) << "\n";
}

void printPlayers(const std::vector<Player>& players) {
    std::cout << "Players:\n";

    for (int i = 0; i < players.size(); i++) {
        std::cout << i + 1 << ". " << players[i].name << "\n";
    }
}

int getWeaponDamage(Weapon weapon) {
    switch (weapon) {
        case Weapon::Pistol:
            return 20;
        
        case Weapon::Rifle:
            return 35;

        case Weapon::Shotgun:
            return 50;
    }

    return 0;
}

void attack(Player& attacker, Player& target) {
    if (attacker.ammo <= 0) {
        std::cout << attacker.name << " is out of ammo\n";
        return;
    }

    int damage = getWeaponDamage(attacker.currentWeapon);
    damagePlayer(target, damage);
    attacker.ammo--;

    std::cout << attacker.name << " attacked "
                << target.name << "\n";
}

void reload(Player& player) {
    player.ammo = 15;
    std::cout << player.name << " reloaded\n";
}

int main() {

    Weapon currentWeapon = Weapon::Shotgun;

    if (currentWeapon == Weapon::Pistol) {
        std::cout << "You have a pistol\n";
    } else if (currentWeapon == Weapon::Shotgun) {
        std::cout << "You have a shotgun\n";
    } else if (currentWeapon == Weapon::Rifle) {
        std::cout << "You have a rifle\n";
    }

    std::vector<Player> players;
    

    players.push_back({"Alpha", 100, 15, 25, Weapon::Pistol});
    players.push_back({"Bravo", 80, 20, 10, Weapon::Shotgun});
    players.push_back({"Charlie", 60, 15, 5, Weapon::Rifle});

    attack(players[0], players[1]);
    attack(players[0], players[1]);
    attack(players[0], players[1]);

    reload(players[0]);

    printStatus(players[0]);
    printStatus(players[1]);

    printPlayers(players);
    int choice;
    std::cout << "choose a player: ";
    std::cin >> choice;

    if (choice < 1 || choice > players.size()) {
        std::cout << "Invalid choice\n";
        return 1;
    }

    Player& selectedPlayer = players[choice - 1];

    std::cout << selectedPlayer.name << " weapon damage: "
            << getWeaponDamage(selectedPlayer.currentWeapon) << "\n";

    while (selectedPlayer.health > 0) {
        int damage;
        std::cout << "How much damage?";
        std::cin >> damage;

        damagePlayer(selectedPlayer, damage);

        printStatus(selectedPlayer);
    }
    std::cout << selectedPlayer.name << " died\n";

    for (Player& player : players) {
        int damage;
        std::cout << "How much damage should " << player.name << " take? ";
        std::cin >> damage;
        damagePlayer(player, damage);

        if (player.health == 0) {
            std::cout << player.name << " is dead\n";
        } else if (player.health < 20) {
            std::cout << player.name << " is critically wounded\n";
        } else {
            std::cout << player.name << " is healthy\n";
        }

        printStatus(player);
    }
    
    return 0;
}