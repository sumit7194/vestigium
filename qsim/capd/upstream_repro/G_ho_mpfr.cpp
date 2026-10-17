// Issue G: C0HOTripletonSet (Hermite-Obreshkov) does not compile with MPFR scalars: HOData.h computes
// ScalarType(sign)/binomial(p+q,q), and the unsigned long long from binomial is ambiguous for MpReal.
#include "capd/mpcapdlib.h"
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  capd::MpIMap f("var:x,y;fun:-y,x;");
  capd::MpIOdeSolver solver(f, 20);
  capd::MpITimeMap tm(solver);
  capd::MpIVector x(2); x[0] = 1; x[1] = 0;
  capd::MpC0HOTripletonSet s(x);
  capd::MpIVector y = tm(capd::MpInterval(1), s);
  return y.dimension() == 2 ? 0 : 1;
}
