// mn_diag8.cpp -- DIAGNOSTIC ONLY (no verdicts): the augmented 8-D MN field (gen/mn_field8.h, mn_codegen8.py) through
// one piece, logging every step, to compare with mn_diag (4-D). Same box, p_y lift (mean-value form, as mn_diag mv),
// solver construction and set type (C0 tripleton).
// Initial lift of (a, b, E2, eG) on the box (y = 0 exactly; they depend on x only there), mean-value form KEEPING the
// correlation with x:  q(x) in q(c) + q_x(c) dx + (q_x(hull) - q_x(c)) dx,  dx in [-h, h]:
//   centre mid q(c); frame column of x gets q_x(c) (an interval); own radius = (q(c) - mid) + (q_x(hull) - q_x(c)) [-h, h].
// Consistency (every step): the tracked (a, b, E2, eG) hull must intersect mn8_aux(x, y) evaluated on the (x, y) hull;
// the widths of both are logged every `every` steps.
// Usage: mn_diag8 <prec> <order> <halfwidth p/q> <T> [every] [decomp_from_t] [tripleton|cn<deg>] [corrpy]
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <sstream>
#include <cstdlib>

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

// read-only view of the tripleton's parts: X = x + C r0 + (B r  intersected with  Q q)
struct Peek : capd::MpC0TripletonSet {
  using capd::MpC0TripletonSet::MpC0TripletonSet;
  IV Cr0() const { return m_C * m_r0; } IV Br() const { return m_B * m_r; } IV Qq() const { return m_Q * m_q; }
  IV X() const { return m_x; } IM Cm() const { return m_C; } IV R0() const { return m_r0; }
  IM Bm() const { return m_B; } IV Rr() const { return m_r; } IM Qm() const { return m_Q; } IV Qv() const { return m_q; }
  double radC_over_midC() const {                       // max entry radius / max |entry midpoint|
    double rmax = 0, mmax = 0;
    for (int i = 0; i < (int)m_C.numberOfRows(); ++i) for (int j = 0; j < (int)m_C.numberOfColumns(); ++j) {
      rmax = std::max(rmax, w(m_C[i][j]) / 2); mmax = std::max(mmax, std::fabs(d(m_C[i][j].mid().leftBound())));
    }
    return rmax / mmax;
  }
};


// ---- strip re-framing (diagnostic; env STRIP_T, STRIP_V "vx vy vpx vpy", STRIP_W p/q or "full", STRIP_AXIS v1|other)
// At t = STRIP_T the set X = x + C r0 + (B r  meet  Q q) is re-framed in an orthonormal POINT frame P (Gram-Schmidt from
// v1 extended to the aux states, then the set's own columns by size, then unit vectors), Z = P^-1 (X - x) as an interval
// vector (a sound superset), and the strip keeps z_k in [-W, W] (k = 0 for v1, 1 for the next axis); the rest of Z is kept.
static std::vector<std::vector<double>> gram_schmidt(std::vector<std::vector<double>> cand, int n) {
  std::vector<std::vector<double>> P;
  for (auto& v : cand) {
    for (auto& p : P) { double dd = 0; for (int i = 0; i < n; ++i) dd += v[i] * p[i]; for (int i = 0; i < n; ++i) v[i] -= dd * p[i]; }
    double nn = 0; for (int i = 0; i < n; ++i) nn += v[i] * v[i]; nn = std::sqrt(nn);
    if (nn < 1e-12) continue;
    for (int i = 0; i < n; ++i) v[i] /= nn;
    P.push_back(v); if ((int)P.size() == n) break;
  }
  return P;
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
  if (argc > 8 && std::string(argv[8]) == "corrpy") {   // p_y tied to (dx, dp_x) to first order (mean-value form, on shell)
    capd::MpIMap fr(rad_vf, 3, 1, 5); for (int i = 0; i < 5; ++i) fr.setParameter(i, MNC[i]);
    IV c3(3), h3(3); c3[0] = cx; c3[2] = cp; h3[0] = wh0; h3[2] = wh1;
    IM Dh(1, 3), Dc(1, 3); fr(h3, Dh); IV rc = fr(c3, Dc);
    MpInterval pc = sqrt(rc[0]);                         // p_y(c)
    MpInterval sx_c = Dc[0][0] / (2 * pc), sp_c = Dc[0][2] / (2 * pc);       // grad p_y at c
    MpInterval sx_h = Dh[0][0] / (2 * pyv), sp_h = Dh[0][2] / (2 * pyv);     // grad p_y on the hull (p_y in pyv there)
    MpInterval pmid = pc.mid();
    x0[3] = pmid; C[3][0] = sx_c; C[3][1] = sp_c;        // frame: p_y follows x and p_x
    r0[2] = (pc - pmid) + (sx_h - sx_c) * r + (sp_h - sp_c) * r;      // own radius: centre width + mean-value remainder
    std::printf("# corrpy: slopes dpy/dx %.6e dpy/dpx %.6e ; own p_y radius width %.3e (was %.3e)\n",
                d(sx_c.mid().leftBound()), d(sp_c.mid().leftBound()), w(r0[2]), w(pyv));
  }
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
  double decomp_from = argc > 6 ? std::stod(argv[6]) : 1e300;          // print the set decomposition every step from t
  std::string settype = argc > 7 ? argv[7] : "tripleton";
  if (settype.rfind("cn", 0) == 0) {                    // C^r jet set of degree r on the same 8-D field and lift
    int deg = std::stoi(settype.substr(2));
    capd::MpIMap fn(mn8_vf, 8, 8, 5, deg); for (int i = 0; i < 5; ++i) fn.setParameter(i, MNC[i]);
    capd::MpICnOdeSolver cs(fn, order);
    capd::MpCnRect2Set sc(x0, C, r0, deg);
    capd::MpICnTimeMap tc(cs); tc.stopAfterStep(true);
    std::printf("# set cn%d\n", deg);
    long m = 0;
    try {
      do {
        tc(T, sc); IV v = IV(sc); ++m;
        IV xy(2); xy[0] = v[0]; xy[1] = v[1]; IV fr = fa(xy);
        for (int i = 0; i < 4; ++i) { MpInterval tmp; if (!intersection(v[4 + i], fr[i], tmp)) throw std::runtime_error(std::string("consistency: tracked ") + nm[i] + " misses fresh enclosure (BUG)"); }
        double tnow = d(tc.getCurrentTime().leftBound());
        if (m % every == 0 || tnow >= decomp_from)
          std::printf("%ld %.6f %.3e  %.3e %.3e %.3e %.3e  %.3e %.3e  %.6f %.6f\n", m, tnow, d(cs.getStep().leftBound()),
                      w(v[0]), w(v[2]), w(v[4]), w(v[5]), w(fr[0]), w(fr[1]), d(v[0].mid().leftBound()), d(v[1].mid().leftBound()));
        std::fflush(stdout);
      } while (!tc.completed());
      std::printf("COMPLETED steps=%ld\n", m);
    } catch (std::exception& e) {
      IV v = IV(sc);
      std::printf("THREW at step %ld t=%.6f: %s\n  last set widths x %.3e px %.3e\n", m, d(tc.getCurrentTime().leftBound()), e.what(), w(v[0]), w(v[2]));
    }
    return 0;
  }
  const char* stT = std::getenv("STRIP_T");
  MpInterval Tend = T; if (stT) T = Q(stT);              // integrate to the cut first
  Peek s0(x0, C, r0);
  Peek* sp = &s0; std::unique_ptr<Peek> s2;
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  std::printf("# step t h  W_x W_px W_a W_b (set)  Wfresh_a Wfresh_b (aux on the set's (x,y) hull)  mid_x mid_y\n");
  long n = 0;
  try {
   for (int phase = 0; phase < (stT ? 2 : 1); ++phase) {
    Peek& s = *sp;
    if (phase == 1) { T = Tend; }
    do {
      tm(T, s); IV v = IV(s); ++n;
      IV xy(2); xy[0] = v[0]; xy[1] = v[1]; IV fr = fa(xy);
      for (int i = 0; i < 4; ++i) { MpInterval tmp; if (!intersection(v[4 + i], fr[i], tmp)) throw std::runtime_error(std::string("consistency: tracked ") + nm[i] + " misses fresh enclosure (BUG)"); }
      double tnow = d(tm.getCurrentTime().leftBound());
      if (tnow >= decomp_from) {
        IV a1 = s.Cr0(), a2 = s.Br(), a3 = s.Qq();
        std::printf("DECOMP %ld %.6f h %.3e  Cr0 x %.3e px %.3e | Br x %.3e px %.3e | Qq x %.3e px %.3e | set x %.3e px %.3e | radC/midC %.2e\n", n, tnow,
                    d(solver.getStep().leftBound()), w(a1[0]), w(a1[2]), w(a2[0]), w(a2[2]), w(a3[0]), w(a3[2]), w(v[0]), w(v[2]), s.radC_over_midC());
      }
      if (n % every == 0)
        std::printf("%ld %.6f %.3e  %.3e %.3e %.3e %.3e  %.3e %.3e  %.6f %.6f\n", n, d(tm.getCurrentTime().leftBound()),
                    d(solver.getStep().leftBound()), w(v[0]), w(v[2]), w(v[4]), w(v[5]), w(fr[0]), w(fr[1]),
                    d(v[0].mid().leftBound()), d(v[1].mid().leftBound()));
      std::fflush(stdout);
    } while (!tm.completed());
    if (phase == 0 && stT) {                               // build the strip
      IV x = s.X(); IM Cm = s.Cm(), Bm = s.Bm(), Qm = s.Qm(); IV r0v = s.R0(), rv = s.Rr(), qv = s.Qv();
      std::vector<double> v1(8, 0.0); { std::istringstream is(std::getenv("STRIP_V")); for (int i = 0; i < 4; ++i) is >> v1[i]; }
      IV xy(2); xy[0] = x[0].mid(); xy[1] = x[1].mid(); IM Da(4, 2); fa(xy, Da);
      for (int i = 0; i < 4; ++i) v1[4 + i] = d(Da[i][0].mid().leftBound()) * v1[0] + d(Da[i][1].mid().leftBound()) * v1[1];
      std::vector<std::pair<double, std::vector<double>>> cols;
      for (int j = 0; j < 8; ++j) for (int which = 0; which < 2; ++which) {
        std::vector<double> c(8); double nn = 0;
        for (int i = 0; i < 8; ++i) { c[i] = d((which ? Bm[i][j] : Cm[i][j]).mid().leftBound()) * w(which ? rv[j] : r0v[j]) / 2; nn += c[i] * c[i]; }
        if (nn > 0) cols.push_back({std::sqrt(nn), c});
      }
      std::sort(cols.begin(), cols.end(), [](const auto& a, const auto& b) { return a.first > b.first; });
      std::vector<std::vector<double>> cand = {v1};
      for (auto& c : cols) cand.push_back(c.second);
      for (int i = 0; i < 8; ++i) { std::vector<double> e(8, 0.0); e[i] = 1; cand.push_back(e); }
      auto Pv = gram_schmidt(cand, 8);
      double cosv = 0, n1 = 0, n2 = 0; for (int i = 0; i < 8; ++i) { cosv += v1[i] * cols[0].second[i]; n1 += v1[i] * v1[i]; n2 += cols[0].second[i] * cols[0].second[i]; }
      IM P(8, 8); for (int j = 0; j < 8; ++j) for (int i = 0; i < 8; ++i) P[i][j] = MpInterval(Pv[j][i]);
      IM Pinv = capd::matrixAlgorithms::gaussInverseMatrix(P);
      IV Z = (Pinv * Cm) * r0v + (Pinv * Bm) * rv, Zq = (Pinv * Cm) * r0v + (Pinv * Qm) * qv;
      if (!intersection(Z, Zq, Z)) throw std::runtime_error("strip: empty Z intersection (BUG)");
      std::printf("# STRIP at t=%.6f: abs cosine of v1 vs longest set axis %.4f ; Z widths:", d(s.getCurrentTime().leftBound()), std::fabs(cosv) / std::sqrt(n1 * n2));
      for (int i = 0; i < 8; ++i) std::printf(" %.3e", w(Z[i])); std::printf("\n");
      std::string Wsp = std::getenv("STRIP_W") ? std::getenv("STRIP_W") : "full";
      int k = (std::getenv("STRIP_AXIS") && std::string(std::getenv("STRIP_AXIS")) == "other") ? 1 : 0;
      if (Wsp != "full") {
        MpInterval Wq = Q(Wsp), cut(-Wq.rightBound(), Wq.rightBound());
        if (!intersection(Z[k], cut, Z[k])) throw std::runtime_error("strip: cut misses Z (BUG)");
        std::printf("# STRIP axis %d half-width %s ; strips needed to tile z_%d: %.3e\n", k, Wsp.c_str(), k, w(s.R0()[0]) >= 0 ? (double)(w(Zq[k]) / (2 * d(Wq.rightBound()))) : 0.0);
      }
      s2.reset(new Peek(x, P, Z, s.getCurrentTime()));
      sp = s2.get();
    }
   }
    std::printf("COMPLETED steps=%ld\n", n);
  } catch (std::exception& e) {
    IV v = IV(*sp);
    std::printf("THREW at step %ld t=%.6f: %s\n  last set widths x %.3e y %.3e px %.3e py %.3e a %.3e b %.3e\n", n,
                d(tm.getCurrentTime().leftBound()), e.what(), w(v[0]), w(v[1]), w(v[2]), w(v[3]), w(v[4]), w(v[5]));
  }
  return 0;
}
