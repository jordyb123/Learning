#include <iostream>
#include <string>

bool isEven(int number) {
    if (number % 2 == 0) {
        return true;
    } else {
        return false;
    }
}

int main() {
    int number;
    std::cout << "Enter a number? ";
    std::cin >> number;

    if (isEven(number)) {
        std::cout << "Even\n";

    } else {
        std::cout << "Odd\n";
    }

    return 0;
}