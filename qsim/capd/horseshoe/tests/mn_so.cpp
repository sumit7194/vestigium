// mn_so.cpp -- DIAGNOSTIC (no verdicts): the smoke box propagated as a SECOND-ORDER set (so_set.h) through the MN
// reduced flow (8-D augmented field), with
//   - the initial set = the MN lift as a second-order set (mn_lift_so, gated): x0, C0, H0 at r = 0, E0 = the cubic
//     remainder over R0 plus the radii of the point coefficients;
//   - on EVERY step: S4 (B9 predicate, B18/B18a implementation) and S9 on the step enclosure from the hull, and the
//     augmented-state consistency check on the hull;
//   - the B17 TIME checkpoints (needle frame from b17_checkpoints.py; set widths by so::Set::project; PROJ lines for the
//     containment test); SECTION checkpoints: the set is saved at t_sec - 0.5 to <state>.pre_<kind> and the checkpoint
//     is DEFERRED to a separately gated section measurement;
//   - logs every N steps: t, h, max|E|, the hull-run delta width, resteps (the Bridge's requested quantities);
//   - checkpoint/restart: the set is written (MPFR hex) every CKPT_SEC seconds and at every B17 checkpoint; a restart
//     with the same arguments resumes from it.
//   - DIAGNOSTIC options (2026-10-25, the swing-1 diagnosis; off by default, the computation is identical either way):
//     SO_DIAG_FROM=t   one DIAG line per step for t >= that time (so.h decomposition hook, logged BEFORE the S4 checks);
//     SAVE_FROM=t SAVE_DT=dt   a permanent extra copy of the set, <state>.t<time>, at every dt-grid point from t on.
// Usage: mn_so <W0 p/q> <checkpoints.txt> <state file> [T_end]
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "so_set.h"
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
using so::RepA;
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepA::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepA::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
static double w(const MpInterval& v) { return so::hi(v) - so::lo(v); }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
#include "../gen/mn_field8.h"
static MpInterval MNC[5];
void mn8_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn8_field<Node>(in, o, c); }
void aux_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]}; mn8_aux<Node>(z, o, c); }
void dom_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]}; mn8_domain<Node>(z, o, c); }
void lift_vf(Node, Node in[], int, Node o[], int, Node par[], int) {     // identical to mn_lift_so (gated)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c);
  Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1];
  Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c);
  o[0] = x; o[1] = zero; o[2] = px; o[3] = sqrt(rad); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i];
}
// ---- S4 (B9 predicate; B18/B18a: structured form, mean-value per sub-box, bisection to depth 12) and S9
static std::unique_ptr<capd::MpIMap> DOM;
static const int S4_DEPTH = 12; static long S4_LEAVES = 0; static double S4_GMIN = 1e300;
static bool certify(const MpInterval& x, const MpInterval& y, int which, int depth) {
  bool ok = false; MpInterval lowg;
  try {
    MpInterval z(0), in[8] = {x, y, z, z, z, z, z, z}, out[2];
    mn8_domain<MpInterval>(in, out, MNC);
    IV box(2), c(2); box[0] = x; box[1] = y; c[0] = x.mid(); c[1] = y.mid(); IM D(2, 2); (*DOM)(box, D); IV vc = (*DOM)(c);
    for (int i = 0; i < 2; ++i) { MpInterval mv = vc[i] + D[i][0] * (x - c[0]) + D[i][1] * (y - c[1]);
      if (!intersection(out[i], mv, out[i])) throw std::runtime_error("S4: empty intersection of two enclosures (BUG)"); }
    capd_proof::require_finite(out[which], "S4 domain function");
    ok = out[which].leftBound() > 0 && (which == 0 || out[0].leftBound() > 0); lowg = out[1];
  } catch (std::exception& e) { if (std::string(e.what()).find("BUG") != std::string::npos) throw; ok = false; }
  if (ok) { ++S4_LEAVES; if (which == 1) S4_GMIN = std::min(S4_GMIN, so::lo(lowg)); return true; }
  if (depth >= S4_DEPTH) return false;
  bool sx = w(x) >= w(y); MpInterval a = sx ? x : y, m = MpInterval(a.mid().leftBound()), lo(a.leftBound(), m.rightBound()), hi(m.leftBound(), a.rightBound());
  return sx ? (certify(lo, y, which, depth + 1) && certify(hi, y, which, depth + 1)) : (certify(x, lo, which, depth + 1) && certify(x, hi, which, depth + 1));
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
static void s9(const IV& b) { MpInterval in[4] = {b[0], b[1], b[2], b[3]}, out[1]; mn_H<MpInterval>(in, out, MNC);
  if (!out[0].contains(MpInterval(-1) / 2)) throw std::runtime_error("S9: enclosure misses H = -1/2 (BUG)"); }
// ---- checkpoint file (time checkpoints only)
struct Checkpoint { std::string kind; double t; IV u1, u2, nH; double tu1, tu2; double g[7]; double centre[4]; };
static std::vector<Checkpoint> read_cps(const char* path) {
  std::ifstream in(path); std::vector<Checkpoint> v; std::string kind;
  while (in >> kind) { Checkpoint c; c.kind = kind; in >> c.t;
    for (IV* u : {&c.u1, &c.u2, &c.nH}) { *u = IV(8); for (int i = 0; i < 8; ++i) { double x; in >> x; (*u)[i] = MpInterval(x); } }
    in >> c.tu1 >> c.tu2; for (double& g : c.g) in >> g; for (double& x : c.centre) in >> x; v.push_back(c); }
  return v;
}
// ---- state serialisation (MPFR hex, exact round trip)
static std::string hx(const MpInterval& v) { char *a = nullptr, *b = nullptr; mpfr_asprintf(&a, "%Ra", v.leftBound().*RepA::rep); mpfr_asprintf(&b, "%Ra", v.rightBound().*RepA::rep);
  std::string s = std::string(a) + " " + b; mpfr_free_str(a); mpfr_free_str(b); return s; }
static MpInterval unhx(std::istream& in) { std::string a, b; in >> a >> b; R lo, hi;
  if (mpfr_set_str(lo.*RepA::rep, a.c_str(), 0, MPFR_RNDN) || mpfr_set_str(hi.*RepA::rep, b.c_str(), 0, MPFR_RNDN)) throw std::runtime_error("state: bad hex");
  return MpInterval(lo, hi); }
static MpInterval LAST_H(0);                                     // the solver's previous step (restored on resume: determinism)
static void save(const char* path, const so::Set& X, long steps, size_t next_cp) {
  std::string tmp = std::string(path) + ".tmp"; std::ofstream o(tmp);
  o << steps << " " << next_cp << " " << hx(X.t) << " " << hx(LAST_H) << "\n";
  for (int i = 0; i < 8; ++i) o << hx(X.x[i]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) o << hx(X.C[i][a]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) o << hx(X.H[i][a][b]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) o << hx(X.B[i][j]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) o << hx(X.re[i]) << " "; o << "\nEND\n"; o.close();
  std::rename(tmp.c_str(), path);                                    // atomic replace
}
static bool load(const char* path, so::Set& X, long& steps, size_t& next_cp) {
  std::ifstream in(path); if (!in) return false;
  in >> steps >> next_cp; X.t = unhx(in); LAST_H = unhx(in);
  for (int i = 0; i < 8; ++i) X.x[i] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) X.C[i][a] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) X.H[i][a][b] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) X.B[i][j] = unhx(in);
  for (int i = 0; i < 8; ++i) X.re[i] = unhx(in);
  std::string end; in >> end; if (end != "END") throw std::runtime_error("state: truncated file");
  return true;
}

int main(int argc, char** argv) {
  if (argc < 4) { std::cerr << "usage: mn_so W0 checkpoints.txt statefile [T_end]\n"; return 2; }
  R::setDefaultPrecision(128);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  DOM.reset(new capd::MpIMap(dom_vf, 2, 2, 5)); for (int i = 0; i < 5; ++i) DOM->setParameter(i, MNC[i]);
  capd::MpIMap fa(aux_vf, 2, 4, 5); for (int i = 0; i < 5; ++i) fa.setParameter(i, MNC[i]);
  auto cps = read_cps(argv[2]); double Tend = argc > 4 ? std::stod(argv[4]) : 1e300;
  const double K = 5.0; const long LOG_EVERY = std::getenv("LOG_EVERY") ? std::atol(std::getenv("LOG_EVERY")) : 20;
  const double CKPT_SEC = std::getenv("CKPT_SEC") ? std::atof(std::getenv("CKPT_SEC")) : 1800;
  so::Set X(8); long steps = 0; size_t next_cp = 0;
  if (load(argv[3], X, steps, next_cp)) std::printf("# RESUMED from %s at t=%.10f steps %ld next checkpoint %zu\n", argv[3], so::md(X.t), steps, next_cp);
  else {                                                           // the lift as a second-order set
    capd::MpIMap L(lift_vf, 2, 8, 8, 3); for (int i = 0; i < 5; ++i) L.setParameter(i, MNC[i]);
    L.setParameter(5, Q("36419361737/10000000000")); L.setParameter(6, Q("60360992808/10000000000")); L.setParameter(7, Q(argv[1]));
    IV r0(2), R0(2); R0[0] = MpInterval(-1, 1); R0[1] = MpInterval(-1, 1);
    capd::diffAlgebra::Jet<IM, 0> j0(8, 2, 3), jR(8, 2, 3); L(r0, j0); L(R0, jR);
    for (int i = 0; i < 8; ++i) {
      MpInterval box(0);
      X.x[i] = j0(i).mid(); box += j0(i) - X.x[i];
      for (int a = 0; a < 2; ++a) { X.C[i][a] = j0(i, a).mid(); box += (j0(i, a) - X.C[i][a]) * so::sym(1); }
      for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) { int lo = std::min(a, b), hi = std::max(a, b); MpInterval cf = lo == hi ? j0(i, lo, hi) * 2 : j0(i, lo, hi);
        X.H[i][a][b] = cf.mid(); box += (cf - X.H[i][a][b]) * so::Set::rr(a, b) / 2; }
      MpInterval r1 = R0[0], r2 = R0[1];
      box += jR(i, 0, 0, 0) * power(r1, 3) + jR(i, 0, 0, 1) * sqr(r1) * r2 + jR(i, 0, 1, 1) * r1 * sqr(r2) + jR(i, 1, 1, 1) * power(r2, 3);
      X.re[i] = box;
    }
    X.B.setToIdentity(); X.t = MpInterval(0);
  }
  std::printf("# mn_so: W0 %s, %zu checkpoints (time ones measured; sections SKIPPED), T_end %g\n", argv[1], cps.size(), Tend); std::fflush(stdout);
  capd::MpIMap fK(mn8_vf, 8, 8, 5, 2), fT(mn8_vf, 8, 8, 5, 2);
  for (int i = 0; i < 5; ++i) { fK.setParameter(i, MNC[i]); fT.setParameter(i, MNC[i]); }
  so::Solver solK(fK, 20), solT(fT, 20);
  if (so::md(LAST_H) > 0) solK.adjustTimeStep(LAST_H);          // resume: same step-control history as an uninterrupted run
  const char* nm[4] = {"a", "b", "E2", "eG"};
  auto t0 = std::chrono::steady_clock::now(); auto lastck = t0; bool pass = true;
  auto offman = [&](const IV& xy, int q) { IM Da(4, 2); IV xm(2); xm[0] = xy[0].mid(); xm[1] = xy[1].mid(); fa(xm, Da);
                                           IV n(8); n[4 + q] = 1; n[0] = -Da[q][0].mid(); n[1] = -Da[q][1].mid(); return n; };
  static so::StepDiag DG; const double DIAG_FROM = std::getenv("SO_DIAG_FROM") ? std::atof(std::getenv("SO_DIAG_FROM")) : 1e300;
  const double SAVE_FROM = std::getenv("SAVE_FROM") ? std::atof(std::getenv("SAVE_FROM")) : 1e300, SAVE_DT = std::getenv("SAVE_DT") ? std::atof(std::getenv("SAVE_DT")) : 0.25;
  long save_k = -1;
  try {
    while (so::md(X.t) < Tend) {
      // section checkpoints: integrate to t_sec - PRE, save the set to <state>.pre_<kind> for the (separately gated) section
      // measurement, and continue; the checkpoint is logged as DEFERRED until that measurement is run
      const double PRE = 0.5;
      double tnext = std::min(next_cp < cps.size() ? (cps[next_cp].kind == "t" ? cps[next_cp].t : cps[next_cp].t - PRE) : Tend, Tend);
      double rem = tnext - so::md(X.t);
      solK.setMaxStep(MpInterval(rem > 0 ? rem : 1e-300));
      so::SO_DIAG = so::md(X.t) >= DIAG_FROM ? &DG : nullptr;
      so::StepLog lg = so::step(solK, solT, X, true); ++steps; LAST_H = solK.getStep();
      if (so::SO_DIAG) { IV hl = X.hull(); double hx = w(hl[0]), hy = w(hl[1]), ex = w(lg.enc[0]), ey = w(lg.enc[1]);
        std::printf("DIAG step %ld t=%.6f h=%.3e maxE %.3e lohner %.3e box0 %.3e box1 %.3e box2 %.3e dDe %.3e remT0 %.3e remT1 %.3e encK %.3e Kw %.3e condB %.3e hull_xy %.3e %.3e enc_xy %.3e %.3e\n",
                    steps, so::md(X.t), lg.h, lg.maxE, DG.lohner, DG.box0, DG.box1, DG.box2, DG.dDe, DG.remT0, DG.remT1, DG.encK, DG.Kw, DG.condB, hx, hy, ex, ey); std::fflush(stdout); }
      if (so::md(X.t) >= SAVE_FROM) { long k = (long)std::floor((so::md(X.t) - SAVE_FROM) / SAVE_DT);
        if (k > save_k) { save_k = k; char nmb[64]; std::snprintf(nmb, sizeof nmb, ".t%.4f", so::md(X.t)); std::string sp = std::string(argv[3]) + nmb;
          save(sp.c_str(), X, steps, next_cp); std::printf("SAVED %s\n", sp.c_str()); std::fflush(stdout); } }
      mn_domain(lg.enc); s9(lg.enc);                               // S4 and S9 on the step enclosure from the hull
      IV hull = X.hull(); mn_domain(hull); s9(hull);
      IV xy(2); xy[0] = hull[0]; xy[1] = hull[1]; IV fr = fa(xy);
      for (int q = 0; q < 4; ++q) { MpInterval tmp; if (!intersection(hull[4 + q], fr[q], tmp)) throw std::runtime_error(std::string("consistency: tracked ") + nm[q] + " misses fresh enclosure (BUG)"); }
      double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
      if (steps % LOG_EVERY == 0)
        std::printf("# step %ld t=%.6f h=%.3e maxE %.3e hullDelta %.3e resteps %ld S4leaves %ld gphiphi_lb %.3e wall %.0f s\n",
                    steps, so::md(X.t), lg.h, lg.maxE, lg.w_D2K_contrib, so::SO_RESTEPS, S4_LEAVES, S4_GMIN, el);
      if (next_cp < cps.size() && cps[next_cp].kind != "t" && std::fabs(so::md(X.t) - (cps[next_cp].t - PRE)) < 1e-9) {
        std::string pre = std::string(argv[3]) + ".pre_" + cps[next_cp].kind; save(pre.c_str(), X, steps, next_cp + 1);
        std::printf("CHECKPOINT %s t=%.4f DEFERRED (set saved at t=%.6f to %s for the section measurement)\n", cps[next_cp].kind.c_str(), cps[next_cp].t, so::md(X.t), pre.c_str());
        ++next_cp; save(argv[3], X, steps, next_cp); lastck = std::chrono::steady_clock::now(); std::fflush(stdout); continue;
      }
      if (next_cp < cps.size() && std::fabs(so::md(X.t) - cps[next_cp].t) < 1e-9) {   // a time checkpoint reached
        const Checkpoint& c = cps[next_cp];
        double W1 = w(X.project(c.u1)), W2 = w(X.project(c.u2)), Wf[5] = {w(X.project(c.nH)), 0, 0, 0, 0};
        for (int q = 0; q < 4; ++q) Wf[1 + q] = w(X.project(offman(xy, q)));
        double fake = 0; for (int q = 0; q < 5; ++q) fake += Wf[q] * c.g[2 + q];
        bool ok = (W1 / c.tu1 <= K) && (W2 / c.tu2 <= K) && (fake <= K * c.tu2 * c.g[1]);
        bool harness = (W1 / c.tu1 < 0.98 || W2 / c.tu2 < 0.98);
        { IV dirs[3] = {c.u1, c.u2, c.nH}; const char* dn[3] = {"u1", "u2", "nH"};
          for (int k = 0; k < 3; ++k) { MpInterval pj = X.project(dirs[k]); char *a = nullptr, *b = nullptr;
            mpfr_asprintf(&a, "%.60RDe", pj.leftBound().*RepA::rep); mpfr_asprintf(&b, "%.60RUe", pj.rightBound().*RepA::rep);
            std::printf("PROJ t t=%.10f %s [%s, %s]\n", c.t, dn[k], a, b); mpfr_free_str(a); mpfr_free_str(b); } }
        std::printf("CHECKPOINT t t=%10.4f u1 %.3e/%.3e=%.2f u2 %.3e/%.3e=%.2f fake %.3e vs %.3e nH %.2e  %s\n", c.t, W1, c.tu1, W1 / c.tu1, W2, c.tu2, W2 / c.tu2,
                    fake, K * c.tu2 * c.g[1], Wf[0], harness ? "HARNESS-ERROR" : (ok ? "PASS" : "FAIL"));
        if (!ok) pass = false; ++next_cp; save(argv[3], X, steps, next_cp); lastck = std::chrono::steady_clock::now();
      }
      if (std::chrono::duration<double>(std::chrono::steady_clock::now() - lastck).count() > CKPT_SEC) { save(argv[3], X, steps, next_cp); lastck = std::chrono::steady_clock::now(); }
      std::fflush(stdout);
      if (next_cp >= cps.size() && so::md(X.t) >= tnext - 1e-12) break;
    }
  } catch (std::exception& e) { std::printf("THREW at step %ld t=%.6f: %s\n", steps, so::md(X.t), e.what()); pass = false; }
  save(argv[3], X, steps, next_cp);
  std::printf("MN-SO %s (time checkpoints only; informational) W0 %s steps %ld resteps %ld wall %.0f s\n", pass ? "PASS" : "FAIL", argv[1], steps, so::SO_RESTEPS,
              std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
}
