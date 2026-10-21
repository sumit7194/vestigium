// mn_diag.cpp -- DIAGNOSTIC ONLY (no verdicts): step-by-step enclosure growth of one MN piece, to locate where the
// 2026-10-20 smoke test (horseshoe_results/mn_smoke/mn1.*) lost its enclosure. Same field, lift, set type and
// solver construction as hs_cover (system mn); the time map runs to T with stopAfterStep and logs every step.
// Usage: mn_diag <prec> <order> <halfwidth p/q> <T> [every] [naive|mv] [tripleton|rect2|pped2] [pscale p/q]
//   pscale c: integrate in P = c p (exact constant linear change of variables; the field is (xdot, ydot, c pdot));
//   widths and midpoints are printed back in the original p units.
//   halfwidth 0 = a point start at the box centre (pure integrator error, no initial width).
//   lift naive (default) = hs_cover's lift: the p_y radicand evaluated once on the hull.
//   lift mv = that enclosure intersected with the mean-value form rad(c) + D rad(hull) (hull - c); both are rigorous.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <iostream>
#include <string>

using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;
typedef capd::MpIVector IV;
typedef capd::MpIMatrix IM;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q);
  if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s);
  mpq_canonicalize(q);
  R lo, hi;
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU);
  mpq_clear(q);
  return MpInterval(lo, hi);
}
static double d(const R& r) { return mpfr_get_d(r.*RepAccess::rep, MPFR_RNDN); }
static double w(const MpInterval& x) { return d(x.rightBound()) - d(x.leftBound()); }

inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
static MpInterval MNC[5];
void mn_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn_field<Node>(in, o, c); }
static MpInterval PSC(1);
void mn_vf_s(Node, Node in[], int, Node o[], int, Node par[], int) {   // par[5] = c
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[4] = {in[0], in[1], in[2] / par[5], in[3] / par[5]}, g[4];
  mn_field<Node>(z, g, c);
  o[0] = g[0]; o[1] = g[1]; o[2] = par[5] * g[2]; o[3] = par[5] * g[3];
}
// p_y radicand on the section as a map (x, y, p_x) -> rad, for its derivative (y is evaluated at exactly 0)
void rad_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, xy[2] = {in[0], in[1]}, g[3];
  mn_lift<Node>(xy, g, c);
  o[0] = (Node(-1) - g[0] * in[2] * in[2] - Node(2) * g[2]) / g[1];
}

template <class SetT>
static void run(capd::MpIOdeSolver& solver, const IV& x0, const IM& C, const IV& r0, const MpInterval& T, long every,
                const char* prec, int order, const char* hws, const char* Ts, const std::string& mode, const char* setname,
                const MpInterval& pyv) {
  SetT s(x0, C, r0);
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  std::printf("# prec %s order %d halfwidth %s T %s lift %s set %s ; initial py width %.3e\n", prec, order, hws, Ts, mode.c_str(), setname, w(pyv));
  std::printf("# step t h  w_x w_y w_px w_py (step enclosure)  W_x W_px (set at step end)  mid_x mid_y\n");
  long n = 0;
  try {
    do {
      tm(T, s);
      IV b = s.getLastEnclosure(), v = IV(s);
      ++n;
      if (n % every == 0)
        std::printf("%ld %.6f %.3e  %.3e %.3e %.3e %.3e  %.3e %.3e  %.6f %.6f\n", n, d(tm.getCurrentTime().leftBound()),
                    d(solver.getStep().leftBound()), w(b[0]), w(b[1]), w(b[2] / PSC), w(b[3] / PSC), w(v[0]), w(v[2] / PSC),
                    d(v[0].mid().leftBound()), d(v[1].mid().leftBound()));
      std::fflush(stdout);
    } while (!tm.completed());
    std::printf("COMPLETED steps=%ld\n", n);
  } catch (std::exception& e) {
    IV v = IV(s);
    std::printf("THREW at step %ld t=%.6f: %s\n  last set widths x %.3e y %.3e px %.3e py %.3e\n", n,
                d(tm.getCurrentTime().leftBound()), e.what(), w(v[0]), w(v[1]), w(v[2] / PSC), w(v[3] / PSC));
  }
}

int main(int argc, char** argv) {
  if (argc < 5) { std::cerr << "usage: mn_diag prec order halfwidth T [every]\n"; return 2; }
  R::setDefaultPrecision(std::stoi(argv[1]));
  int order = std::stoi(argv[2]); MpInterval hw = Q(argv[3]); MpInterval T = Q(argv[4]);
  long every = argc > 5 ? std::stol(argv[5]) : 1;
  std::string mode = argc > 6 ? argv[6] : "naive";
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  MpInterval cx = Q("36419361737/10000000000"), cp = Q("60360992808/10000000000");
  // lift exactly as hs_cover (system mn): w = (x, p_x), y = 0, p_y > 0 from H = -1/2 on the hull
  MpInterval r(-hw.rightBound(), hw.rightBound()), wh0 = cx + r, wh1 = cp + r;
  MpInterval in2[2] = {wh0, MpInterval(0)}, out[3];
  mn_lift<MpInterval>(in2, out, MNC);
  MpInterval rad = (MpInterval(-1) - out[0] * wh1 * wh1 - 2 * out[2]) / out[1];
  std::printf("# naive radicand width %.3e\n", w(rad));
  if (mode == "mv") {
    capd::MpIMap fr(rad_vf, 3, 1, 5); for (int i = 0; i < 5; ++i) fr.setParameter(i, MNC[i]);
    IV c3(3), h3(3); c3[0] = cx; c3[2] = cp; h3[0] = wh0; h3[2] = wh1;     // y = [0, 0] exactly in both
    IM D(1, 3); IV rh = fr(h3, D); IV rc = fr(c3);
    MpInterval mv = rc[0] + D[0][0] * (wh0 - cx) + D[0][2] * (wh1 - cp);
    std::printf("# mv radicand width %.3e  (D_x %.3e, D_px %.3e)\n", w(mv), d(D[0][0].mid().leftBound()), d(D[0][2].mid().leftBound()));
    if (!intersection(rad, mv, rad)) { std::cout << "empty intersection (BUG)\n"; return 1; }
  }
  if (!(rad.leftBound() > 0)) { std::cout << "radicand not > 0\n"; return 1; }
  MpInterval pyv = sqrt(rad), pm = pyv.mid();
  IV x0(4), r0(4); IM C(4, 4);
  x0[0] = cx; x0[2] = cp; x0[3] = pm; C[0][0] = 1; C[2][1] = 1; C[3][2] = 1; C[1][3] = 1;
  r0[0] = r; r0[1] = r; r0[2] = pyv - pm; r0[3] = 0;
  if (argc > 8) PSC = Q(argv[8]);
  for (int i = 2; i < 4; ++i) { x0[i] = x0[i] * PSC; for (int j = 0; j < 4; ++j) C[i][j] = C[i][j] * PSC; }
  capd::MpIMap f(mn_vf_s, 4, 4, 6); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]); f.setParameter(5, PSC);
  capd::MpIOdeSolver solver(f, order);
  std::string set = argc > 7 ? argv[7] : "tripleton";
  if (set == "tripleton") run<capd::MpC0TripletonSet>(solver, x0, C, r0, T, every, argv[1], order, argv[3], argv[4], mode, "tripleton", pyv);
  else if (set == "rect2") run<capd::MpC0Rect2Set>(solver, x0, C, r0, T, every, argv[1], order, argv[3], argv[4], mode, "rect2", pyv);
  else if (set == "pped2") run<capd::MpC0Pped2Set>(solver, x0, C, r0, T, every, argv[1], order, argv[3], argv[4], mode, "pped2", pyv);
  else { std::cerr << "unknown set\n"; return 2; }
  return 0;
}
