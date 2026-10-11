#include "proof_guard.h"
#include <iostream>
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  capd::MpIMap f("var:x;fun:-x;");
  capd::MpIOdeSolver solver(f, 20);
  capd::MpITimeMap tm(solver);
  capd::MpIVector u(1); u[0] = capd::MpInterval(1);
  capd::MpC0Rect2Set s(u);                         // MPFR-interval doubleton set
  capd::MpIVector r = tm(capd::MpInterval(1), s);
  std::cout << r << std::endl;
}
