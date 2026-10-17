// Issue F: MpReal(mpq_srcptr, ...) and MpReal(mpfr_t, ...) are declared in MpReal.h but not defined (link error).
#include "capd/mpcapdlib.h"
#include <iostream>
int main() {
  mpq_t q; mpq_init(q); mpq_set_ui(q, 1, 3);
  capd::MpFloat a(q, capd::MpFloat::RoundDown);          // undefined symbol at link time
  mpfr_t r; mpfr_init2(r, 64); mpfr_set_ui(r, 1, MPFR_RNDN);
  capd::MpFloat b(r, capd::MpFloat::RoundDown);          // undefined symbol at link time
  std::cout << a << " " << b << "\n";
}
