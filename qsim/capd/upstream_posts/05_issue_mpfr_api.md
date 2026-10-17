**Title:** MPFR scalar API: two MpReal constructors are declared but not defined; Hermite–Obreshkov sets don't compile with MpReal

**Body:**

**Environment.** CAPD master 2f060980d0685cc9bf88352e08c242197cd7d686 (HEAD as of 2026-10-17), built with `-DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON` on Apple arm64 (macOS 26.5, Apple clang 21, MPFR 4.2.2, GMP 6.3.0).

**1. Two `MpReal` constructors are declared but not defined.**

`MpReal(mpq_srcptr, RoundingMode, PrecisionType)` and `MpReal(mpfr_t, RoundingMode, PrecisionType)` are both
declared in `capd/multiPrec/MpReal.h`. Using either gives an undefined-symbol link error.

Either define them (for example `mpfr_init2` plus `mpfr_set_q` / `mpfr_set` with the given rounding mode) or
remove the declarations. The mpq constructor would be the natural way to enclose an exact rational outward. We
currently call `mpfr_set_q` on the underlying `mpfr_t` with `MPFR_RNDD` / `MPFR_RNDU` instead.

```cpp
#include "capd/mpcapdlib.h"
int main() {
  mpq_t q; mpq_init(q); mpq_set_ui(q, 1, 3);
  capd::MpFloat a(q, capd::MpFloat::RoundDown);       // undefined: MpReal::MpReal(__mpq_struct const*, mpfr_rnd_t, MpPrecision)
  mpfr_t r; mpfr_init2(r, 64); mpfr_set_ui(r, 1, MPFR_RNDN);
  capd::MpFloat b(r, capd::MpFloat::RoundDown);       // undefined: MpReal::MpReal(__mpfr_struct*, mpfr_rnd_t, MpPrecision)
  return a < b;
}
```

**2. Hermite–Obreshkov sets (`C0HO*`) do not compile with MPFR scalars.**

`capd::MpC0HOTripletonSet`, and the other HO sets, fail to compile. `capd/dynset/HOData.h:56` computes
`ScalarType(sign)/binomial(p+q,q)`, and the `unsigned long long` returned by `binomial` is ambiguous for `MpReal`:
"conversion from 'unsigned long long' to 'const capd::multiPrec::MpReal' is ambiguous".

Your published Rössler example (`examples/RosslerChaoticDynamics`) uses `C0HOTripletonSet`, so an MPFR port of it
has to fall back to `MpC0TripletonSet`. A possible fix is an explicit conversion, for example
`ScalarType(sign) / ScalarType(static_cast<long>(binomial(p+q,q)))`, or a cast based on `TypeTraits`.

```cpp
#include "capd/mpcapdlib.h"
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  capd::MpIMap f("var:x,y;fun:-y,x;"); capd::MpIOdeSolver solver(f, 20); capd::MpITimeMap tm(solver);
  capd::MpIVector x(2); x[0] = 1; x[1] = 0;
  capd::MpC0HOTripletonSet s(x);                     // HOData.h:56: ambiguous conversion from unsigned long long
  return tm(capd::MpInterval(1), s).dimension() == 2 ? 0 : 1;
}
```
