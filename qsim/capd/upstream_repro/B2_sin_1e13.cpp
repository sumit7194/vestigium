// Issue B, one point: sin at |x| = 1e13 and 1e14 (256 bits), timed.
#include "capd/mpcapdlib.h"
#include <chrono>
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  for (double x : {1e13, 1e14}) {
    auto t0 = std::chrono::steady_clock::now();
    capd::MpInterval s = sin(capd::MpInterval(x));
    std::cout << "sin(" << x << "): " << std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() << " s\n" << std::flush;
  }
}
