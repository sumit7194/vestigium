// FIRED CONTROL (bridge 2026-10-11): NaN-producing and division-by-zero operations must never reach a certificate
// decision silently. For each case: (1) record what raw CAPD MpInterval does (THROW, or the interval it returns,
// possibly with NaN/inf endpoints); (2) if it returned an interval, every capd_proof decision helper on it must THROW
// unless the interval is finite. Also positive controls: finite intervals decide correctly. Exit 0 only if all hold.
#include "capd/mpcapdlib.h"
// raw CAPD log captured before the guard poisons the name (this control characterises CAPD itself)
static capd::MpInterval raw_log(const capd::MpInterval& x) { return log(x); }
#include "proof_guard.h"
#include <functional>
#include <iostream>
#include <vector>

using capd::MpInterval;
typedef capd::MpFloat R;

static int failures = 0;

static bool all_helpers_throw(const MpInterval& r) {
  const MpInterval two(2), zero(0), box(-1e300, 1e300);
  std::vector<std::function<void()>> hs = {
      [&] { capd_proof::certainly_positive(r); },  [&] { capd_proof::certainly_negative(r); },
      [&] { capd_proof::certainly_less(r, two); }, [&] { capd_proof::certainly_less(zero, r); },
      [&] { capd_proof::certainly_disjoint(r, two); }, [&] { capd_proof::certainly_in_interior(r, box); },
      [&] { capd_proof::require_finite(r); }};
  for (auto& h : hs) {
    try { h(); return false; } catch (std::runtime_error& e) {
      if (std::string(e.what()).find("capd_proof: non-finite") != 0) return false;
    }
  }
  return true;
}

static void check(const char* name, std::function<MpInterval()> f) {
  MpInterval r;
  try { r = f(); } catch (std::exception& e) {
    std::cout << "  " << name << ": raw CAPD THROWS (" << std::string(e.what()).substr(0, 60) << ") -> caught\n";
    return;
  }
  const bool finite = isNumber(r.leftBound()) && isNumber(r.rightBound());
  std::cout << "  " << name << ": raw CAPD returns " << r << (finite ? " (finite)" : " (NON-FINITE)");
  if (finite) { std::cout << " -> no NaN to catch\n"; return; }
  bool ok = all_helpers_throw(r);
  std::cout << (ok ? " -> every decision helper THROWS: caught\n" : " -> SLIPPED THROUGH a decision helper\n");
  if (!ok) ++failures;
}

int main() {
  R::setDefaultPrecision(256);
  const R inf = R::positiveInfinity();
  const R nan = R(0.0) / R(0.0);
  const MpInterval I_inf(inf, inf), I_ninf(-inf, -inf), I_ent(-inf, inf), I_nan(nan, nan), I_halfnan(R(0.0), nan);
  std::cout << "NaN sources:\n";
  check("0 * inf          ", [&] { return MpInterval(0) * I_inf; });
  check("[0,1] * [1,inf]  ", [&] { return MpInterval(0, 1) * MpInterval(R(1.0), inf); });
  check("inf - inf        ", [&] { return I_inf - I_inf; });
  check("inf + (-inf)     ", [&] { return I_inf + I_ninf; });
  check("inf / inf        ", [&] { return I_inf / I_inf; });
  check("entire * 0       ", [&] { return I_ent * MpInterval(0); });
  check("log of [-1, 1]    ", [&] { return raw_log(MpInterval(-1, 1)); });
  check("log of [-2, -1]   ", [&] { return raw_log(MpInterval(-2, -1)); });
  check("[nan,nan] + 1    ", [&] { return I_nan + MpInterval(1); });
  check("[0,nan] * 2      ", [&] { return I_halfnan * MpInterval(2); });
  check("exp of [nan,nan]  ", [&] { return exp(I_nan); });
  check("sqrt of [nan,nan] ", [&] { return sqrt(I_nan); });
  std::cout << "Division by intervals containing 0 (the other classic silent-NaN source):\n";
  check("1 / [0, 0]       ", [&] { return MpInterval(1) / MpInterval(0); });
  check("0 / [0, 0]       ", [&] { return MpInterval(0) / MpInterval(0); });
  check("1 / [-0, 0]      ", [&] { return MpInterval(1) / MpInterval(-R(0.0), R(0.0)); });
  check("1 / [0, 1]       ", [&] { return MpInterval(1) / MpInterval(0, 1); });
  check("1 / [-1, 0]      ", [&] { return MpInterval(1) / MpInterval(-1, 0); });
  check("1 / [-1, 1]      ", [&] { return MpInterval(1) / MpInterval(-1, 1); });
  check("[-1,1] / [-1,1]  ", [&] { return MpInterval(-1, 1) / MpInterval(-1, 1); });
  check("1 / [tiny, tiny] ", [&] { return MpInterval(1) / MpInterval(R("1e-1000000000")); });
  check("1 / entire       ", [&] { return MpInterval(1) / I_ent; });
  check("inf / [1, 2]     ", [&] { return I_inf / MpInterval(1, 2); });
  check("1 / [nan,nan]    ", [&] { return MpInterval(1) / I_nan; });
  std::cout << "Infinite (non-NaN) results must also be refused by the decision helpers:\n";
  check("exp of [1e300]    ", [&] { return exp(MpInterval(1e300)); });
  check("[1,inf] + 1      ", [&] { return MpInterval(R(1.0), inf) + MpInterval(1); });
  std::cout << "Positive controls (finite intervals must decide correctly):\n";
  bool pc = capd_proof::certainly_positive(MpInterval(1, 2)) && !capd_proof::certainly_positive(MpInterval(-1, 2)) &&
            capd_proof::certainly_negative(MpInterval(-2, -1)) &&
            capd_proof::certainly_disjoint(MpInterval(2.5, 3), MpInterval(2)) &&
            !capd_proof::certainly_disjoint(MpInterval(1.5, 2.5), MpInterval(2)) &&
            capd_proof::certainly_less(MpInterval(0, 1), MpInterval(1.5, 2)) &&
            capd_proof::certainly_in_interior(MpInterval(0, 1), MpInterval(-1, 2)) &&
            !capd_proof::certainly_in_interior(MpInterval(0, 2), MpInterval(-1, 2));
  std::cout << "  " << (pc ? "all correct" : "WRONG") << "\n";
  if (!pc) ++failures;
  std::cout << (failures == 0 ? "G_NAN CONTROL PASS" : "G_NAN CONTROL FAIL") << " (" << failures << " slipped)\n";
  return failures == 0 ? 0 : 1;
}
