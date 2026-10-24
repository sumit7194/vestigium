// kerr_p.cpp -- NON-RIGOROUS compiled replacement for MNFlow.P / Pinv / py_of (mn_numerics.py), for the B15 constructor
// stage only (the frozen B14 constructor is untouched; it is plugged in through the same adapter). Same field: the
// B10-regularised MN/Kerr reduced field of gen/mn_field.h (generated from the gated symbolic source), in double, with
// the Jacobian by forward-mode dual numbers (exact derivatives of the same expression; no finite differences).
// Same semantics as MNFlow.P: start on y = 0 with p_y > 0 lifted from H = -1/2; return = the next crossing of y = 0
// with ydot > 0 at t > 1e-6 (event direction +1), n times; jac: the 2x2 section derivative with the same on-shell
// D_in and the same "slide along the flow back to y = 0" correction. Pinv: the reversed flow, first crossing with the
// reversed-time direction -1 at t > 1e-6. Integrator: Boost.Odeint dense-output Dormand-Prince 5(4), abs = rel = 1e-12
// by default. Events per registered B15b (E1-E5), coded independently of kerr_rs: every accepted step is sampled at 10
// points of its dense output and may change side at most once (E5, a detection heuristic); the event is bisected in
// the step-local theta to 4e-16 (E1) -- but Boost's calc_state takes ABSOLUTE t, so here the resolution is also bounded
// by ulp(t0 + theta h); the state at the event comes from a real integration over the local length theta h (2^m
// substeps of the error stepper, max-norm error test; independent of the ulp of t), checked against the interpolant to
// 1e-11 block-relative (E2); failures halve the step, up to 10 times, then the call returns -1 (never 0, "no return");
// T is summed with compensation (E4); per-call diagnostics via kerr_stats (E3).
// Status: the SECOND implementation of registered B15b (cross-checks only); kerr_rs is the primary.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <boost/numeric/odeint.hpp>

struct D4 {                                     // value + gradient in 4 variables
  double v; double d[4];
  D4() : v(0) { std::memset(d, 0, sizeof d); }
  D4(double x) : v(x) { std::memset(d, 0, sizeof d); }
  D4(int x) : v(x) { std::memset(d, 0, sizeof d); }
};
inline D4 operator+(D4 a, const D4& b) { a.v += b.v; for (int i = 0; i < 4; ++i) a.d[i] += b.d[i]; return a; }
inline D4 operator-(D4 a, const D4& b) { a.v -= b.v; for (int i = 0; i < 4; ++i) a.d[i] -= b.d[i]; return a; }
inline D4 operator-(D4 a) { a.v = -a.v; for (int i = 0; i < 4; ++i) a.d[i] = -a.d[i]; return a; }
inline D4 operator*(const D4& a, const D4& b) { D4 r; r.v = a.v * b.v; for (int i = 0; i < 4; ++i) r.d[i] = a.d[i] * b.v + a.v * b.d[i]; return r; }
inline D4 operator/(const D4& a, const D4& b) { D4 r; r.v = a.v / b.v; for (int i = 0; i < 4; ++i) r.d[i] = (a.d[i] * b.v - a.v * b.d[i]) / (b.v * b.v); return r; }
inline D4 sqrt(const D4& a) { D4 r; r.v = std::sqrt(a.v); for (int i = 0; i < 4; ++i) r.d[i] = a.d[i] / (2 * r.v); return r; }
inline D4 mn_exp(const D4& a) { D4 r; r.v = std::exp(a.v); for (int i = 0; i < 4; ++i) r.d[i] = a.d[i] * r.v; return r; }
inline double mn_exp(double a) { return std::exp(a); }
#include "gen/mn_field.h"

typedef std::array<double, 20> St;             // state (x, y, px, py) + 4x4 variational matrix (row-major)
static double C5[5] = {39, -0.625, 0, 0.98, 222.5};
static double RTOL = 1e-12, ATOL = 1e-12;
static void field(const double z[4], double f[4]) { mn_field<double>(z, f, C5); }
static void field_jac(const double z[4], double f[4], double J[16]) {
  D4 in[4], out[4], c[5];
  for (int i = 0; i < 4; ++i) { in[i] = D4(z[i]); in[i].d[i] = 1; }
  for (int i = 0; i < 5; ++i) c[i] = D4(C5[i]);
  mn_field<D4>(in, out, c);
  for (int i = 0; i < 4; ++i) { f[i] = out[i].v; for (int j = 0; j < 4; ++j) J[4 * i + j] = out[i].d[j]; }
}
struct Rhs {
  bool var; double sign;
  void operator()(const St& s, St& ds, double) const {
    double f[4], J[16];
    if (!var) { field(s.data(), f); for (int i = 0; i < 4; ++i) ds[i] = sign * f[i]; for (int i = 4; i < 20; ++i) ds[i] = 0; return; }
    field_jac(s.data(), f, J);
    for (int i = 0; i < 4; ++i) ds[i] = sign * f[i];
    for (int i = 0; i < 4; ++i) for (int j = 0; j < 4; ++j) { double a = 0; for (int k = 0; k < 4; ++k) a += J[4 * i + k] * s[4 + 4 * k + j]; ds[4 + 4 * i + j] = sign * a; }
  }
};
// per-call diagnostics (E3): crossings, max |ydot| h dtheta, max E2 difference, min |ydot| at a crossing, E2 / E5 retries
static double STATS[6];
// E2's registered bar is 1e-11; kerr_test_e2_bar exists ONLY for the -1 negative control (never in a counted run)
static double E2_BAR = 1e-11;
static void stats_reset() { STATS[0] = STATS[1] = STATS[2] = STATS[4] = STATS[5] = 0; STATS[3] = INFINITY; }
// E2's block-relative difference: state block (0..4) and variational block (4..20) separately
static double block_diff(const St& a, const St& b) {
  double d = 0;
  const int lo[2] = {0, 4}, hi[2] = {4, 20};
  for (int k = 0; k < 2; ++k) {
    double sc = 1; for (int i = lo[k]; i < hi[k]; ++i) sc = std::max(sc, std::fabs(b[i]));
    for (int i = lo[k]; i < hi[k]; ++i) d = std::max(d, std::fabs(a[i] - b[i]) / sc);
  }
  return d;
}
// a real integration from x0 over length len: 2^m equal substeps of the dopri5 error stepper, each passing the max-norm
// test |err_i| <= atol + rtol max(|x_i|, |x1_i|); false if no m <= 10 passes
static bool integrate_exact(const Rhs& rhs, const St& x0, double t0, double len, St& out) {
  boost::numeric::odeint::runge_kutta_dopri5<St> es;
  for (int m = 0; m <= 10; ++m) {
    const int n = 1 << m; const double hs = len / n; St x = x0, xe; double t = t0; bool ok = true;
    es.reset();
    for (int k = 0; k < n && ok; ++k) {
      St xold = x; es.do_step(rhs, x, t, hs, xe); t += hs;
      for (int i = 0; i < 20; ++i) if (!(std::fabs(xe[i]) <= ATOL + RTOL * std::max(std::fabs(xold[i]), std::fabs(x[i])))) { ok = false; break; }
    }
    if (ok) { out = x; return true; }
  }
  return false;
}
// integrate from s until the first event (y crosses 0 with direction dir) at t > 1e-6.
// returns 1 with s = the state at the event (by a real step) and the event at t0ev + dtev; 0 if a step start passes
// tmax; -1 if an E2 or E5 check failed after 10 halvings
static int to_event_(St& s, double& t0ev, double& dtev, bool var, double sign, double dir, double tmax) {
  using namespace boost::numeric::odeint;
  auto stepper = make_dense_output(ATOL, RTOL, runge_kutta_dopri5<St>());
  Rhs rhs{var, sign};
  // "past the section in the event direction" (dir > 0: y >= 0; dir < 0: y <= 0): the event is a change false -> true
  auto past = [dir](double v) { return dir > 0 ? v >= 0 : v <= 0; };
  stepper.initialize(s, 0.0, 1e-6);
  // retry caps: E5 counts consecutive failures of the SAME step start (reset once a step passes E5); E2 counts every
  // failure for this crossing, never reset (a non-event step after a halving must not restart the count)
  int e5_run = 0, e2_count = 0; St m;
  while (true) {
    const St start = stepper.current_state();
    auto iv = stepper.do_step(rhs);
    const double t0 = iv.first, h = iv.second - iv.first;
    if (t0 > tmax) return 0;
    bool sm[10]; int nch = 0, jch = -1;
    for (int j = 0; j < 10; ++j) {
      if (j == 0) m = start; else if (j == 9) m = stepper.current_state(); else stepper.calc_state(t0 + h * (j / 9.0), m);
      sm[j] = past(m[1]);
      if (j > 0 && sm[j] != sm[j - 1]) { ++nch; jch = j - 1; }
    }
    if (nch > 1) {                                                    // E5
      ++STATS[5]; if (++e5_run > 10) return -1;
      stepper.initialize(start, t0, 0.5 * h); continue;
    }
    e5_run = 0;
    if (!(nch == 1 && !sm[jch] && sm[jch + 1] && t0 + h > 1e-6)) continue;
    double lo = std::max({jch / 9.0, (1e-6 - t0) / h, 0.0}), hi = (jch + 1) / 9.0;   // E1
    for (int it = 0; it < 200 && hi - lo > 4e-16; ++it) {
      const double mid = 0.5 * (lo + hi); stepper.calc_state(t0 + h * mid, m);
      if (past(m[1])) hi = mid; else lo = mid;
    }
    St interp, stepped; stepper.calc_state(t0 + h * hi, interp);
    if (integrate_exact(rhs, start, t0, h * hi, stepped)) {           // E2
      const double d = block_diff(stepped, interp);
      if (d <= E2_BAR) {
        St f; rhs(stepped, f, 0.0);
        STATS[0] += 1; STATS[1] = std::max(STATS[1], std::fabs(f[1]) * h * (hi - lo));
        STATS[2] = std::max(STATS[2], d); STATS[3] = std::min(STATS[3], std::fabs(f[1]));
        s = stepped; t0ev = t0; dtev = h * hi; return 1;
      }
    }
    ++STATS[4]; if (++e2_count > 10) return -1;
    stepper.initialize(start, t0, 0.5 * h);
  }
}
// an exception (e.g. Boost's step-size adjustment failure) must not cross the C ABI: it is an integration failure, -1
static int to_event(St& s, double& t0ev, double& dtev, bool var, double sign, double dir, double tmax) {
  try { return to_event_(s, t0ev, dtev, var, sign, dir, tmax); } catch (...) { return -1; }
}
struct Kahan { double s = 0, c = 0; void add(double v) { double y = v - c, t = s + y; c = (t - s) - y; s = t; } };
extern "C" {
void kerr_set(double k, double alpha, double beta, double E, double L, double rtol, double atol) {
  C5[0] = k; C5[1] = alpha; C5[2] = beta; C5[3] = E; C5[4] = L; RTOL = rtol; ATOL = atol;
}
double kerr_py(double x, double px) {
  double in[2] = {x, 0.0}, g[3]; mn_lift<double>(in, g, C5);
  double r = (-1.0 - g[0] * px * px - 2 * g[2]) / g[1];
  return r > 0 ? std::sqrt(r) : NAN;
}
// out: x, px, T, and if jac: DP (2x2 row-major) -> 7 doubles. Returns 1 on success, 0 if no return within tmax,
// -1 if an integration check (E2 / E5) failed: a numerical failure, never to be read as "no return".
int kerr_P(double x, double px, int n, int jac, double tmax, double* out) {
  stats_reset();
  double py = kerr_py(x, px); if (!(py == py)) return 0;
  St s{}; s[0] = x; s[1] = 0; s[2] = px; s[3] = py;
  if (jac) for (int i = 0; i < 4; ++i) s[4 + 5 * i] = 1;
  Kahan T;
  for (int k = 0; k < n; ++k) {
    double a, b; const int r = to_event(s, a, b, jac, 1.0, 1.0, tmax); if (r != 1) return r;
    s[1] = 0; T.add(a); T.add(b);
  }
  out[0] = s[0]; out[1] = s[2]; out[2] = T.s;
  if (!jac) return 1;
  double f0[4], z0[4] = {x, 0, px, py}; field(z0, f0);
  double Hx = -f0[2], Hpx = f0[0], Hpy = f0[1];
  double Din[4][2] = {{1, 0}, {0, 0}, {0, 1}, {-Hx / Hpy, -Hpx / Hpy}};
  double V[4][2];
  for (int i = 0; i < 4; ++i) for (int j = 0; j < 2; ++j) { double a = 0; for (int k = 0; k < 4; ++k) a += s[4 + 4 * i + k] * Din[k][j]; V[i][j] = a; }
  double f[4]; field(s.data(), f);
  // slide back to y = 0, with the y row copied first: the in-place loop zeroed V[1] at i = 1, so the p_x and p_y rows
  // went uncorrected (found by the kerr_rs cross-check, 2026-10-24: det DP 0.57 instead of 1; the x row was unaffected)
  const double V1[2] = {V[1][0], V[1][1]};
  for (int i = 0; i < 4; ++i) for (int j = 0; j < 2; ++j) V[i][j] -= f[i] * (V1[j] / f[1]);
  out[3] = V[0][0]; out[4] = V[0][1]; out[5] = V[2][0]; out[6] = V[2][1];
  return 1;
}
// Returns 1 / 0 / -1 as kerr_P.
int kerr_Pinv(double x, double px, double tmax, double* out) {
  stats_reset();
  double py = kerr_py(x, px); if (!(py == py)) return 0;
  St s{}; s[0] = x; s[1] = 0; s[2] = px; s[3] = py; double a, b;
  const int r = to_event(s, a, b, false, -1.0, -1.0, tmax); if (r != 1) return r;
  out[0] = s[0]; out[1] = s[2]; return 1;
}
// TEST HOOK, negative control only: set E2's bar (registered value 1e-11; a negative bar makes every crossing fail)
void kerr_test_e2_bar(double bar) { E2_BAR = bar; }
// E3 diagnostics of the last kerr_P / kerr_Pinv call -> 6 doubles (as kerr_rs's kerr_stats)
void kerr_stats(double* out) { for (int i = 0; i < 6; ++i) out[i] = STATS[i]; }
}
