// Regression for upstream #27 (test code): thin initial set at the equilibrium of x' = 10(1-x).
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <cmath>
#include <iostream>
template <class Map, class Solver, class TM, class Vec, class Set, class Itv>
void run(const char* tag, double lo, double hi) {
  std::cout << tag << " x(0) in [" << lo << ", " << hi << "]: ";
  try {
    Map map("var:x;fun:10*(1-x);"); Solver solver(map, 12);
    solver.setAbsoluteTolerance(1e-10); solver.setRelativeTolerance(1e-10);
    TM tm(solver); Vec u0(1); u0[0] = Itv(lo, hi); Set set(u0);
    Vec r = tm(Itv(0.05), set); std::cout << "x(0.05) = " << r << "\n";
  } catch (const std::exception& e) { std::string w = e.what(); std::cout << "THROW " << w.substr(0, w.find('\n')) << "\n"; }
}
int main() {
  capd::MpFloat::setDefaultPrecision(256);
  run<capd::IMap, capd::IOdeSolver, capd::ITimeMap, capd::IVector, capd::C0Rect2Set, capd::interval>("D ", 1.0, 1.0);
  run<capd::IMap, capd::IOdeSolver, capd::ITimeMap, capd::IVector, capd::C0Rect2Set, capd::interval>("D ", std::nextafter(1.0, 0.0), 1.0);
  run<capd::MpIMap, capd::MpIOdeSolver, capd::MpITimeMap, capd::MpIVector, capd::MpC0Rect2Set, capd::MpInterval>("Mp", 1.0, 1.0);
  run<capd::MpIMap, capd::MpIOdeSolver, capd::MpITimeMap, capd::MpIVector, capd::MpC0Rect2Set, capd::MpInterval>("Mp", std::nextafter(1.0, 0.0), 1.0);
}
