// Regression for upstream #28 (test code, not proof code): sin of a large negative point interval.
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <cstdlib>
#include <iostream>
int main(int argc, char** argv) {
  const double x = std::atof(argv[2]);
  std::cout.precision(17);
  if (std::string(argv[1]) == "D") std::cout << "D sin(" << x << ") = " << sin(capd::interval(x)) << std::endl;
  else { capd::MpFloat::setDefaultPrecision(256); std::cout << "Mp sin(" << x << ") = " << sin(capd::MpInterval(x)) << std::endl; }
}
