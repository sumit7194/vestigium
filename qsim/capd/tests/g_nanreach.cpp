// REACHABILITY test (bridge 2026-10-11 NaN safeguard). CAPD can SWALLOW a NaN: [0, NaN] * 2 returns the finite
// [0, 0] (g_nan.cpp), which no after-the-fact check can see. So the question is whether NaN can be CREATED from the
// intervals that a computation can actually reach. With directed rounding, overflow sends a lower bound to -inf or
// to the largest finite number, and an upper bound to +inf or to the most negative finite number. So the reachable
// boxes have lo in R u {-inf} and hi in R u {+inf} (never lo = +inf or hi = -inf).
// Exhaustive over a grid of special endpoints {-inf, -MAX, -1e9, -1, -tiny, -0, 0, tiny, 1e-9, 1, 3, 1e9, MAX, +inf}
// at precisions 53 and 256: every binary op (+ - * /) on every pair of reachable boxes, and every unary op
// (sqrt exp checked_log checked_sin checked_cos) on every box. For each result that is not a THROW, require:
//  (1) no NaN endpoint; (2) lo <= hi; (3) it contains the op applied to every finite grid point of the box
//      (point ops on finite values were validated against Arb in DIFFCHECK.md).
// Exit 0 only if no violation. Prints the counts and every violation.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <functional>
#include <sstream>
#include <iostream>
#include <string>
#include <vector>

using capd::MpInterval;
typedef capd::MpFloat R;

static long n_cases = 0, n_throw = 0, n_ok = 0, n_bad = 0;

static bool has_nan(const MpInterval& r) { return isNaN(r.leftBound()) || isNaN(r.rightBound()); }
static bool contains_pt(const MpInterval& r, const MpInterval& p) {
  return r.leftBound() <= p.leftBound() && p.rightBound() <= r.rightBound();
}

int main(int argc, char** argv) {
  // CONTROL mode ("control"): also include the UNREACHABLE boxes (lo = +inf or hi = -inf); violations MUST appear
  const bool control = argc > 1 && std::string(argv[1]) == "control";
  capd_proof::watchdog(120);  // a hang fails closed (exit 124)
  for (long prec : {53L, 256L}) {
    R::setDefaultPrecision(prec);
    const R inf = R::positiveInfinity();
    R MAX;
    // largest finite: nextbelow(+inf) via MPFR through the rounding-down overflow of exp
    MAX = exp(MpInterval(R(1e300))).leftBound();
    std::vector<R> pts = {-inf, -MAX, R(-1e9), R(-1.0), R("-1e-1000000000"), -R(0.0), R(0.0),
                          R("1e-1000000000"), R(1e-9), R(1.0), R(3.0), R(1e9), MAX, inf};
    std::vector<R> fin;  for (auto& p : pts) if (isNumber(p)) fin.push_back(p);
    std::vector<MpInterval> boxes;
    for (size_t i = 0; i < pts.size(); ++i)
      for (size_t j = (control ? 0 : i); j < pts.size(); ++j) {
        if (control && pts[j] < pts[i] && !(pts[i] == inf || pts[j] == -inf)) continue;
        if (!control && (pts[i] == inf || pts[j] == -inf)) continue;          // unreachable
        boxes.push_back(MpInterval(pts[i], pts[j]));
      }
    auto inside = [&](const MpInterval& b) { std::vector<MpInterval> v;
      for (auto& p : fin) if (b.leftBound() <= p && p <= b.rightBound()) v.push_back(MpInterval(p));
      return v; };
    auto report = [&](const std::string& what, const MpInterval& r, const std::string& why) {
      ++n_bad; std::cout << "  VIOLATION prec " << prec << ": " << what << " = " << r << "  (" << why << ")\n"; };
    typedef std::function<MpInterval(const MpInterval&, const MpInterval&)> Bin;
    std::vector<std::pair<std::string, Bin>> bins = {
        {"+", [](const MpInterval& a, const MpInterval& b) { return a + b; }},
        {"-", [](const MpInterval& a, const MpInterval& b) { return a - b; }},
        {"*", [](const MpInterval& a, const MpInterval& b) { return a * b; }},
        {"/", [](const MpInterval& a, const MpInterval& b) { return a / b; }}};
    for (auto& op : bins)
      for (auto& x : boxes)
        for (auto& y : boxes) {
          ++n_cases; MpInterval r;
          std::ostringstream w; w << x << " " << op.first << " " << y;
          try { r = op.second(x, y); } catch (std::exception&) { ++n_throw; continue; }
          ++n_ok;
          if (has_nan(r)) { report(w.str(), r, "NaN endpoint"); continue; }
          if (!(r.leftBound() <= r.rightBound())) { report(w.str(), r, "inverted"); continue; }
          for (auto& p : inside(x)) for (auto& q : inside(y)) {
            MpInterval v; try { v = op.second(p, q); } catch (std::exception&) { continue; }
            if (has_nan(v)) continue;  // point op on finite values: only 0/0-type, which throw
            if (!contains_pt(r, v)) { std::ostringstream m; m << "misses " << p << op.first << q << " = " << v; report(w.str(), r, m.str()); goto next_bin; }
          }
          next_bin:;
        }
    typedef std::function<MpInterval(const MpInterval&)> Un;
    std::vector<std::pair<std::string, Un>> uns = {
        {"sqrt", [](const MpInterval& a) { return sqrt(a); }},
        {"exp", [](const MpInterval& a) { return exp(a); }},
        {"checked_log", [](const MpInterval& a) { return capd_proof::checked_log(a); }},
        {"checked_sin", [](const MpInterval& a) { return capd_proof::checked_sin(a); }},
        {"checked_cos", [](const MpInterval& a) { return capd_proof::checked_cos(a); }}};
    for (auto& op : uns)
      for (auto& x : boxes) {
        ++n_cases; MpInterval r;
        std::ostringstream w; w << op.first << " of " << x;
        try { r = op.second(x); } catch (std::exception&) { ++n_throw; continue; }
        ++n_ok;
        if (has_nan(r)) { report(w.str(), r, "NaN endpoint"); continue; }
        if (!(r.leftBound() <= r.rightBound())) { report(w.str(), r, "inverted"); continue; }
        for (auto& p : inside(x)) {
          MpInterval v; try { v = op.second(p); } catch (std::exception&) { continue; }
          if (!contains_pt(r, v)) { std::ostringstream m; m << "misses value at " << p << " = " << v; report(w.str(), r, m.str()); break; }
        }
      }
  }
  std::cout << "cases " << n_cases << ", THROW " << n_throw << ", returned " << n_ok << ", VIOLATIONS " << n_bad << "\n";
  if (control) {
    std::cout << (n_bad > 0 ? "NANREACH CONTROL FIRED" : "NANREACH CONTROL DID NOT FIRE") << "\n";
    return n_bad > 0 ? 0 : 1;
  }
  std::cout << (n_bad == 0 ? "NANREACH PASS" : "NANREACH FAIL") << "\n";
  return n_bad == 0 ? 0 : 1;
}
