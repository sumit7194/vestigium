// kerr_p.cpp -- NON-RIGOROUS compiled replacement for MNFlow.P / Pinv / py_of (mn_numerics.py), for the B15 constructor
// stage only (the frozen B14 constructor is untouched; it is plugged in through the same adapter). Same field: the
// B10-regularised MN/Kerr reduced field of gen/mn_field.h (generated from the gated symbolic source), in double, with
// the Jacobian by forward-mode dual numbers (exact derivatives of the same expression; no finite differences).
// Same semantics as MNFlow.P: start on y = 0 with p_y > 0 lifted from H = -1/2; return = the next crossing of y = 0
// with ydot > 0 at t > 1e-6 (event direction +1), n times; jac: the 2x2 section derivative with the same on-shell
// D_in and the same "slide along the flow back to y = 0" correction. Pinv: the reversed flow, first crossing with the
// reversed-time direction -1 at t > 1e-6. Integrator: Boost.Odeint dense-output Dormand-Prince 5(4), abs = rel = 1e-12
// by default, events located by bisection on the dense output to |dt| <= 1e-14 (1 + t).
// Status: candidate for a REGISTERED amendment of B15's map implementation, after the gate (kerr_p_gate.py).
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
// integrate from s until the first event (y crosses 0 with direction dir) at t > 1e-6; returns false if t > tmax
static bool to_event(St& s, double& tev, bool var, double sign, double dir, double tmax) {
  using namespace boost::numeric::odeint;
  auto stepper = make_dense_output(ATOL, RTOL, runge_kutta_dopri5<St>());
  Rhs rhs{var, sign};
  stepper.initialize(s, 0.0, 1e-6);
  St a, b, m;
  while (true) {
    auto iv = stepper.do_step(rhs);
    double t0 = iv.first, t1 = iv.second;
    if (t0 > tmax) return false;
    stepper.calc_state(t0, a); b = stepper.current_state();
    double ya = a[1], yb = b[1];
    bool cross = dir > 0 ? (ya < 0 && yb >= 0) : (ya > 0 && yb <= 0);
    if (cross && t1 > 1e-6) {
      double lo = std::max(t0, 1e-6), hi = t1;
      for (int it = 0; it < 200 && hi - lo > 1e-14 * (1 + hi); ++it) {
        double mid = 0.5 * (lo + hi); stepper.calc_state(mid, m);
        bool before = dir > 0 ? (m[1] < 0) : (m[1] > 0);
        if (before) lo = mid; else hi = mid;
      }
      tev = hi; stepper.calc_state(hi, s); return true;
    }
  }
}
extern "C" {
void kerr_set(double k, double alpha, double beta, double E, double L, double rtol, double atol) {
  C5[0] = k; C5[1] = alpha; C5[2] = beta; C5[3] = E; C5[4] = L; RTOL = rtol; ATOL = atol;
}
double kerr_py(double x, double px) {
  double in[2] = {x, 0.0}, g[3]; mn_lift<double>(in, g, C5);
  double r = (-1.0 - g[0] * px * px - 2 * g[2]) / g[1];
  return r > 0 ? std::sqrt(r) : NAN;
}
// out: x, px, T, and if jac: DP (2x2 row-major) -> 7 doubles. Returns 1 on success, 0 if no return within tmax.
int kerr_P(double x, double px, int n, int jac, double tmax, double* out) {
  double py = kerr_py(x, px); if (!(py == py)) return 0;
  St s{}; s[0] = x; s[1] = 0; s[2] = px; s[3] = py;
  if (jac) for (int i = 0; i < 4; ++i) s[4 + 5 * i] = 1;
  double T = 0;
  for (int k = 0; k < n; ++k) { double te; if (!to_event(s, te, jac, 1.0, 1.0, tmax)) return 0; s[1] = 0; T += te; }
  out[0] = s[0]; out[1] = s[2]; out[2] = T;
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
int kerr_Pinv(double x, double px, double tmax, double* out) {
  double py = kerr_py(x, px); if (!(py == py)) return 0;
  St s{}; s[0] = x; s[1] = 0; s[2] = px; s[3] = py; double te;
  if (!to_event(s, te, false, -1.0, -1.0, tmax)) return 0;
  out[0] = s[0]; out[1] = s[2]; return 1;
}
}
