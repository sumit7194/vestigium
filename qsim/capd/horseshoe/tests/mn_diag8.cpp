// mn_diag8.cpp -- DIAGNOSTIC ONLY (no verdicts): the augmented 8-D MN field (gen/mn_field8.h, mn_codegen8.py) through
// one piece, logging every step, to compare with mn_diag (4-D). Same box, p_y lift (mean-value form, as mn_diag mv),
// solver construction and set type (C0 tripleton).
// Initial lift of (a, b, E2, eG) on the box (y = 0 exactly; they depend on x only there), mean-value form KEEPING the
// correlation with x:  q(x) in q(c) + q_x(c) dx + (q_x(hull) - q_x(c)) dx,  dx in [-h, h]:
//   centre mid q(c); frame column of x gets q_x(c) (an interval); own radius = (q(c) - mid) + (q_x(hull) - q_x(c)) [-h, h].
// Consistency (every step): the tracked (a, b, E2, eG) hull must intersect mn8_aux(x, y) evaluated on the (x, y) hull;
// the widths of both are logged every `every` steps.
// Usage: mn_diag8 <prec> <order> <halfwidth p/q> <T> [every]
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
#include "../gen/mn_field8.h"
static MpInterval MNC[5];
void mn8_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn8_field<Node>(in, o, c); }
void aux_vf(Node, Node in[], int, Node o[], int, Node par[], int) {   // (x, y) -> (a, b, E2, eG)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]};
  mn8_aux<Node>(z, o, c);                                              // mn8_aux reads in[0], in[1] only
}
void rad_vf(Node, Node in[], int, Node o[], int, Node par[], int) {   // (x, y, p_x) -> p_y radicand (as mn_diag)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, xy[2] = {in[0], in[1]}, g[3];
  mn_lift<Node>(xy, g, c);
  o[0] = (Node(-1) - g[0] * in[2] * in[2] - Node(2) * g[2]) / g[1];
}

int main(int argc, char** argv) {
  if (argc < 5) { std::cerr << "usage: mn_diag8 prec order halfwidth T [every]\n"; return 2; }
  R::setDefaultPrecision(std::stoi(argv[1]));
  int order = std::stoi(argv[2]); MpInterval hw = Q(argv[3]); MpInterval T = Q(argv[4]);
  long every = argc > 5 ? std::stol(argv[5]) : 1;
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  MpInterval cx = Q("36419361737/10000000000"), cp = Q("60360992808/10000000000");
  MpInterval r(-hw.rightBound(), hw.rightBound()), wh0 = cx + r, wh1 = cp + r;
  // p_y: naive on the hull intersected with the mean-value form (identical to mn_diag mode mv)
  MpInterval in2[2] = {wh0, MpInterval(0)}, out[3];
  mn_lift<MpInterval>(in2, out, MNC);
  MpInterval rad = (MpInterval(-1) - out[0] * wh1 * wh1 - 2 * out[2]) / out[1];
  {
    capd::MpIMap fr(rad_vf, 3, 1, 5); for (int i = 0; i < 5; ++i) fr.setParameter(i, MNC[i]);
    IV c3(3), h3(3); c3[0] = cx; c3[2] = cp; h3[0] = wh0; h3[2] = wh1;
    IM D(1, 3); fr(h3, D); IV rc = fr(c3);
    MpInterval mv = rc[0] + D[0][0] * (wh0 - cx) + D[0][2] * (wh1 - cp);
    if (!intersection(rad, mv, rad)) { std::cout << "empty p_y intersection (BUG)\n"; return 1; }
  }
  if (!(rad.leftBound() > 0)) { std::cout << "radicand not > 0\n"; return 1; }
  MpInterval pyv = sqrt(rad), pm = pyv.mid();
  // (a, b, E2, eG): correlated mean-value lift in x (y = 0)
  capd::MpIMap fa(aux_vf, 2, 4, 5); for (int i = 0; i < 5; ++i) fa.setParameter(i, MNC[i]);
  IV c2(2), h2(2); c2[0] = cx; h2[0] = wh0;
  IM Dh(4, 2), Dc(4, 2); fa(h2, Dh); IV qc = fa(c2, Dc);
  IV x0(8), r0(8); IM C(8, 8);
  x0[0] = cx; x0[2] = cp; x0[3] = pm; C[0][0] = 1; C[2][1] = 1; C[3][2] = 1; C[1][3] = 1;
  r0[0] = r; r0[1] = r; r0[2] = pyv - pm; r0[3] = 0;
  std::printf("# prec %s order %d halfwidth %s T %s ; py width %.3e\n", argv[1], order, argv[3], argv[4], w(pyv));
  const char* nm[4] = {"a", "b", "E2", "eG"};
  for (int i = 0; i < 4; ++i) {
    MpInterval m = qc[i].mid();
    x0[4 + i] = m; C[4 + i][0] = Dc[i][0]; C[4 + i][4 + i] = 1;
    r0[4 + i] = (qc[i] - m) + (Dh[i][0] - Dc[i][0]) * r;
    MpInterval naive = fa(h2)[i];
    std::printf("# lift %s = %.12e  slope %.4e  own radius width %.3e  (naive hull width %.3e, linear %.3e)\n", nm[i],
                d(m.leftBound()), d(Dc[i][0].mid().leftBound()), w(r0[4 + i]), w(naive), w(Dc[i][0] * r));
  }
  capd::MpIMap f(mn8_vf, 8, 8, 5); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]);
  capd::MpIOdeSolver solver(f, order);
  capd::MpC0TripletonSet s(x0, C, r0);
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  std::printf("# step t h  W_x W_px W_a W_b (set)  Wfresh_a Wfresh_b (aux on the set's (x,y) hull)  mid_x mid_y\n");
  long n = 0;
  try {
    do {
      tm(T, s); IV v = IV(s); ++n;
      IV xy(2); xy[0] = v[0]; xy[1] = v[1]; IV fr = fa(xy);
      for (int i = 0; i < 4; ++i) { MpInterval tmp; if (!intersection(v[4 + i], fr[i], tmp)) throw std::runtime_error(std::string("consistency: tracked ") + nm[i] + " misses fresh enclosure (BUG)"); }
      if (n % every == 0)
        std::printf("%ld %.6f %.3e  %.3e %.3e %.3e %.3e  %.3e %.3e  %.6f %.6f\n", n, d(tm.getCurrentTime().leftBound()),
                    d(solver.getStep().leftBound()), w(v[0]), w(v[2]), w(v[4]), w(v[5]), w(fr[0]), w(fr[1]),
                    d(v[0].mid().leftBound()), d(v[1].mid().leftBound()));
      std::fflush(stdout);
    } while (!tm.completed());
    std::printf("COMPLETED steps=%ld\n", n);
  } catch (std::exception& e) {
    IV v = IV(s);
    std::printf("THREW at step %ld t=%.6f: %s\n  last set widths x %.3e y %.3e px %.3e py %.3e a %.3e b %.3e\n", n,
                d(tm.getCurrentTime().leftBound()), e.what(), w(v[0]), w(v[1]), w(v[2]), w(v[3]), w(v[4]), w(v[5]));
  }
  return 0;
}
