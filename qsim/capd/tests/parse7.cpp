// Test-only (NOT proof code): CAPD #7 parse_from_sstream, printing both bounds exactly as hex floats.
#include "capd/capdlib.h"
#include <cstdio>
#include <sstream>
int main() {
  capd::interval a{};
  std::istringstream s("[3.21312312, 4.324324324]");
  s >> a;
  std::printf("left  %.17g  %a\nright %.17g  %a\n", a.leftBound(), a.leftBound(), a.rightBound(), a.rightBound());
}
