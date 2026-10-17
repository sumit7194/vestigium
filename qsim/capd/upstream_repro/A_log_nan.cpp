// Issue A: MpInterval log of an interval reaching below 0 returns NaN endpoints instead of throwing (sqrt throws).
#include "capd/mpcapdlib.h"
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(113);
  capd::MpInterval a(-1, 1), b(-2, -1);
  std::cout << "log([-1,1])  = " << log(a) << "\n";
  std::cout << "log([-2,-1]) = " << log(b) << "\n";
  try { std::cout << "sqrt([-2,-1]) = " << sqrt(b) << "\n"; } catch (std::exception& e) { std::cout << "sqrt([-2,-1]) throws: " << e.what() << "\n"; }
  capd::MpInterval n = log(a);                          // [nan, 0]
  capd::MpInterval z(capd::MpFloat(0), n.leftBound());  // [0, NaN]
  std::cout << "[0,NaN]*2   = " << z * 2 << "\n";
}
