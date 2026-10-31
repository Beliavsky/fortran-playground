#include <random>
#include <iostream>
#include <iomanip>
int main() {
    std::mt19937_64 rng(5489ULL);
    for (int i = 1; i <= 1000; ++i) {
        auto value = rng();
        if (i <= 10 || i == 312 || i == 313 || i == 624 || i == 625 || i == 1000)
            std::cout << std::dec << i << ' ' << std::hex << std::uppercase
                      << std::setw(16) << std::setfill('0') << value << '\n';
    }
}
