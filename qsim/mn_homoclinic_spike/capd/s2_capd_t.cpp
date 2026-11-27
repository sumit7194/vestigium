// s2_capd.cpp -- MN homoclinic spike S2 (PREREG.md S2 AMENDMENT A1-A10), rigorous part. MPFR intervals only, under
// proof_guard.h (guard_build.sh). Written by Claude Opus 5.5 (Quantum), 2026-11-27.
//
// The field: the B10-regularised MN/Kerr reduced field gen/mn_field.h (mn_codegen.py; the same formulas as
// mn_s5_gate.mine, G-norm-checked in S1), state (x, y, p_x, p_y), c = (k, alpha, beta, E, L) as exact-rational
// enclosures. (M, a) = (5, 3): k = 4, alpha = -1/3. Section Sigma = {y = 0}, crossing MinusPlus (ydot > 0); section
// coordinates w = (x, p_x); p_y lifted by the positive root of H = -1/2.
//
// Mode "ret" (S2-0, the cost/width pilot): one rigorous C^1 return of the box w = (x, p_x) +- hw:
//   C^1 time map, step by step to t = Tstop (every step enclosure: domain S4 checks, finite, progress lines), then the
//   C^1 Poincare map to the next upward crossing, then a C^0 replay of [Tstop, rt] for the domain checks on the last
//   steps. Prints the return-time, P(box) and the section derivative DP_sec (2 x 2) enclosures and their widths.
//   DP_sec = rows (x, p_x) of DP_full * C_lift, C_lift = d(x, 0, p_x, p_y(x, p_x)) / d(x, p_x), with
//   dp_y/dx = pxdot / ydot and dp_y/dp_x = -xdot / ydot (from H; enclosed over the box).
// No watchdog, no caps (the no-hard-caps rule); the only stops are thrown failures (domain, non-finite, energy).
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <gmp.h>
#include <chrono>
#include <cstdio>
#include <cmath>
#include <iostream>
#include <string>
#include "proof_guard.h"

using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;
typedef capd::MpIVector IV;
typedef capd::MpIMatrix IM;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s0) {           // exact rational "p/q" or a decimal string, enclosed outward
  std::string s = s0; mpq_t q; mpq_init(q);
  size_t dot = s.find('.');
  if (dot != std::string::npos) {                       // decimal -> p/10^d exactly
    std::string ip = s.substr(0, dot), fp = s.substr(dot + 1); std::string num = ip + fp; std::string den = "1" + std::string(fp.size(), '0');
    s = num + "/" + den;
  }
  if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s0);
  mpq_canonicalize(q);
  R lo, hi;
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU);
  mpq_clear(q);
  if (!(lo <= hi)) throw std::runtime_error("rational enclosure failed: " + s0);
  return MpInterval(lo, hi);
}
static std::string dec(const R& r, int d = 17) { char* s = nullptr; std::string f = "%." + std::to_string(d) + "Re"; mpfr_asprintf(&s, f.c_str(), r.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o; }
static std::string iv(const MpInterval& x) { return "[" + dec(x.leftBound()) + "," + dec(x.rightBound()) + "]"; }
static double dbl(const R& r) { return mpfr_get_d(r.*RepAccess::rep, MPFR_RNDN); }
static double wid(const MpInterval& x) { return dbl((x.rightBound() - x.leftBound())); }

inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "gen/mn_field.h"
static MpInterval MNC[5];
static int TOLEXP = 0;   // 0 = CAPD default (10^-(digits+3)); else abs = rel tolerance 10^-TOLEXP for every solver
static void settol(capd::MpIOdeSolver& s) { if (TOLEXP > 0) { double t = std::pow(10.0, -TOLEXP); s.setAbsoluteTolerance(t); s.setRelativeTolerance(t); } }   // step control only (a double by CAPD design); never a proof value
void mn_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn_field<Node>(in, o, c); }

static MpInterval mn_Hi(const IV& x) { MpInterval in[4] = {x[0], x[1], x[2], x[3]}, out[1]; mn_H<MpInterval>(in, out, MNC); return out[0]; }

// S4 domain (as hs_cover's B9 checks): fail closed on every step enclosure
static void mn_domain(const IV& b) {
  capd_proof::require_finite_all(b, "S4 enclosure");
  const MpInterval &x = b[0], &y = b[1];
  if (!((x - 1).leftBound() >= MpInterval(1) / 20)) throw std::runtime_error("S4: x - 1 < 0.05 possible");
  if (!((x * x + y * y - 1).leftBound() >= MpInterval(1) / 4)) throw std::runtime_error("S4: R^2 < 0.25 possible");
  if (!((1 - y * y).leftBound() > 0)) throw std::runtime_error("S4: 1 - y^2 > 0 not certified");
  MpInterval in[2] = {x, y}, out[1];
  mn_B<MpInterval>(in, out, MNC); capd_proof::require_finite(out[0], "S4 B");
  if (!(out[0].leftBound() > 0)) throw std::runtime_error("S4: B > 0 (det g < 0) not certified");
  MpInterval d = MpInterval(1) / 40, xi[2] = {x + MpInterval(-d.rightBound(), d.rightBound()), y + MpInterval(-d.rightBound(), d.rightBound())};
  mn_gpp<MpInterval>(xi, out, MNC); capd_proof::require_finite(out[0], "S4 g_phiphi");
  if (!(out[0].leftBound() > 0)) throw std::runtime_error("S4: g_phiphi > 0 on the inflated box not certified");
}

static double secs(std::chrono::steady_clock::time_point t0) { return std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count(); }

struct RetOut { MpInterval rt, Px, Ppx; IM Dsec; long steps; double sec; };

static RetOut ret(capd::MpIMap& f, int order, const MpInterval& x, const MpInterval& px, double Tstop, const std::string& label, bool progress) {
  auto t0 = std::chrono::steady_clock::now();
  // lift
  MpInterval lin[2] = {x, MpInterval(0)}, lo[3]; mn_lift<MpInterval>(lin, lo, MNC);
  MpInterval rad = (MpInterval(-1) - lo[0] * px * px - 2 * lo[2]) / lo[1];
  if (!(rad.leftBound() > 0)) throw std::runtime_error("lift: radicand > 0 not certified");
  MpInterval py = sqrt(rad);
  IV X0(4); X0[0] = x; X0[1] = MpInterval(0); X0[2] = px; X0[3] = py;
  IV c(4); for (int i = 0; i < 4; ++i) c[i] = MpInterval(X0[i].mid().leftBound());
  IV r0 = X0 - c;
  // lift Jacobian on the box
  MpInterval fin[4] = {X0[0], X0[1], X0[2], X0[3]}, fo[4]; mn_field<MpInterval>(fin, fo, MNC);
  if (!(fo[1].leftBound() > 0)) throw std::runtime_error("lift: ydot > 0 not certified on the box");
  MpInterval dpydx = fo[2] / fo[1], dpydpx = -fo[0] / fo[1];
  capd::MpIOdeSolver solver(f, order); settol(solver); capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  capd::MpC1Rect2Set s(c, r0);
  long steps = 0; MpInterval T(Tstop);
  do {
    tm(T, s); mn_domain(s.getLastEnclosure()); ++steps;
    if (progress && steps % 200 == 0)
      std::printf("PROG %s steps %ld t %.4f wall %.1f s\n", label.c_str(), steps, dbl(s.getCurrentTime().leftBound()), secs(t0)), std::fflush(stdout);
  } while (!tm.completed());
  IV cS = (IV)s; double tS = dbl(s.getCurrentTime().leftBound());
  capd::MpICoordinateSection section(4, 1); capd::MpIPoincareMap pm(solver, section, capd::poincare::MinusPlus);
  IM D(4, 4); MpInterval rt;
  IV y = pm(s, D, rt);
  capd_proof::require_finite_all(y, "return"); capd_proof::require_finite(rt, "return time");
  IM DP = pm.computeDP(y, D, rt);
  if (!mn_Hi(y).contains(MpInterval(-1) / 2)) throw std::runtime_error("return enclosure misses H = -1/2 (BUG)");
  // C^0 replay of [Tstop, rt] for the domain checks on the Poincare map's own steps
  { capd::MpIOdeSolver rs(f, order); settol(rs); capd::MpITimeMap rtm(rs); rtm.stopAfterStep(true);
    capd::MpC0TripletonSet s0(cS, MpInterval(tS)); MpInterval T2(rt.rightBound());
    do { rtm(T2, s0); mn_domain(s0.getLastEnclosure()); ++steps; } while (!rtm.completed()); }
  IM C(4, 2); C[0][0] = 1; C[2][1] = 1; C[3][0] = dpydx; C[3][1] = dpydpx;
  IM Dsec(2, 2);
  for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) {
    int ri = i == 0 ? 0 : 2; MpInterval acc(0);
    for (int k = 0; k < 4; ++k) acc += DP[ri][k] * C[k][j];
    Dsec[i][j] = acc;
  }
  return RetOut{rt, y[0], y[2], Dsec, steps, secs(t0)};
}

int main(int argc, char** argv) {
  try {
    std::string mode = argc > 1 ? argv[1] : "";
    if (mode != "ret" || argc < 10) { std::cerr << "usage: s2_capd ret <beta p/q> <x> <px> <hw> <Tstop> <prec> <order> <label>\n"; return 2; }
    R::setDefaultPrecision(std::stoi(argv[7])); int order = std::stoi(argv[8]); if (argc > 10) TOLEXP = std::stoi(argv[10]);
    MNC[0] = Q("4"); MNC[1] = Q("-1/3"); MNC[2] = Q(argv[2]);
    MNC[3] = Q("0.93528150456799871854"); MNC[4] = Q("12.972532035607280691");
    capd::MpIMap f(mn_vf, 4, 4, 5); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]);
    MpInterval hw = Q(argv[5]); MpInterval box(-hw.rightBound(), hw.rightBound());
    MpInterval x = Q(argv[3]) + box, px = Q(argv[4]) + box;
    std::printf("RUN %s beta %s x %s px %s hw %s Tstop %s prec %s order %d tol 1e-%d (0 = CAPD default)\n", argv[9], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], order, TOLEXP);
    std::fflush(stdout);
    RetOut o = ret(f, order, x, px, std::stod(argv[6]), argv[9], true);
    double dmax = 0, wmax = 0;
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) { dmax = std::max(dmax, std::max(std::fabs(dbl(o.Dsec[i][j].leftBound())), std::fabs(dbl(o.Dsec[i][j].rightBound())))); wmax = std::max(wmax, wid(o.Dsec[i][j])); }
    std::printf("RESULT %s rt %s\n  Px  %s  width %.3e\n  Ppx %s  width %.3e\n", argv[9], iv(o.rt).c_str(), iv(o.Px).c_str(), wid(o.Px), iv(o.Ppx).c_str(), wid(o.Ppx));
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) std::printf("  DP[%d][%d] %s  width %.3e\n", i, j, iv(o.Dsec[i][j]).c_str(), wid(o.Dsec[i][j]));
    std::printf("SUMMARY %s steps %ld wall_s %.1f maxwidth_P %.3e maxwidth_DP %.3e rel_DP %.3e\n", argv[9], o.steps, o.sec,
                std::max(wid(o.Px), wid(o.Ppx)), wmax, wmax / dmax);
    return 0;
  } catch (std::exception& e) { std::printf("FAIL %s\n", e.what()); return 1; }
}
