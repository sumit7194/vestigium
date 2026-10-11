#include "proof_guard.h"
#include <iostream>
int main() { capd::intervals::Interval<double, capd::rounding::DoubleRounding> x(1.0, 2.0); std::cout << (x*x) << std::endl; }
