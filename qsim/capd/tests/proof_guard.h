// proof_guard.h -- include LAST in every proof-bearing translation unit (CAPD trust rule 1, bridge 2026-10-11).
// Layer 1: after CAPD's headers are in, POISON every non-MPFR-interval CAPD type name, so proof code that names one
// fails to compile. Allowed in proof code: MpInterval and the MpI* types (MpIMap, MpIVector, MpIMatrix,
// MpIOdeSolver, MpICnOdeSolver, MpITimeMap, MpIPoincareMap, MpICnPoincareMap, MpICoordinateSection,
// MpIAffineSection, MpINonlinearSection, ...).
// Layer 2 (in check_proof_object.sh): nm of the proof object file must show no capd template instantiated on
// double, long double or a double interval -- that catches indirect use that name-poisoning cannot see.
#pragma once
#include "capd/mpcapdlib.h"
// double-interval types (I*, interval, DInterval), plain double and long-double types (D*, LD*), and non-interval
// multiprecision types (Mp* without I):
#pragma GCC poison interval DInterval IMap IVector IMatrix IOdeSolver ICnOdeSolver ITimeMap ICnTimeMap
#pragma GCC poison IPoincareMap ICnPoincareMap ICoordinateSection IAffineSection INonlinearSection IFunction
#pragma GCC poison DMap DVector DMatrix DOdeSolver DCnOdeSolver DTimeMap DCnTimeMap DPoincareMap DCnPoincareMap
#pragma GCC poison DCoordinateSection DAffineSection DNonlinearSection DFunction
#pragma GCC poison LDMap LDVector LDMatrix LDOdeSolver LDCnOdeSolver LDTimeMap LDPoincareMap LDFunction
#pragma GCC poison MpMap MpVector MpMatrix MpOdeSolver MpCnOdeSolver MpTimeMap MpCnTimeMap MpPoincareMap
#pragma GCC poison MpCnPoincareMap MpCoordinateSection MpAffineSection MpNonlinearSection MpFunction
// double-interval SET typedefs are unprefixed in namespace capd (their MPFR versions are MpC0Rect2Set etc.):
#pragma GCC poison C0Set C0Intv2Set C0Pped2Set C0Rect2Set C0TripletonSet C0PpedSet C0RectSet C0HORect2Set
#pragma GCC poison C0HOTripletonSet C1Set C1RectSet C1PpedSet C1Rect2Set C1Pped2Set C11Rect2Set C1HORect2Set
#pragma GCC poison C1HOPped2Set C2Set C2Rect2Set CnSet CnRect2Set

// ---- Trig-argument range guard and watchdog (bridge 2026-10-11; CAPD MPFR interval sin hangs for |x| >~ 1e13,
// CTEST_REPORT.md, regression #28). FAIL CLOSED: proof code calls capd_proof::checked_sin / checked_cos, which throw
// unless the whole argument interval lies in [-1e12, 1e12] (a NaN endpoint also throws). The bare names are poisoned
// below, so proof code cannot call the unguarded functions directly. check_proof_object.sh additionally refuses any
// trig or log name inside a string literal (a CAPD Map formula), because arguments inside an ODE step cannot be
// range-checked.
#include <csignal>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <unistd.h>
namespace capd_proof {
inline const capd::MpInterval& trig_checked(const capd::MpInterval& x) {
  static const capd::MpFloat LIM(1e12);  // exact in double and in MPFR
  // both endpoints finite, ordered, and inside [-LIM, LIM] (an inverted box such as [+inf, 3] would otherwise pass
  // the range test and send CAPD's quadrant() into an endless loop: found by the g_nanreach control)
  if (!(isNumber(x.leftBound()) && isNumber(x.rightBound()) && x.leftBound() <= x.rightBound() &&
        x.leftBound() >= -LIM && x.rightBound() <= LIM))
    throw std::runtime_error("capd_proof: trig argument outside [-1e12, 1e12] (fail closed; CAPD sin hang >~1e13)");
  return x;
}
inline capd::MpInterval checked_sin(const capd::MpInterval& x) { return capd::intervals::sin(trig_checked(x)); }
inline capd::MpInterval checked_cos(const capd::MpInterval& x) { return capd::intervals::cos(trig_checked(x)); }
// CAPD's MpInterval log does NOT throw on a box reaching below 0: it returns a NaN endpoint (testNaN is compiled out,
// __MPI_TEST_NAN__ is off in MpIntervalSettings.h; found by the trust-rule-3 differential check, DIFFCHECK.md).
// checked_log fails closed unless the whole box is > 0, and also rejects a NaN result.
inline capd::MpInterval checked_log(const capd::MpInterval& x) {
  if (!(isNumber(x.leftBound()) && !isNaN(x.rightBound()) && x.leftBound() <= x.rightBound() && x.leftBound() > 0))
    throw std::runtime_error("capd_proof: log argument not certainly > 0 (fail closed)");
  capd::MpInterval r = capd::intervals::log(x);
  if (!(r.leftBound() <= r.rightBound())) throw std::runtime_error("capd_proof: log returned NaN/inverted (fail closed)");
  return r;
}
// ---- Finite-endpoint decision helpers (bridge 2026-10-11). CAPD's NaN checks are compiled out (__MPI_TEST_NAN__ is
// off, and enabling it does not compile at 2f06098: MpInterval_Fun.hpp:36 has an extra ')'), so any NaN-producing
// operation (0*inf, inf-inf, log below 0, ...) passes NaN through SILENTLY, and every NaN comparison is false.
// RULE: every interval that enters a certificate decision goes through these helpers. Each first requires both
// endpoints to be finite numbers (mpfr_number_p: not NaN, not +-inf) and lo <= hi, and THROWS otherwise (fail
// closed); only then does it decide. Never write a raw comparison on bounds in proof code.
inline void require_finite(const capd::MpInterval& x, const char* what = "interval") {
  if (!(isNumber(x.leftBound()) && isNumber(x.rightBound()) && x.leftBound() <= x.rightBound()))
    throw std::runtime_error(std::string("capd_proof: non-finite or inverted ") + what + " in a certificate decision (fail closed)");
}
template <class V> inline void require_finite_all(const V& v, const char* what = "vector/matrix") {
  for (auto it = v.begin(); it != v.end(); ++it) require_finite(*it, what);
}
inline bool certainly_positive(const capd::MpInterval& x) { require_finite(x); return x.leftBound() > 0; }
inline bool certainly_negative(const capd::MpInterval& x) { require_finite(x); return x.rightBound() < 0; }
inline bool certainly_less(const capd::MpInterval& x, const capd::MpInterval& y) {
  require_finite(x); require_finite(y); return x.rightBound() < y.leftBound();
}
// "certainly x != c": x and c are certainly disjoint (e.g. tr[g,h] != 2)
inline bool certainly_disjoint(const capd::MpInterval& x, const capd::MpInterval& c) {
  require_finite(x); require_finite(c); return x.rightBound() < c.leftBound() || c.rightBound() < x.leftBound();
}
// x lies in the interior of y (covering relations, a priori bounds)
inline bool certainly_in_interior(const capd::MpInterval& x, const capd::MpInterval& y) {
  require_finite(x); require_finite(y); return y.leftBound() < x.leftBound() && x.rightBound() < y.rightBound();
}

// Hard wall-clock watchdog: SIGALRM after `seconds` writes a message and exits 124 (no result is ever printed).
extern "C" inline void watchdog_fire(int) {
  const char m[] = "\nWATCHDOG TIMEOUT: proof program exceeded its wall-clock limit (fail closed)\n";
  ssize_t r = ::write(2, m, sizeof(m) - 1); (void)r; std::_Exit(124);
}
inline void watchdog(unsigned seconds) { std::signal(SIGALRM, watchdog_fire); ::alarm(seconds); }
}  // namespace capd_proof
#pragma GCC poison sin cos tan asin acos atan sinh cosh tanh log
