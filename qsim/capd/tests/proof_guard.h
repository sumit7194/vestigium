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
#include <unistd.h>
namespace capd_proof {
inline const capd::MpInterval& trig_checked(const capd::MpInterval& x) {
  static const capd::MpFloat LIM(1e12);  // exact in double and in MPFR
  if (!(x.leftBound() >= -LIM && x.rightBound() <= LIM))
    throw std::runtime_error("capd_proof: trig argument outside [-1e12, 1e12] (fail closed; CAPD sin hang >~1e13)");
  return x;
}
inline capd::MpInterval checked_sin(const capd::MpInterval& x) { return capd::intervals::sin(trig_checked(x)); }
inline capd::MpInterval checked_cos(const capd::MpInterval& x) { return capd::intervals::cos(trig_checked(x)); }
// CAPD's MpInterval log does NOT throw on a box reaching below 0: it returns a NaN endpoint (testNaN is compiled out,
// __MPI_TEST_NAN__ is off in MpIntervalSettings.h; found by the trust-rule-3 differential check, DIFFCHECK.md).
// checked_log fails closed unless the whole box is > 0, and also rejects a NaN result.
inline capd::MpInterval checked_log(const capd::MpInterval& x) {
  if (!(x.leftBound() > 0)) throw std::runtime_error("capd_proof: log argument not certainly > 0 (fail closed)");
  capd::MpInterval r = capd::intervals::log(x);
  if (!(r.leftBound() <= r.rightBound())) throw std::runtime_error("capd_proof: log returned NaN/inverted (fail closed)");
  return r;
}
// Hard wall-clock watchdog: SIGALRM after `seconds` writes a message and exits 124 (no result is ever printed).
extern "C" inline void watchdog_fire(int) {
  const char m[] = "\nWATCHDOG TIMEOUT: proof program exceeded its wall-clock limit (fail closed)\n";
  ssize_t r = ::write(2, m, sizeof(m) - 1); (void)r; std::_Exit(124);
}
inline void watchdog(unsigned seconds) { std::signal(SIGALRM, watchdog_fire); ::alarm(seconds); }
}  // namespace capd_proof
#pragma GCC poison sin cos tan asin acos atan sinh cosh tanh log
