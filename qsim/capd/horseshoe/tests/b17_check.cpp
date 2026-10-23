// b17_check.cpp -- the PREREG B17 diagnostic success check for MN set-propagation fixes (no covering verdict).
// One smoke box (F5-R UPO 2 centre, half-width W0) through one full return of the 8-D augmented field
// (gen/mn_field8.h), with the correlated p_y and a/b/E2/eG lifts; C0 tripleton; options by environment:
//   REORG_FACTOR=off|<factor>   CAPD reorganisation policy (default: CAPD's factor 20)
//   QRESEED=<N>                 re-seed the tripleton's Q branch in the needle frame every N steps (0 = never)
// On EVERY step: S4 domain (B9 predicate; B18 structured evaluation + bisection, depth cap 12), S9 (H of the 4-D part contains -1/2), augmented-state consistency
// (tracked a, b, E2, eG meet their fresh enclosures from (x, y)); any failure throws = B17 FAIL.
// Checkpoints (file from tests/b17_checkpoints.py): TIME checkpoints measure the set's widths projected on the
// checkpoint's u1, u2, n_H and the four off-manifold covectors; SECTION checkpoints measure A (P(set) - x0) from CAPD's
// Poincare map in those coordinates (a copy of the set is mapped; the run itself continues by the time map).
// B17 rule per checkpoint (k = 5): set/true <= k on u1 and u2; sum_d width_d g_d <= k true_u2 g_u2 over the fake
// directions (n_H, a, b, E2, eG). Pass = all checkpoints pass and the return section is reached.
// Usage: b17_check <W0 p/q> <checkpoint file .txt>
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

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
void aux_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]};
  mn8_aux<Node>(z, o, c);                                              // reads in[0], in[1] only
}
void rad_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, xy[2] = {in[0], in[1]}, g[3];
  mn_lift<Node>(xy, g, c);
  o[0] = (Node(-1) - g[0] * in[2] * in[2] - Node(2) * g[2]) / g[1];
}

// S4 (B9 predicate, B18 implementation): on the (x, y) part of an enclosure: x - 1 >= 0.05, R^2 >= 0.25, 1 - y^2 > 0,
// B > 0 on the enclosure, and g_phiphi > 0 on the +-0.025 inflated box. B and g_phiphi are evaluated in the structured
// A-free form (gen/mn_field8.h mn8_domain, gated against the original expressions); a box that does not certify is
// bisected (longer side first) down to S4_DEPTH levels; any box still uncertified at the cap is an S4 FAIL.
static const int S4_DEPTH = 12;
static long S4_LEAVES = 0;
static double S4_GMIN = 1e300;                                   // smallest certified lower bound of g_phiphi (data)
void dom_vf(Node, Node in[], int, Node o[], int, Node par[], int) {   // (x, y) -> (B, g_phiphi), structured form
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]};
  mn8_domain<Node>(z, o, c);                                       // reads in[0], in[1] only
}
static std::unique_ptr<capd::MpIMap> DOM;
static bool certify(const MpInterval& x, const MpInterval& y, int which, int depth) {   // which: 0 = B > 0, 1 = g_phiphi > 0
  bool ok = false;
  MpInterval lowg;
  try {
    MpInterval z(0), in[8] = {x, y, z, z, z, z, z, z}, out[2];
    mn8_domain<MpInterval>(in, out, MNC);
    // B18a: mean-value form on the (convex) sub-box, intersected with the plain enclosure
    IV box(2), c(2); box[0] = x; box[1] = y; c[0] = x.mid(); c[1] = y.mid();
    IM D(2, 2); (*DOM)(box, D); IV vc = (*DOM)(c);
    for (int i = 0; i < 2; ++i) {
      MpInterval mv = vc[i] + D[i][0] * (x - c[0]) + D[i][1] * (y - c[1]);
      if (!intersection(out[i], mv, out[i])) throw std::runtime_error("S4: empty intersection of two enclosures (BUG)");
    }
    capd_proof::require_finite(out[which], "S4 domain function");
    ok = out[which].leftBound() > 0 && (which == 0 || out[0].leftBound() > 0);
    lowg = out[1];
  } catch (std::exception& e) {
    if (std::string(e.what()).find("BUG") != std::string::npos) throw;
    ok = false;
  }
  if (ok) { ++S4_LEAVES; if (which == 1) S4_GMIN = std::min(S4_GMIN, d(lowg.leftBound())); return true; }
  if (depth >= S4_DEPTH) return false;
  bool splitx = w(x) >= w(y);
  MpInterval a = splitx ? x : y, m = MpInterval(a.mid().leftBound()), lo(a.leftBound(), m.rightBound()), hi(m.leftBound(), a.rightBound());
  return splitx ? (certify(lo, y, which, depth + 1) && certify(hi, y, which, depth + 1))
                : (certify(x, lo, which, depth + 1) && certify(x, hi, which, depth + 1));
}
static void mn_domain(const IV& b) {
  capd_proof::require_finite_all(b, "S4 enclosure");
  const MpInterval &x = b[0], &y = b[1];
  if (!((x - 1).leftBound() >= MpInterval(1) / 20)) throw std::runtime_error("S4: x - 1 < 0.05 possible");
  if (!((x * x + y * y - 1).leftBound() >= MpInterval(1) / 4)) throw std::runtime_error("S4: R^2 < 0.25 possible");
  if (!((1 - y * y).leftBound() > 0)) throw std::runtime_error("S4: 1 - y^2 > 0 not certified");
  if (!certify(x, y, 0, 0)) throw std::runtime_error("S4: B > 0 (det g < 0) not certified at the depth cap");
  MpInterval dd = MpInterval(1) / 40, ir(-dd.rightBound(), dd.rightBound());
  if (!certify(x + ir, y + ir, 1, 0)) throw std::runtime_error("S4: g_phiphi > 0 on the inflated box not certified at the depth cap");
}
static void s9(const IV& b) {
  MpInterval in[4] = {b[0], b[1], b[2], b[3]}, out[1];
  mn_H<MpInterval>(in, out, MNC);
  if (!out[0].contains(MpInterval(-1) / 2)) throw std::runtime_error("S9: step enclosure misses H = -1/2 (BUG)");
}

struct Peek : capd::MpC0TripletonSet {
  using capd::MpC0TripletonSet::MpC0TripletonSet;
  IM Cm() const { return m_C; } IV R0() const { return m_r0; } IM Bm() const { return m_B; } IV Rr() const { return m_r; }
  IM Qm() const { return m_Q; } IV Qv() const { return m_q; } IV X() const { return m_x; }
  // the set's width along covector n: n.(C r0) + (n.(B r)  meet  n.(Q q))
  MpInterval proj(const IV& n) const {                     // n.x (interval) + along(n): the projected set
    MpInterval c(0); for (int j = 0; j < (int)n.dimension(); ++j) c += n[j] * m_x[j]; return c + along(n);
  }
  MpInterval along(const IV& n) const {
    MpInterval a1(0), a2(0), a3(0);
    IV nC = transpose(m_C) * n, nB = transpose(m_B) * n, nQ = transpose(m_Q) * n;
    for (int j = 0; j < (int)n.dimension(); ++j) { a1 += nC[j] * m_r0[j]; a2 += nB[j] * m_r[j]; a3 += nQ[j] * m_q[j]; }
    MpInterval e; if (!intersection(a2, a3, e)) e = a2;
    return a1 + e;
  }
  // needle-frame re-seed of the Q branch (the Bridge's r-only policy): Q := orthonormalised mid(C) (columns weighted by
  // rad r0, largest first), q := Q^-1 (B r)  meet  Q^-1 (Q_old q_old); C, r0, B, r untouched
  void reseedQ() {
    int n = (int)m_x.dimension();
    std::vector<std::pair<double, std::vector<double>>> cols;
    for (int j = 0; j < n; ++j) {
      std::vector<double> c(n); double nn = 0, rj = w(m_r0[j]) / 2;
      for (int i = 0; i < n; ++i) { c[i] = d(m_C[i][j].mid().leftBound()) * rj; nn += c[i] * c[i]; }
      if (nn > 0) cols.push_back({std::sqrt(nn), c});
    }
    std::sort(cols.begin(), cols.end(), [](const auto& a, const auto& b) { return a.first > b.first; });
    std::vector<std::vector<double>> P;
    auto add = [&](std::vector<double> v) {
      for (auto& p : P) { double dd = 0; for (int i = 0; i < n; ++i) dd += v[i] * p[i]; for (int i = 0; i < n; ++i) v[i] -= dd * p[i]; }
      double nn = 0; for (int i = 0; i < n; ++i) nn += v[i] * v[i]; nn = std::sqrt(nn);
      if (nn < 1e-12 || (int)P.size() == n) return; for (int i = 0; i < n; ++i) v[i] /= nn; P.push_back(v);
    };
    for (auto& c : cols) add(c.second);
    for (int i = 0; i < n; ++i) { std::vector<double> e(n, 0.0); e[i] = 1; add(e); }
    IM Qn(n, n); for (int j = 0; j < n; ++j) for (int i = 0; i < n; ++i) Qn[i][j] = MpInterval(P[j][i]);
    IM iQn = capd::matrixAlgorithms::krawczykInverse(Qn);
    IV q1 = (iQn * m_B) * m_r, q2 = (iQn * m_Q) * m_q, qn(n);
    if (!intersection(q1, q2, qn)) throw std::runtime_error("reseedQ: empty intersection (BUG)");
    m_Q = Qn; m_invQ = iQn; m_q = qn;
  }
};

struct Checkpoint { std::string kind; double t; IV u1, u2, nH; double tu1, tu2; double g[7]; double centre[4]; };
static std::vector<Checkpoint> read_cps(const char* path) {
  std::ifstream in(path); std::vector<Checkpoint> v; std::string kind;
  while (in >> kind) {
    Checkpoint c; c.kind = kind; in >> c.t;
    for (IV* u : {&c.u1, &c.u2, &c.nH}) { *u = IV(8); for (int i = 0; i < 8; ++i) { double x; in >> x; (*u)[i] = MpInterval(x); } }
    in >> c.tu1 >> c.tu2; for (double& g : c.g) in >> g; for (double& x : c.centre) in >> x;
    v.push_back(c);
  }
  return v;
}

int main(int argc, char** argv) {
  if (argc < 3) { std::cerr << "usage: b17_check W0 checkpoints.txt\n"; return 2; }
  R::setDefaultPrecision(128);
  const int order = 20; const double K = 5.0;
  MpInterval hw = Q(argv[1]); auto cps = read_cps(argv[2]);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  MpInterval cx = Q("36419361737/10000000000"), cp = Q("60360992808/10000000000");
  if (const char* off = std::getenv("CENTRE_OFFSET")) {   // containment reference runs: W0 = 0 at a shifted point
    std::istringstream is(off); std::string du, dp; is >> du >> dp; cx = cx + Q(du); cp = cp + Q(dp);
    std::printf("# centre offset %s %s\n", du.c_str(), dp.c_str());
  }
  MpInterval r(-hw.rightBound(), hw.rightBound()), wh0 = cx + r, wh1 = cp + r;
  // p_y: naive hull meet mean-value form, then the correlated (corrpy) lift
  MpInterval in2[2] = {wh0, MpInterval(0)}, out[3];
  mn_lift<MpInterval>(in2, out, MNC);
  MpInterval rad = (MpInterval(-1) - out[0] * wh1 * wh1 - 2 * out[2]) / out[1];
  capd::MpIMap fr(rad_vf, 3, 1, 5); for (int i = 0; i < 5; ++i) fr.setParameter(i, MNC[i]);
  IV c3(3), h3(3); c3[0] = cx; c3[2] = cp; h3[0] = wh0; h3[2] = wh1;
  IM Dh3(1, 3), Dc3(1, 3); fr(h3, Dh3); IV rc = fr(c3, Dc3);
  { MpInterval mv = rc[0] + Dh3[0][0] * (wh0 - cx) + Dh3[0][2] * (wh1 - cp); if (!intersection(rad, mv, rad)) { std::cout << "empty p_y intersection (BUG)\n"; return 1; } }
  if (!(rad.leftBound() > 0)) { std::cout << "S9: radicand not > 0\n"; return 1; }
  MpInterval pyv = sqrt(rad), pc = sqrt(rc[0]), pmid = pc.mid();
  MpInterval sx_c = Dc3[0][0] / (2 * pc), sp_c = Dc3[0][2] / (2 * pc), sx_h = Dh3[0][0] / (2 * pyv), sp_h = Dh3[0][2] / (2 * pyv);
  capd::MpIMap fa(aux_vf, 2, 4, 5); for (int i = 0; i < 5; ++i) fa.setParameter(i, MNC[i]);
  IV c2(2), h2(2); c2[0] = cx; h2[0] = wh0;
  IM Dh(4, 2), Dc(4, 2); fa(h2, Dh); IV qc = fa(c2, Dc);
  IV x0(8), r0(8); IM C(8, 8);
  x0[0] = cx; x0[2] = cp; x0[3] = pmid; C[0][0] = 1; C[2][1] = 1; C[3][0] = sx_c; C[3][1] = sp_c; C[3][2] = 1; C[1][3] = 1;
  r0[0] = r; r0[1] = r; r0[2] = (pc - pmid) + (sx_h - sx_c) * r + (sp_h - sp_c) * r; r0[3] = 0;
  for (int i = 0; i < 4; ++i) { MpInterval m = qc[i].mid(); x0[4 + i] = m; C[4 + i][0] = Dc[i][0]; C[4 + i][4 + i] = 1; r0[4 + i] = (qc[i] - m) + (Dh[i][0] - Dc[i][0]) * r; }
  DOM.reset(new capd::MpIMap(dom_vf, 2, 2, 5)); for (int i = 0; i < 5; ++i) DOM->setParameter(i, MNC[i]);
  capd::MpIMap f(mn8_vf, 8, 8, 5); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]);
  capd::MpIOdeSolver solver(f, order);
  Peek s(x0, C, r0);
  std::string reorg = std::getenv("REORG_FACTOR") ? std::getenv("REORG_FACTOR") : "default";
  if (reorg == "off") s.onoffReorganization(false); else if (reorg != "default") s.setFactor(std::stod(reorg));
  long reseedN = std::getenv("QRESEED") ? std::stol(std::getenv("QRESEED")) : 0;
  std::printf("# B17 check: W0 %s, k %.0f, reorganisation %s, Q re-seed every %ld steps, %zu checkpoints\n", argv[1], K, reorg.c_str(), reseedN, cps.size()); std::fflush(stdout);
  const char* nm[4] = {"a", "b", "E2", "eG"};
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  auto t0 = std::chrono::steady_clock::now(); long steps = 0; bool pass = true, harness_error = false;
  auto offman = [&](const IV& xy, int q) { IM Da(4, 2); IV xm(2); xm[0] = xy[0].mid(); xm[1] = xy[1].mid(); fa(xm, Da);
                                           IV n(8); n[4 + q] = 1; n[0] = -Da[q][0].mid(); n[1] = -Da[q][1].mid(); return n; };
  auto verdict = [&](const Checkpoint& c, double W1, double W2, const double Wf[5]) {
    double fake = 0; for (int q = 0; q < 5; ++q) fake += Wf[q] * c.g[2 + q];
    bool ok = (W1 / c.tu1 <= K) && (W2 / c.tu2 <= K) && (fake <= K * c.tu2 * c.g[1]);
    const double TOL = 0.02;                                  // B17a: the reference's own error (hull ~ linear to <1%)
    if (W1 / c.tu1 < 1 - TOL || W2 / c.tu2 < 1 - TOL) { harness_error = true; }
    std::printf("CHECKPOINT %-10s t=%10.4f  u1 %.3e/%.3e=%.2f  u2 %.3e/%.3e=%.2f  fake %.3e vs %.3e  nH %.2e a %.2e b %.2e E2 %.2e eG %.2e  %s\n",
                c.kind.c_str(), c.t, W1, c.tu1, W1 / c.tu1, W2, c.tu2, W2 / c.tu2, fake, K * c.tu2 * c.g[1], Wf[0], Wf[1], Wf[2], Wf[3], Wf[4],
                (W1 / c.tu1 < 0.98 || W2 / c.tu2 < 0.98) ? "HARNESS-ERROR" : (ok ? "PASS" : "FAIL"));
    std::printf("# g_phiphi certified lower bound so far: %.4e\n", S4_GMIN);
    std::fflush(stdout); if (!ok) pass = false;
  };
  try {
    for (const auto& c : cps) {
      if (c.kind == "t") {
        MpInterval T = MpInterval(c.t);
        do {
          tm(T, s); ++steps;
          if (steps % 100 == 0) { std::printf("# progress t=%.4f steps %ld S4 leaves %ld g_phiphi lower bound %.3e wall %.0f s\n", d(s.getCurrentTime().leftBound()), steps, S4_LEAVES, S4_GMIN,
                                              std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count()); std::fflush(stdout); }
          if (reseedN > 0 && steps % reseedN == 0) s.reseedQ();
          IV v = IV(s), e = s.getLastEnclosure();
          mn_domain(e);
          try { s9(e); } catch (std::exception& ex) { throw std::runtime_error(std::string("[S9] ") + ex.what()); }
          IV xy(2); xy[0] = v[0]; xy[1] = v[1]; IV fr2(4);
          try { fr2 = fa(xy); } catch (std::exception& ex) { throw std::runtime_error(std::string("[aux] ") + ex.what()); }
          for (int q = 0; q < 4; ++q) { MpInterval tmp; if (!intersection(v[4 + q], fr2[q], tmp)) throw std::runtime_error(std::string("consistency: tracked ") + nm[q] + " misses fresh enclosure (BUG)"); }
        } while (!tm.completed());
        IV v = IV(s), xy(2); xy[0] = v[0]; xy[1] = v[1];
        double Wf[5] = {w(s.along(c.nH)), 0, 0, 0, 0};
        for (int q = 0; q < 4; ++q) Wf[1 + q] = w(s.along(offman(xy, q)));
        verdict(c, w(s.along(c.u1)), w(s.along(c.u2)), Wf);
        { IV dirs[3] = {c.u1, c.u2, c.nH}; const char* dn[3] = {"u1", "u2", "nH"};
          for (int k = 0; k < 3; ++k) { MpInterval pj = s.proj(dirs[k]); char *a = nullptr, *b = nullptr;
            mpfr_asprintf(&a, "%.30Re", pj.leftBound().*RepAccess::rep); mpfr_asprintf(&b, "%.30Re", pj.rightBound().*RepAccess::rep);
            std::printf("PROJ %s t=%.10f %s [%s, %s]\n", c.kind.c_str(), c.t, dn[k], a, b); mpfr_free_str(a); mpfr_free_str(b); } }
      } else {                                                 // section checkpoint: map a COPY of the set to y = 0
        Peek sc = s;
        capd::MpICoordinateSection sec(8, 1);
        capd::MpIPoincareMap pm(solver, sec, c.kind == "sec_down" ? capd::poincare::PlusMinus : capd::poincare::MinusPlus);
        IV xc(8); for (int i = 0; i < 4; ++i) xc[i] = MpInterval(c.centre[i]);
        IV cxy(2); cxy[0] = xc[0]; cxy[1] = xc[1]; IV ac = fa(cxy); for (int q = 0; q < 4; ++q) xc[4 + q] = ac[q].mid();
        IM A(8, 8); IV rows[8] = {c.u1, c.u2, c.nH, offman(cxy, 0), offman(cxy, 1), offman(cxy, 2), offman(cxy, 3), IV(8)};
        rows[7][1] = 1;
        for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) A[i][j] = rows[i][j];
        MpInterval rt; IV img = pm(sc, xc, A, rt);
        { const char* dn[3] = {"u1", "u2", "nH"};
          for (int k = 0; k < 3; ++k) { char *a = nullptr, *b = nullptr;
            mpfr_asprintf(&a, "%.30Re", img[k].leftBound().*RepAccess::rep); mpfr_asprintf(&b, "%.30Re", img[k].rightBound().*RepAccess::rep);
            std::printf("PROJREL %s t=%.10f %s [%s, %s]\n", c.kind.c_str(), c.t, dn[k], a, b); mpfr_free_str(a); mpfr_free_str(b); } }
        double Wf[5] = {w(img[2]), w(img[3]), w(img[4]), w(img[5]), w(img[6])};
        verdict(c, w(img[0]), w(img[1]), Wf);
        std::printf("# section return-time enclosure [%.6f, %.6f]\n", d(rt.leftBound()), d(rt.rightBound()));
      }
    }
  } catch (std::exception& e) {
    std::printf("THREW at step %ld t=%.6f: %s\n", steps, d(s.getCurrentTime().leftBound()), e.what());
    pass = false;
  }
  double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  if (harness_error) std::printf("B17 HARNESS ERROR (a set narrower than its reference): not a pass or a fail\n");
  std::printf("B17 %s  W0 %s  reorganisation %s  QRESEED %ld  steps %ld  wall %.0f s  S4 certified leaves %ld\n", pass ? "PASS" : "FAIL", argv[1], reorg.c_str(), reseedN, steps, sec, S4_LEAVES);
  return 0;
}
