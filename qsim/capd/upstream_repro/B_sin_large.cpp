// Issue B: MpInterval sin argument reduction is linear in |x|; time sin at growing |x| (256 bits).
#include "capd/mpcapdlib.h"
#include <chrono>
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  for (double x : {1e9, 1e10, 1e11, 1e12}) {
    auto t0 = std::chrono::steady_clock::now();
    capd::MpInterval s = sin(capd::MpInterval(x));
    double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    std::cout << "sin(" << x << "): " << ms << " ms, width " << s.rightBound() - s.leftBound() << "\n";
  }
}
