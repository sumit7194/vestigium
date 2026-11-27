// s2_main.cpp -- MN homoclinic spike S2, rigorous stages (PREREG.md A1-A11). MPFR intervals only, under proof_guard.h
// (guard_build.sh). Written by Claude Opus 5.5 (Quantum), 2026-11-27.
//
// Field: gen/mn_field.h (the B10-regularised MN/Kerr reduced field, mn_codegen.py; G-norm-checked in S1), or with
// -DSABFIELD the control-(iii) field gen_sab/mn_field.h (the same generator with the 3 beta^2 (P3^2 - P2^2)/R^6 term of
// G dropped). (M, a) = (5, 3): k = 4, alpha = -1/3; E, L the decimal strings of the registration, as exact rationals.
// Section Sigma = {y = 0}, section coordinates w = (x, p_x), p_y lifted by the positive root of H = -1/2.
// A node's map is "the first upward crossing of Sigma after t = Tstop": C^1 (or C^0) time map step by step to Tstop
// (every step enclosure: S4 domain checks), y(Tstop) < 0 certified (fail closed), then the CAPD Poincare map
// (MinusPlus), then a C^0 replay of [Tstop, rt] with the same domain checks. Step tolerance 1e-24 (A11), order 20.
// All decisions are interval inequalities evaluated here. The spec file (key value lines) is written by s2run.py; its
// decimals are read as exact rationals and enclosed outward. No watchdog, no caps (no-hard-caps rule).
//
// Modes (argv[1]) and spec keys:
//   fp    : Krawczyk for F(w) = P(w) - w.   keys: beta Tstop w(2) A(2x2) rmin [pointonly]
//   cone  : the A11 lemma.   keys: beta Tstop c(2) rho T(2x2 columns u~, s~) delta
//   bvp   : R-symmetric half BVP (A1).   keys: beta c(2) T(2x2) L rhop deltastar m ubar z(m-1 x 2) tstop(m) A rmin [pointonly]
//           X = (u, z_1..z_{m-1}); F_1 = P(w_u(u)) - z_1, F_i = P(z_{i-1}) - z_i, F_m = p_x(P(z_{m-1}));
//           w_u(u) = c + u u~ + h(u) s~, h(u) in [-eta, eta], eta = rhop + L (|u| + rhop), h'(u) in [-L, L] (A11 lemma).
//   meet  : control (ii) at beta = 0.   keys: beta c T L rhop deltastar m c0 cprime xmid xrad z(m-1) zp(m-1) g(2)
//           tstop(m) tstopp(m) A rmin [pointonly];  X = (c, z_1..z_{m-1}, z'_1..z'_{m-1}, c', alpha) with the phase
//           condition x(z_{m-1}) = xh, xh in [xmid +- xrad] (uniform contraction over xh); plus the K_r lemma check.
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <gmp.h>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include "proof_guard.h"

using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;
typedef capd::MpIVector IV;
typedef capd::MpIMatrix IM;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s0) {
  std::string s = s0; bool neg = false;
  if (!s.empty() && (s[0] == '-' || s[0] == '+')) { neg = s[0] == '-'; s = s.substr(1); }
  size_t e = s.find_first_of("eE"); long ex = 0;
  if (e != std::string::npos) { ex = std::stol(s.substr(e + 1)); s = s.substr(0, e); }
  size_t dot = s.find('.'); std::string num, den = "1";
  if (s.find('/') != std::string::npos) { num = s; den = ""; }
  else if (dot != std::string::npos) { num = s.substr(0, dot) + s.substr(dot + 1); den = "1" + std::string(s.size() - dot - 1, '0'); }
  else num = s;
  if (ex > 0 && den != "") num += std::string(ex, '0'); else if (ex < 0 && den != "") den += std::string(-ex, '0');
  std::string qs = den == "" ? num : num + "/" + den; if (neg) qs = "-" + qs;
  mpq_t q; mpq_init(q);
  if (mpq_set_str(q, qs.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s0);
  mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q);
  return MpInterval(lo, hi);
}
static std::string bnd(const R& r, bool up) { char* s = nullptr; mpfr_asprintf(&s, up ? "%.24RUe" : "%.24RDe", r.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o; }
static std::string iv(const MpInterval& x) { return "[" + bnd(x.leftBound(), false) + "," + bnd(x.rightBound(), true) + "]"; }
static std::string mid40(const MpInterval& x) { R m = x.mid().leftBound(); char* s = nullptr; mpfr_asprintf(&s, "%.40Re", m.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o; }
static double dbl(const R& r) { return mpfr_get_d(r.*RepAccess::rep, MPFR_RNDN); }
static MpInterval mag(const MpInterval& a) { R l = a.leftBound(), h = a.rightBound(); if (l < 0) l = -l; if (h < 0) h = -h; return MpInterval(l > h ? l : h); }
static MpInterval sym(const MpInterval& r) { return MpInterval(-r.rightBound(), r.rightBound()); }

inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#ifdef SABFIELD
#include "gen_sab/mn_field.h"
static const char* FIELD = "SABOTAGED(drop 3beta^2 G term)";
#else
#include "gen/mn_field.h"
static const char* FIELD = "true";
#endif
static MpInterval MNC[5];
void mn_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn_field<Node>(in, o, c); }
static MpInterval mn_Hi(const IV& x) { MpInterval in[4] = {x[0], x[1], x[2], x[3]}, out[1]; mn_H<MpInterval>(in, out, MNC); return out[0]; }
static void mn_domain(const IV& b) {
  capd_proof::require_finite_all(b, "S4 enclosure");
  const MpInterval &x = b[0], &y = b[1];
  if (!((x - 1).leftBound() >= MpInterval(1) / 20)) throw std::runtime_error("S4: x - 1 < 0.05 possible");
  if (!((x * x + y * y - 1).leftBound() >= MpInterval(1) / 4)) throw std::runtime_error("S4: R^2 < 0.25 possible");
  if (!((1 - y * y).leftBound() > 0)) throw std::runtime_error("S4: 1 - y^2 > 0 not certified");
  MpInterval in[2] = {x, y}, out[1];
  mn_B<MpInterval>(in, out, MNC); capd_proof::require_finite(out[0], "S4 B");
  if (!(out[0].leftBound() > 0)) throw std::runtime_error("S4: B > 0 not certified");
  MpInterval d = MpInterval(1) / 40, xi[2] = {x + sym(d), y + sym(d)};
  mn_gpp<MpInterval>(xi, out, MNC); capd_proof::require_finite(out[0], "S4 g_phiphi");
  if (!(out[0].leftBound() > 0)) throw std::runtime_error("S4: g_phiphi > 0 on the inflated box not certified");
}
// ---- Tier-1 dump (A13): exact MPFR hex endpoints of every CAPD enclosure that enters a decision
static FILE* DUMPF = nullptr;
static std::string hx(const R& r) { char* c = nullptr; mpfr_asprintf(&c, "%Ra", r.*RepAccess::rep); std::string o(c); mpfr_free_str(c); return o; }
static void dI(const std::string& tag, const std::string& nm, int i, int j, const MpInterval& x) {
  if (DUMPF) std::fprintf(DUMPF, "%s %s %d %d %s %s\n", tag.c_str(), nm.c_str(), i, j, hx(x.leftBound()).c_str(), hx(x.rightBound()).c_str()); }
static int ORDER = 20; static double TOL = 1e-24;
static void settol(capd::MpIOdeSolver& s) { s.setAbsoluteTolerance(TOL); s.setRelativeTolerance(TOL); }   // step control only
static double T0;
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }

struct Pass { IV P; IM D; MpInterval rt; long steps; };
// one node map on the box (x, px) (a point if the intervals are thin); c1 = also the 2x2 section derivative
static Pass pass(capd::MpIMap& f, const MpInterval& x, const MpInterval& px, double Tstop, bool c1, const std::string& tag) {
  double t0 = now();
  MpInterval lin[2] = {x, MpInterval(0)}, lo[3]; mn_lift<MpInterval>(lin, lo, MNC);
  MpInterval rad = (MpInterval(-1) - lo[0] * px * px - 2 * lo[2]) / lo[1];
  if (!(rad.leftBound() > 0)) throw std::runtime_error(tag + ": lift radicand > 0 not certified");
  IV X0(4); X0[0] = x; X0[1] = MpInterval(0); X0[2] = px; X0[3] = sqrt(rad);
  capd::MpIOdeSolver solver(f, ORDER); settol(solver); capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  capd::MpICoordinateSection section(4, 1); capd::MpIPoincareMap pm(solver, section, capd::poincare::MinusPlus);
  long steps = 0; MpInterval T(Tstop); Pass out; out.D = IM(2, 2);
  IV cS(4); double tS;
  if (c1) {
    IV c(4); for (int i = 0; i < 4; ++i) c[i] = MpInterval(X0[i].mid().leftBound());
    capd::MpC1Rect2Set s(c, IV(X0 - c));
    do { tm(T, s); mn_domain(s.getLastEnclosure()); ++steps; } while (!tm.completed());
    cS = (IV)s; tS = dbl(s.getCurrentTime().leftBound());
    if (!(cS[1].rightBound() < 0)) throw std::runtime_error(tag + ": y(Tstop) < 0 not certified (crossing rule)");
    IM D(4, 4); out.P = pm(s, D, out.rt);
    capd_proof::require_finite_all(out.P, (tag + " return").c_str()); capd_proof::require_finite(out.rt, (tag + " rt").c_str());
    capd_proof::require_finite_all(D, (tag + " DPhi").c_str());
    IM DP = pm.computeDP(out.P, D, out.rt);
    capd_proof::require_finite_all(DP, (tag + " DP").c_str());
    MpInterval fin[4] = {X0[0], X0[1], X0[2], X0[3]}, fo[4]; mn_field<MpInterval>(fin, fo, MNC);
    if (!(fo[1].leftBound() > 0)) throw std::runtime_error(tag + ": ydot > 0 not certified at the start");
    IM C(4, 2); C[0][0] = 1; C[2][1] = 1; C[3][0] = fo[2] / fo[1]; C[3][1] = -fo[0] / fo[1];
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) { int ri = i == 0 ? 0 : 2; MpInterval acc(0); for (int k = 0; k < 4; ++k) acc += DP[ri][k] * C[k][j]; out.D[i][j] = acc; }
    capd_proof::require_finite_all(out.D, (tag + " DPsec").c_str());
  } else {
    capd::MpC0TripletonSet s(X0);
    do { tm(T, s); mn_domain(s.getLastEnclosure()); ++steps; } while (!tm.completed());
    cS = (IV)s; tS = dbl(s.getCurrentTime().leftBound());
    if (!(cS[1].rightBound() < 0)) throw std::runtime_error(tag + ": y(Tstop) < 0 not certified (crossing rule)");
    out.P = pm(s, out.rt);
    capd_proof::require_finite_all(out.P, (tag + " return").c_str()); capd_proof::require_finite(out.rt, (tag + " rt").c_str());
  }
  if (!mn_Hi(out.P).contains(MpInterval(-1) / 2)) throw std::runtime_error(tag + ": return misses H = -1/2 (BUG)");
  { capd::MpIOdeSolver rs(f, ORDER); settol(rs); capd::MpITimeMap rtm(rs); rtm.stopAfterStep(true);
    capd::MpC0TripletonSet s0(cS, MpInterval(tS)); MpInterval T2(out.rt.rightBound());
    do { rtm(T2, s0); mn_domain(s0.getLastEnclosure()); ++steps; } while (!rtm.completed()); }
  out.steps = steps;
  if (DUMPF) { for (int i = 0; i < 4; ++i) dI(tag, "X0", i, 0, X0[i]); dI(tag, "P", 0, 0, out.P[0]); dI(tag, "P", 1, 0, out.P[2]); dI(tag, "rt", 0, 0, out.rt);
               if (c1) for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) dI(tag, "D", i, j, out.D[i][j]); std::fflush(DUMPF); }
  std::printf("PASS %s %s steps %ld wall %.1f s (total %.1f s)\n", tag.c_str(), c1 ? "C1" : "C0", steps, now() - t0, now() - T0); std::fflush(stdout);
  return out;
}

// ---------------- spec
struct Spec { std::map<std::string, std::vector<std::string>> kv; bool has(const std::string& k) const { return kv.count(k); }
  const std::vector<std::string>& v(const std::string& k) const { auto it = kv.find(k); if (it == kv.end()) throw std::runtime_error("spec: missing " + k); return it->second; }
  MpInterval q(const std::string& k, size_t i = 0) const { return Q(v(k).at(i)); }
  double d(const std::string& k) const { return std::stod(v(k).at(0)); }
  int n(const std::string& k) const { return std::stoi(v(k).at(0)); } };
static Spec readspec(const char* fn) {
  Spec S; std::ifstream in(fn); if (!in) throw std::runtime_error("cannot open spec"); std::string line;
  while (std::getline(in, line)) { if (line.empty() || line[0] == '#') continue; std::istringstream ss(line); std::string k, t; ss >> k; std::vector<std::string> vals; while (ss >> t) vals.push_back(t); S.kv[k] = vals; }
  return S;
}
static IM readmat(const Spec& S, const std::string& k, int n, int m) { const auto& v = S.v(k); if ((int)v.size() != n * m) throw std::runtime_error("spec: " + k + " size"); IM A(n, m); for (int i = 0; i < n; ++i) for (int j = 0; j < m; ++j) A[i][j] = Q(v[i * m + j]); return A; }
static MpInterval normInf(const IM& A) { MpInterval best(0); for (int i = 0; i < (int)A.numberOfRows(); ++i) { MpInterval s(0); for (int j = 0; j < (int)A.numberOfColumns(); ++j) s += mag(A[i][j]); if (s.rightBound() > best.rightBound()) best = MpInterval(s.rightBound()); } return best; }
static MpInterval normInfV(const IV& v) { MpInterval b(0); for (int i = 0; i < (int)v.dimension(); ++i) { MpInterval m = mag(v[i]); if (m.rightBound() > b.rightBound()) b = MpInterval(m.rightBound()); } return b; }
static IM inv2(const IM& T) { MpInterval det = T[0][0] * T[1][1] - T[0][1] * T[1][0]; if (det.contains(MpInterval(0))) throw std::runtime_error("frame singular");
  IM Ti(2, 2); Ti[0][0] = T[1][1] / det; Ti[0][1] = -T[0][1] / det; Ti[1][0] = -T[1][0] / det; Ti[1][1] = T[0][0] / det; return Ti; }
static void printv(const std::string& tag, const IV& v) { for (int i = 0; i < (int)v.dimension(); ++i) std::printf("%s[%d] %s mid %s\n", tag.c_str(), i, iv(v[i]).c_str(), mid40(v[i]).c_str()); }
static void printm(const std::string& tag, const IM& M) { for (int i = 0; i < (int)M.numberOfRows(); ++i) for (int j = 0; j < (int)M.numberOfColumns(); ++j) std::printf("%s[%d][%d] %s mid %s\n", tag.c_str(), i, j, iv(M[i][j]).c_str(), mid40(M[i][j]).c_str()); }

static bool krawczyk(const MpInterval& Y, const MpInterval& Z, const R& r) {
  MpInterval rr(r), v = Z * rr - rr + Y;
  std::printf("KRAWCZYK Y %s Z %s r %s  Zr - r + Y <= %s\n", bnd(Y.rightBound(), true).c_str(), bnd(Z.rightBound(), true).c_str(), bnd(r, true).c_str(), bnd(v.rightBound(), true).c_str());
  return capd_proof::certainly_less(Z, MpInterval(1)) && capd_proof::certainly_negative(v);   // trust rule: finite-checked decisions
}
static R pickr(const MpInterval& Yest, const Spec& S) { R r = (Yest * 4).rightBound(); R rmin = S.q("rmin").rightBound(); return r < rmin ? rmin : r; }

// ---------------- fp
static int run_fp(capd::MpIMap& f, const Spec& S) {
  double Ts = S.d("Tstop"); MpInterval w0 = S.q("w", 0), w1 = S.q("w", 1); IM A = readmat(S, "A", 2, 2);
  Pass p = pass(f, w0, w1, Ts, false, "fp_point");
  IV F(2); F[0] = p.P[0] - w0; F[1] = p.P[2] - w1; printv("F", F);
  if (S.has("pointonly")) return 0;
  MpInterval Yest = normInfV(A * F); R r = pickr(Yest, S);
  dI("fp", "r", 0, 0, MpInterval(r));
  Pass b = pass(f, w0 + sym(MpInterval(r)), w1 + sym(MpInterval(r)), Ts, true, "fp_ball");
  IM I2(2, 2); I2[0][0] = 1; I2[1][1] = 1;
  MpInterval Y = normInfV(A * F), Z = normInf(I2 - A * (b.D - I2));
  bool ok = krawczyk(Y, Z, r);
  printm("DPfp", b.D);
  std::printf("RESULT fp %s rho %s\n", ok ? "CERTIFIED" : "FAIL", bnd(r, true).c_str());
  return ok ? 0 : 3;
}

// ---------------- cone (A11 lemma)
static int run_cone(capd::MpIMap& f, const Spec& S) {
  double Ts = S.d("Tstop"); MpInterval c0 = S.q("c", 0), c1 = S.q("c", 1), rho = S.q("rho"), delta = S.q("delta");
  IM T = readmat(S, "T", 2, 2), Ti = inv2(T);
  IV hb(2); hb[0] = c0 + sym((mag(T[0][0]) + mag(T[0][1])) * delta); hb[1] = c1 + sym((mag(T[1][0]) + mag(T[1][1])) * delta);
  Pass b = pass(f, hb[0], hb[1], Ts, true, "cone_box");
  IM Mm = Ti * b.D * T;      // [M] contains Ti DP(xi) T for all xi in B (B inside the hull box hb)
  printm("M", Mm); capd_proof::require_finite_all(Mm, "cone M");
  MpInterval a = Mm[0][0], bb = mag(Mm[0][1]), cc = mag(Mm[1][0]), dd = mag(Mm[1][1]);
  if (!capd_proof::certainly_less(MpInterval(1), a)) { std::printf("RESULT cone FAIL a_min <= 1\n"); return 3; }
  MpInterval rhop = normInf(Ti) * rho;   // the fixed point in eigen-coordinates: |(u*, s*)| <= ||Ti||_inf rho
  // pick L: smallest of the trial values for which (H1),(H2) hold
  for (int k = 0; k < 40; ++k) {
    MpInterval L = (cc.rightBound() == 0 ? Q("1/1000000000000") : cc * 2 / (MpInterval(a.leftBound()) - 2)) * MpInterval(1 << (k % 20)) * (k >= 20 ? MpInterval(1048576) : MpInterval(1));
    MpInterval mu = MpInterval(a.leftBound()) - bb * L, nu = cc / L + dd;
    bool h1 = capd_proof::certainly_less(MpInterval(1), mu) && capd_proof::certainly_negative(cc + dd * L - L * mu), h2 = capd_proof::certainly_less(nu, MpInterval(1));
    if (h1 && h2) {
      MpInterval kappa = mag(a) + bb * L, mx = L.rightBound() > 1 ? L : MpInterval(1);
      MpInterval dstar = (delta - rhop) / (kappa * mx);
      std::printf("CONE L %s mu >= %s nu <= %s kappa <= %s rhop <= %s deltastar >= %s\n", bnd(L.rightBound(), true).c_str(), bnd(mu.leftBound(), false).c_str(),
                  bnd(nu.rightBound(), true).c_str(), bnd(kappa.rightBound(), true).c_str(), bnd(rhop.rightBound(), true).c_str(), bnd(dstar.leftBound(), false).c_str());
      std::printf("RESULT cone CERTIFIED L %s rhop %s deltastar %s\n", bnd(L.rightBound(), true).c_str(), bnd(rhop.rightBound(), true).c_str(), bnd(dstar.leftBound(), false).c_str());
      return 0;
    }
  }
  std::printf("RESULT cone FAIL (no L in the trial ladder satisfies H1 and H2)\n"); return 3;
}

// ---------------- shared: the W^u endpoint
struct Frame { IV c; IM T; MpInterval L, rhop, dstar; };
static Frame readframe(const Spec& S) { Frame F; F.c = IV(2); F.c[0] = S.q("c", 0); F.c[1] = S.q("c", 1); F.T = readmat(S, "T", 2, 2); F.L = S.q("L"); F.rhop = S.q("rhop"); F.dstar = S.q("deltastar"); return F; }
static IV ut(const Frame& F) { IV u(2); u[0] = F.T[0][0]; u[1] = F.T[1][0]; return u; }
static IV st(const Frame& F) { IV s(2); s[0] = F.T[0][1]; s[1] = F.T[1][1]; return s; }
static MpInterval etarad(const Frame& F, const MpInterval& u) { return F.rhop + F.L * (mag(u) + F.rhop); }
static void checkreach(const Frame& F, const MpInterval& u, const R& r, const std::string& tag) {
  MpInterval need = mag(u) + MpInterval(r) + F.rhop;
  if (!(need.rightBound() <= F.dstar.leftBound())) throw std::runtime_error(tag + ": |u - u*| + r exceeds deltastar (lemma reach)");
}

// ---------------- bvp
static int run_bvp(capd::MpIMap& f, const Spec& S) {
  Frame Fr = readframe(S); int m = S.n("m"); int D = 2 * m - 1;
  MpInterval ub = S.q("ubar"); std::vector<IV> z(m);       // z[1..m-1]
  for (int i = 1; i < m; ++i) { z[i] = IV(2); z[i][0] = S.q("z", 2 * (i - 1)); z[i][1] = S.q("z", 2 * (i - 1) + 1); }
  std::vector<double> ts(m); for (int i = 0; i < m; ++i) ts[i] = std::stod(S.v("tstop").at(i));
  IV U = ut(Fr), Sv = st(Fr);
  IV w0 = Fr.c + U * ub;                                       // eta_mid = 0
  std::vector<Pass> pt(m);
  pt[0] = pass(f, w0[0], w0[1], ts[0], false, "bvp_pt0");
  for (int i = 1; i < m; ++i) pt[i] = pass(f, z[i][0], z[i][1], ts[i], false, "bvp_pt" + std::to_string(i));
  IV F(D);                                                     // without the eta term (added after the ball pass)
  for (int i = 0; i < m - 1; ++i) { F[2 * i] = pt[i].P[0] - z[i + 1][0]; F[2 * i + 1] = pt[i].P[2] - z[i + 1][1]; }
  F[D - 1] = pt[m - 1].P[2];
  printv("F", F);
  if (S.has("pointonly")) return 0;
  IM A = readmat(S, "A", D, D);
  MpInterval eta = etarad(Fr, ub);
  IV Fe = F; Fe[0] += sym(eta / 10); Fe[1] += sym(eta / 10);       // r choice only: |DP s~| <= ~0.04 near fp
  R r = pickr(normInfV(A * Fe), S);
  checkreach(Fr, ub, r, "bvp");
  std::printf("BALL r %s eta %s\n", bnd(r, true).c_str(), bnd(eta.rightBound(), true).c_str()); dI("bvp", "r", 0, 0, MpInterval(r));
  std::vector<Pass> bl(m);
  { MpInterval uu = ub + sym(MpInterval(r)), ee = sym(etarad(Fr, uu) + Fr.L * MpInterval(r));
    IV W = Fr.c + U * uu + Sv * ee; bl[0] = pass(f, W[0], W[1], ts[0], true, "bvp_ball0"); }
  for (int i = 1; i < m; ++i) bl[i] = pass(f, z[i][0] + sym(MpInterval(r)), z[i][1] + sym(MpInterval(r)), ts[i], true, "bvp_ball" + std::to_string(i));
  // F(x-bar) with the mean-value eta term: P(w_u(ubar)) in P(w0) + DP([W]) (h(ubar) s~), h(ubar) in [-eta, eta]
  IV corr = (bl[0].D * Sv) * sym(eta); F[0] += corr[0]; F[1] += corr[1];     // thin DP s~ first (no wrapping), then the eta factor
  // DF over the ball
  IM DF(D, D);
  IV c0 = bl[0].D * U + (bl[0].D * Sv) * sym(Fr.L); DF[0][0] = c0[0]; DF[1][0] = c0[1];
  for (int i = 0; i < m - 1; ++i) { int col = 1 + 2 * i; DF[2 * i][col] = -1; DF[2 * i + 1][col + 1] = -1;
    if (2 * i + 2 < D - 1) { for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) DF[2 * i + 2 + a][col + b] = bl[i + 1].D[a][b]; }
    else { DF[D - 1][col] = bl[i + 1].D[1][0]; DF[D - 1][col + 1] = bl[i + 1].D[1][1]; } }
  IM ID(D, D); for (int i = 0; i < D; ++i) ID[i][i] = 1;
  MpInterval Y = normInfV(A * F), Z = normInf(ID - A * DF);
  bool ok = krawczyk(Y, Z, r);
  // tangent of W^u at the symmetric point p, over the ball: v = DP_{m-1} ... DP_0 (u~ + [-L, L] s~)
  IV vU = U, vS = Sv; for (int i = 0; i < m; ++i) { vU = bl[i].D * vU; vS = bl[i].D * vS; }   // two thin chains
  IV v = vU + vS * sym(Fr.L);
  // the symmetric point p = P(z_{m-1}) over the ball (mean value)
  IV dz(2); dz[0] = sym(MpInterval(r)); dz[1] = sym(MpInterval(r)); IV pe = bl[m - 1].D * dz; IV p(2); p[0] = pt[m - 1].P[0] + pe[0]; p[1] = pt[m - 1].P[2] + pe[1];
  printv("p", p); printv("v", v);
  bool vx0 = !capd_proof::certainly_disjoint(v[0], MpInterval(0)), vp0 = !capd_proof::certainly_disjoint(v[1], MpInterval(0));   // finite-checked
  std::printf("SIGNTEST v_x %s 0 ; v_px %s 0\n", vx0 ? "CONTAINS" : "EXCLUDES", vp0 ? "CONTAINS" : "EXCLUDES");
  std::printf("RESULT bvp krawczyk %s v_x %s v_px %s\n", ok ? "CERTIFIED" : "FAIL", vx0 ? "contains0" : "excludes0", vp0 ? "contains0" : "excludes0");
  return ok ? 0 : 3;
}

// ---------------- meet (control ii, beta = 0)
static MpInterval Kr_dx(const MpInterval& x, const MpInterval& px, const MpInterval& E, const MpInterval& L);
static MpInterval Kr_dpx(const MpInterval& x, const MpInterval& px);
static int run_meet(capd::MpIMap& f, const Spec& S) {
  // X = (c, z_1..z_{m-1}, z'_1..z'_{m-1}, c', alpha), dim D = 4m - 1. Equations: forward links from w_u(c), links from
  // w_u(c'), the meeting P(z_{m-1}) - R P(z'_{m-1}) - alpha g = 0, and the phase condition x(z_{m-1}) = xh, xh in
  // [xmid +- xrad] (the family parameter; uniform contraction over it).
  Frame Fr = readframe(S); int m = S.n("m"); int D = 4 * m - 1;
  MpInterval cb = S.q("c0"), cp = S.q("cprime"), xmid = S.q("xmid"), xrad = S.q("xrad"); IV g(2); g[0] = S.q("g", 0); g[1] = S.q("g", 1);
  std::vector<IV> z(m), zp(m);
  for (int i = 1; i < m; ++i) { z[i] = IV(2); zp[i] = IV(2); z[i][0] = S.q("z", 2 * (i - 1)); z[i][1] = S.q("z", 2 * (i - 1) + 1); zp[i][0] = S.q("zp", 2 * (i - 1)); zp[i][1] = S.q("zp", 2 * (i - 1) + 1); }
  std::vector<double> ts(m), tsp(m); for (int i = 0; i < m; ++i) { ts[i] = std::stod(S.v("tstop").at(i)); tsp[i] = std::stod(S.v("tstopp").at(i)); }
  IV U = ut(Fr), Sv = st(Fr); IM Rm(2, 2); Rm[0][0] = 1; Rm[1][1] = -1;
  const int ob = 1 + 2 * (m - 1), rb = 2 * (m - 1), mr = 4 * (m - 1);
  std::vector<Pass> pt(m), ptp(m);
  { IV w0 = Fr.c + U * cb; pt[0] = pass(f, w0[0], w0[1], ts[0], false, "meet_pt0"); }
  { IV w0 = Fr.c + U * cp; ptp[0] = pass(f, w0[0], w0[1], tsp[0], false, "meet_ptp0"); }
  for (int i = 1; i < m; ++i) { pt[i] = pass(f, z[i][0], z[i][1], ts[i], false, "meet_pt" + std::to_string(i)); ptp[i] = pass(f, zp[i][0], zp[i][1], tsp[i], false, "meet_ptp" + std::to_string(i)); }
  IV F(D);
  for (int i = 0; i < m - 1; ++i) { F[2 * i] = pt[i].P[0] - z[i + 1][0]; F[2 * i + 1] = pt[i].P[2] - z[i + 1][1];
    F[rb + 2 * i] = ptp[i].P[0] - zp[i + 1][0]; F[rb + 2 * i + 1] = ptp[i].P[2] - zp[i + 1][1]; }
  F[mr] = pt[m - 1].P[0] - ptp[m - 1].P[0]; F[mr + 1] = pt[m - 1].P[2] + ptp[m - 1].P[2];
  F[D - 1] = z[m - 1][0] - xmid;
  printv("F", F);
  if (S.has("pointonly")) return 0;
  IM A = readmat(S, "A", D, D);
  MpInterval eta = etarad(Fr, cb), etap = etarad(Fr, cp);
  IV Fe = F; Fe[0] += sym(eta / 10); Fe[1] += sym(eta / 10); Fe[rb] += sym(etap / 10); Fe[rb + 1] += sym(etap / 10); Fe[D - 1] += sym(xrad);
  R r = pickr(normInfV(A * Fe), S); MpInterval R1(r);
  checkreach(Fr, cb, r, "meet c"); checkreach(Fr, cp, r, "meet c'");
  std::printf("BALL r %s eta %s etap %s\n", bnd(r, true).c_str(), bnd(eta.rightBound(), true).c_str(), bnd(etap.rightBound(), true).c_str()); dI("meet", "r", 0, 0, MpInterval(r));
  std::vector<Pass> bl(m), blp(m);
  { MpInterval uu = cb + sym(R1), ee = sym(etarad(Fr, uu) + Fr.L * R1); IV W = Fr.c + U * uu + Sv * ee; bl[0] = pass(f, W[0], W[1], ts[0], true, "meet_ball0"); }
  { MpInterval uu = cp + sym(R1), ee = sym(etarad(Fr, uu) + Fr.L * R1); IV W = Fr.c + U * uu + Sv * ee; blp[0] = pass(f, W[0], W[1], tsp[0], true, "meet_ballp0"); }
  for (int i = 1; i < m; ++i) { bl[i] = pass(f, z[i][0] + sym(R1), z[i][1] + sym(R1), ts[i], true, "meet_ball" + std::to_string(i));
                                blp[i] = pass(f, zp[i][0] + sym(R1), zp[i][1] + sym(R1), tsp[i], true, "meet_ballp" + std::to_string(i)); }
  { IV d0 = (bl[0].D * Sv) * sym(eta); F[0] += d0[0]; F[1] += d0[1];
    IV d1 = (blp[0].D * Sv) * sym(etap); F[rb] += d1[0]; F[rb + 1] += d1[1];
    F[D - 1] += sym(xrad); }
  IM DF(D, D);
  IV c0 = bl[0].D * U + (bl[0].D * Sv) * sym(Fr.L); DF[0][0] = c0[0]; DF[1][0] = c0[1];
  IV cpc = blp[0].D * U + (blp[0].D * Sv) * sym(Fr.L); DF[rb][D - 2] = cpc[0]; DF[rb + 1][D - 2] = cpc[1];
  for (int i = 0; i < m - 1; ++i) {
    int cz = 1 + 2 * i, czp = ob + 2 * i;                       // columns of z_{i+1}, z'_{i+1}
    DF[2 * i][cz] = -1; DF[2 * i + 1][cz + 1] = -1; DF[rb + 2 * i][czp] = -1; DF[rb + 2 * i + 1][czp + 1] = -1;
    if (i < m - 2) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) { DF[2 * i + 2 + a][cz + b] = bl[i + 1].D[a][b]; DF[rb + 2 * i + 2 + a][czp + b] = blp[i + 1].D[a][b]; }
  }
  IM RD = Rm * blp[m - 1].D; int czl = 1 + 2 * (m - 2), czpl = ob + 2 * (m - 2);
  for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) { DF[mr + a][czl + b] = bl[m - 1].D[a][b]; DF[mr + a][czpl + b] = -RD[a][b]; }
  DF[mr][D - 1] = -g[0]; DF[mr + 1][D - 1] = -g[1];
  DF[D - 1][czl] = 1;
  IM ID(D, D); for (int i = 0; i < D; ++i) ID[i][i] = 1;
  MpInterval Y = normInfV(A * F), Z = normInf(ID - A * DF);
  bool ok = krawczyk(Y, Z, r);
  IV dz(2); dz[0] = sym(R1); dz[1] = sym(R1); IV pe = blp[m - 1].D * dz; IV y(2); y[0] = ptp[m - 1].P[0] + pe[0]; y[1] = -(ptp[m - 1].P[2] + pe[1]);
  MpInterval al = sym(R1); IV hull(2); hull[0] = y[0] + g[0] * al; hull[1] = y[1] + g[1] * al;
  MpInterval gk = Kr_dx(hull[0], hull[1], MNC[3], MNC[4]) * g[0] + Kr_dpx(hull[0], hull[1]) * g[1];
  bool sgn = capd_proof::certainly_disjoint(gk, MpInterval(0));
  // the family: c(xh) for xh in the interval; report the c-enclosure (the homoclinic points w_u(c(xh)) lie on W^u)
  std::printf("KLEMMA gradK.g on the meeting hull %s -> %s\n", iv(gk).c_str(), sgn ? "SIGN-DEFINITE (alpha = 0 exactly by Carter)" : "NOT sign-definite");
  std::printf("FAMILY xh in %s ; c in %s\n", iv(xmid + sym(xrad)).c_str(), iv(cb + sym(R1)).c_str());
  std::printf("RESULT meet krawczyk %s klemma %s r %s\n", ok ? "CERTIFIED" : "FAIL", sgn ? "OK" : "FAIL", bnd(r, true).c_str());
  return ok && sgn ? 0 : 3;
}
// K_r(x, p_x) = 1/2 [Delta p_r^2 - Pr^2 / Delta + r^2], r = M + k x, p_r = p_x / k, Delta = r^2 - 2 M r + a^2, Pr = E (r^2 + a^2) - a L
static MpInterval Kr_dx(const MpInterval& x, const MpInterval& px, const MpInterval& E, const MpInterval& L) {
  MpInterval M(5), a(3), k(4), r = M + k * x, pr = px / k, Del = r * r - 2 * M * r + a * a, dDel = 2 * r - 2 * M, Pr = E * (r * r + a * a) - a * L, dPr = 2 * E * r;
  MpInterval dKdr = (dDel * pr * pr - (2 * Pr * dPr * Del - Pr * Pr * dDel) / (Del * Del) + 2 * r) / 2;
  return dKdr * k;
}
static MpInterval Kr_dpx(const MpInterval& x, const MpInterval& px) { MpInterval M(5), a(3), k(4), r = M + k * x, Del = r * r - 2 * M * r + a * a; return Del * px / (k * k); }

int main(int argc, char** argv) {
  try {
    T0 = now();
    if (argc < 3) { std::cerr << "usage: s2_main fp|cone|bvp|meet spec\n"; return 2; }
    std::string mode = argv[1]; Spec S = readspec(argv[2]);
    if (argc > 3) { DUMPF = std::fopen(argv[3], "w"); if (!DUMPF) throw std::runtime_error("cannot open dump"); }
    R::setDefaultPrecision(S.has("prec") ? S.n("prec") : 128); if (S.has("order")) ORDER = S.n("order"); if (S.has("tol")) TOL = S.d("tol");
    MNC[0] = Q("4"); MNC[1] = Q("-1/3"); MNC[2] = S.q("beta"); MNC[3] = Q("0.93528150456799871854"); MNC[4] = Q("12.972532035607280691");
    capd::MpIMap f(mn_vf, 4, 4, 5); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]);
    std::printf("RUN %s spec %s field %s beta %s prec %d order %d tol %.1e\n", mode.c_str(), argv[2], FIELD, S.v("beta")[0].c_str(), (int)R::getDefaultPrecision(), ORDER, TOL); std::fflush(stdout);
    int rc = mode == "fp" ? run_fp(f, S) : mode == "cone" ? run_cone(f, S) : mode == "bvp" ? run_bvp(f, S) : mode == "meet" ? run_meet(f, S) : 2;
    std::printf("END rc %d total wall %.1f s\n", rc, now() - T0);
    return rc;
  } catch (std::exception& e) { std::printf("FAIL %s\n", e.what()); return 1; }
}
