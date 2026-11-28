// Route-1 pilot, development harness 1 (NOT proof code; no claims). Claude Opus 5.5 (Quantum), 2026-11-28.
// The MN field with beta carried as a 5th STATE variable (beta' = 0), so that d/dbeta comes out of CAPD's C^2 jet.
// mode "jet": integrate the C^2 time map over [0, T] from a thin point (x, y, px, py, beta) and print the value,
// the Jacobian column d/dbeta, and selected Hessian entries, for comparison with float finite differences.
// mode "ret" (D2): the C^2 section return map in reduced coordinates u = (x, px, beta) on y = 0, H = -1/2:
//   lift L(u) = (x, 0, px, p_y(x, px, beta), beta) as its own C^2 map, the flow to Tstop then the CAPD C^2 Poincare map,
//   and the chain rule; prints P, DP (2x3) and TRUE second derivatives d2P (2x3x3) for a float finite-difference check.
// mode "fpw" (D3): the fixed point uniformly over beta in [b0, b1] by a parametric Krawczyk argument for
//   G(z, beta) = P(L(z, beta)) - z, z = (x, px), on the ball zbar + [-r, r]^2, and the drift c'(beta) = -(D_z G)^-1 d_beta G.
//   C^1 passes; the lifted initial set is the mean-value enclosure L(mid U) + DL(U)(U - mid U), and D(P o L) = DP . DL(U).
// Usage: r1_dev jet T x y px py beta  |  r1_dev ret Tstop x px beta order tol  |  r1_dev fpw Tstop xbar pxbar b0 b1 r order tol
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <gmp.h>
#include <cstdio>
#include <iostream>
#include <string>
#include "proof_guard.h"
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Qs(const std::string& s) {   // exact rational "p/q" or integer, outward-rounded
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational " + s); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
static std::string e(const MpInterval& x) { R m = x.mid().leftBound(); char* s = nullptr; mpfr_asprintf(&s, "%.30Re", m.*RepAccess::rep); std::string o(s); mpfr_free_str(s);
  R w = x.rightBound() - x.leftBound(); char* t = nullptr; mpfr_asprintf(&t, "%.2Re", w.*RepAccess::rep); o += " w " + std::string(t); mpfr_free_str(t); return o; }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "gen/mn_field.h"
// state (x, y, px, py, beta); params (k, alpha, E, L, zero)
void mn_vf5(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], in[4], par[2], par[3]}; mn_field<Node>(in, o, c); o[4] = par[4];
}
// the lift: vars (x, px, beta) -> state (x, 0, px, p_y, beta); params (k, alpha, E, L, zero)
void lift5(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], in[2], par[2], par[3]}; Node xy[2] = {in[0], par[4]}, g[3]; mn_lift<Node>(xy, g, c);
  o[0] = in[0]; o[1] = par[4]; o[2] = in[1]; o[3] = sqrt((-1 - g[0] * in[1] * in[1] - 2 * g[2]) / g[1]); o[4] = in[2];
}
static void setpar(capd::MpIMap& f) {
  f.setParameter(0, Qs("4")); f.setParameter(1, Qs("-1/3")); f.setParameter(2, Qs("93528150456799871854/100000000000000000000"));
  f.setParameter(3, Qs("12972532035607280691/1000000000000000000")); f.setParameter(4, MpInterval(0));
}
// Taylor coefficient -> true second derivative (CAPD stores h(i,j,c) with the 1/2 on the diagonal only; see ROUTE1_DEV_LOG D1)
static MpInterval d2(const capd::MpIHessian& H, int i, int j, int c) { return j == c ? 2 * H(i, j, c) : (j < c ? H(i, j, c) : H(i, c, j)); }
static int run_ret(int argc, char** argv) {
  if (argc < 8) { std::cerr << "usage: r1_dev ret Tstop x px beta order tol\n"; return 2; }
  int order = std::stoi(argv[6]); double tol = std::stod(argv[7]);
  capd::MpIMap f(mn_vf5, 5, 5, 5); setpar(f);
  capd::MpIMap L(lift5, 3, 5, 5, 2); setpar(L);
  IV u(3); u[0] = Qs(argv[3]); u[1] = Qs(argv[4]); u[2] = Qs(argv[5]);
  IM DL(5, 3); capd::MpIHessian HL(5, 3); IV x0 = L(u, DL, HL);
  capd_proof::require_finite_all(x0, "lift");
  capd::MpIC2OdeSolver solver(f, order); solver.setAbsoluteTolerance(tol); solver.setRelativeTolerance(tol);
  capd::MpIC2TimeMap tm(solver); capd::MpC2Rect2Set s(x0);
  MpInterval T = Qs(argv[2]); tm(T, s);
  IV cS = (IV)s; if (!(cS[1].rightBound() < 0)) throw std::runtime_error("y(Tstop) < 0 not certified");
  capd::MpICoordinateSection section(5, 1); capd::MpIC2PoincareMap pm(solver, section, capd::poincare::MinusPlus);
  IM Dphi(5, 5); capd::MpIHessian Hphi(5, 5); MpInterval rt; IV P = pm(s, Dphi, Hphi, rt);
  IM DP(5, 5); capd::MpIHessian D2P(5, 5); pm.computeDP(P, Dphi, Hphi, DP, D2P);
  capd_proof::require_finite_all(P, "P"); capd_proof::require_finite_all(DP, "DP");
  int out[2] = {0, 2};
  for (int a = 0; a < 2; ++a) std::printf("P %d %s\n", a, e(P[out[a]]).c_str());
  for (int a = 0; a < 2; ++a) for (int b = 0; b < 3; ++b) {     // D(P o L) = DP DL
    MpInterval acc(0); for (int j = 0; j < 5; ++j) acc += DP[out[a]][j] * DL[j][b]; std::printf("D %d %d %s\n", a, b, e(acc).c_str()); }
  for (int a = 0; a < 2; ++a) for (int b = 0; b < 3; ++b) for (int c = b; c < 3; ++c) {   // d2(P o L) = d2P(DL, DL) + DP d2L
    MpInterval acc(0); int i = out[a];
    for (int j = 0; j < 5; ++j) for (int k = 0; k < 5; ++k) acc += d2(D2P, i, j, k) * DL[j][b] * DL[k][c];
    for (int j = 0; j < 5; ++j) acc += DP[i][j] * d2(HL, j, b, c);
    std::printf("D2 %d %d %d %s\n", a, b, c, e(acc).c_str()); }
  return 0;
}
// one C^1 return of the lifted box U (3-D: x, px, beta) -> value box P (x, px) and D (2 x 3) = rows(x, px) of DP . DL(U)
struct Ret { IV P; IM D; };
static Ret ret1(capd::MpIMap& f, capd::MpIMap& L, const IV& U, const MpInterval& Tstop, int order, double tol) {
  IV um(3); for (int i = 0; i < 3; ++i) um[i] = MpInterval(U[i].mid().leftBound());
  IM DLm(5, 3); IV xm = L(um, DLm); IM DLU(5, 3); L(U, DLU);
  IV X0 = xm + DLU * (U - um);                     // mean-value enclosure of L(U)
  capd_proof::require_finite_all(X0, "lift box");
  IV c(5); for (int i = 0; i < 5; ++i) c[i] = MpInterval(X0[i].mid().leftBound());
  capd::MpIOdeSolver solver(f, order); solver.setAbsoluteTolerance(tol); solver.setRelativeTolerance(tol);
  capd::MpITimeMap tm(solver); capd::MpC1Rect2Set s(c, IV(X0 - c)); MpInterval T = Tstop; tm(T, s);
  IV cS = (IV)s; if (!(cS[1].rightBound() < 0)) throw std::runtime_error("y(Tstop) < 0 not certified");
  capd::MpICoordinateSection section(5, 1); capd::MpIPoincareMap pm(solver, section, capd::poincare::MinusPlus);
  IM Dphi(5, 5); MpInterval rt; IV P = pm(s, Dphi, rt); IM DP = pm.computeDP(P, Dphi, rt);
  capd_proof::require_finite_all(P, "P"); capd_proof::require_finite_all(DP, "DP");
  Ret o; o.P = IV(2); o.P[0] = P[0]; o.P[1] = P[2]; o.D = IM(2, 3); int rows[2] = {0, 2};
  for (int a = 0; a < 2; ++a) for (int b = 0; b < 3; ++b) { MpInterval acc(0); for (int j = 0; j < 5; ++j) acc += DP[rows[a]][j] * DLU[j][b]; o.D[a][b] = acc; }
  capd_proof::require_finite_all(o.D, "D(PoL)");
  return o;
}
static MpInterval absmax(const MpInterval& a) { R l = a.leftBound(), h = a.rightBound(); if (l < 0) l = -l; if (h < 0) h = -h; return MpInterval(l > h ? l : h); }
static int run_fpw(int argc, char** argv) {
  // PARAMETRIC centre: zhat(beta) = zbar + ct (beta - bm), ct = a float estimate of c'. Then, along the path (zhat(beta), beta),
  // G(zhat(beta), beta) = G0 + D_tau G * (beta - bm) with D_tau G = D_z G ct + d_beta G - ct (mean value over the derivative pass),
  // so Y = |A G0| + |A D_tau G| w/2 keeps the beta-correlation that a box evaluation loses (D3, first attempt).
  if (argc < 12) { std::cerr << "usage: r1_dev fpw Tstop xbar pxbar b0 b1 r ctx ctp order tol   (zbar = fixed point at bm = (b0+b1)/2)\n"; return 2; }
  MpInterval Tstop = Qs(argv[2]), xb = Qs(argv[3]), pb = Qs(argv[4]), B(Qs(argv[5]).leftBound(), Qs(argv[6]).rightBound()), r = Qs(argv[7]);
  MpInterval ctx = Qs(argv[8]), ctp = Qs(argv[9]); int order = std::stoi(argv[10]); double tol = std::stod(argv[11]);
  MpInterval bm(B.mid().leftBound()), hw = (B - bm); hw = absmax(hw);           // half-width of the beta interval
  capd::MpIMap f(mn_vf5, 5, 5, 5); setpar(f); capd::MpIMap L(lift5, 3, 5, 5, 1); setpar(L);
  IV Upt(3); Upt[0] = xb; Upt[1] = pb; Upt[2] = bm;                               // thin point (zbar, bm)
  MpInterval Rr = r + absmax(ctx) * hw; { MpInterval R2 = r + absmax(ctp) * hw; if (R2.rightBound() > Rr.rightBound()) Rr = R2; }
  MpInterval RR(-Rr.rightBound(), Rr.rightBound());
  IV Ub(3); Ub[0] = xb + RR; Ub[1] = pb + RR; Ub[2] = B;                           // contains zhat(beta) + [-r, r]^2 for all beta in B
  Ret a = ret1(f, L, Upt, Tstop, order, tol); Ret b = ret1(f, L, Ub, Tstop, order, tol);
  IV G0(2); G0[0] = a.P[0] - xb; G0[1] = a.P[1] - pb;
  IM DG(2, 2); for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) DG[i][j] = b.D[i][j] - (i == j ? MpInterval(1) : MpInterval(0));
  IV DtG(2); DtG[0] = DG[0][0] * ctx + DG[0][1] * ctp + b.D[0][2]; DtG[1] = DG[1][0] * ctx + DG[1][1] * ctp + b.D[1][2];
  MpInterval m00(DG[0][0].mid().leftBound()), m01(DG[0][1].mid().leftBound()), m10(DG[1][0].mid().leftBound()), m11(DG[1][1].mid().leftBound());
  MpInterval det = m00 * m11 - m01 * m10; IM A(2, 2); A[0][0] = m11 / det; A[0][1] = -m01 / det; A[1][0] = -m10 / det; A[1][1] = m00 / det;
  IV AG0 = A * G0, ADt = A * DtG; IM ADG = A * DG; IM I_ADG(2, 2);
  for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) I_ADG[i][j] = (i == j ? MpInterval(1) : MpInterval(0)) - ADG[i][j];
  MpInterval Y(0); for (int i = 0; i < 2; ++i) { MpInterval yi = absmax(AG0[i]) + absmax(ADt[i]) * hw; if (yi.rightBound() > Y.rightBound()) Y = MpInterval(yi.rightBound()); }
  MpInterval Z(0); for (int i = 0; i < 2; ++i) { MpInterval row = absmax(I_ADG[i][0]) + absmax(I_ADG[i][1]); if (row.rightBound() > Z.rightBound()) Z = MpInterval(row.rightBound()); }
  MpInterval marg = Z * r - r + Y; bool ok = Z.rightBound() < 1 && marg.rightBound() < 0;
  MpInterval d = DG[0][0] * DG[1][1] - DG[0][1] * DG[1][0];
  if (d.contains(MpInterval(0))) throw std::runtime_error("D_z G singular on the ball");
  MpInterval g0 = b.D[0][2], g1 = b.D[1][2];
  MpInterval cx = -(DG[1][1] * g0 - DG[0][1] * g1) / d, cp = -(-DG[1][0] * g0 + DG[0][0] * g1) / d;
  std::printf("FPW beta [%s] r %s R %s\n", e(B).c_str(), e(r).c_str(), e(Rr).c_str());
  std::printf("G0 %s %s\nDtauG %s %s\n", e(G0[0]).c_str(), e(G0[1]).c_str(), e(DtG[0]).c_str(), e(DtG[1]).c_str());
  std::printf("KRAWCZYK Y %s Z %s margin %s -> %s\n", e(Y).c_str(), e(Z).c_str(), e(marg).c_str(), ok ? "CERTIFIED (for every beta in B a unique fixed point in zhat(beta) + [-r,r]^2)" : "FAIL");
  std::printf("CPRIME x %s\nCPRIME px %s\n", e(cx).c_str(), e(cp).c_str());
  return ok ? 0 : 3;
}
int main(int argc, char** argv) {
  try {
    R::setDefaultPrecision(128);
    if (argc > 1 && std::string(argv[1]) == "fpw") return run_fpw(argc, argv);
    if (argc > 1 && std::string(argv[1]) == "ret") return run_ret(argc, argv);
    if (argc < 8) { std::cerr << "usage: r1_dev jet T x y px py beta (exact rationals)\n"; return 2; }
    capd::MpIMap f(mn_vf5, 5, 5, 5); setpar(f);
    IV x0(5); for (int i = 0; i < 5; ++i) x0[i] = Qs(argv[3 + i]);
    capd::MpIC2OdeSolver solver(f, 20); solver.setAbsoluteTolerance(1e-24); solver.setRelativeTolerance(1e-24);   // step control only (double, as in S2)
    capd::MpIC2TimeMap tm(solver);
    capd::MpC2Rect2Set s(x0);
    MpInterval T = Qs(argv[2]);
    IV v = tm(T, s);
    IM D = (IM)s;
    capd_proof::require_finite_all(v, "value"); capd_proof::require_finite_all(D, "D");
    for (int i = 0; i < 5; ++i) std::printf("VAL %d %s\n", i, e(v[i]).c_str());
    for (int i = 0; i < 5; ++i) std::printf("DBETA %d %s\n", i, e(D[i][4]).c_str());
    for (int i = 0; i < 4; ++i) std::printf("DX %d %s\n", i, e(D[i][0]).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_x_beta %d %s\n", i, e(s(i, 0, 4)).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_x_x %d %s\n", i, e(s(i, 0, 0)).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_beta_beta %d %s\n", i, e(s(i, 4, 4)).c_str());
    return 0;
  } catch (std::exception& ex) { std::printf("FAIL %s\n", ex.what()); return 1; }
}
