// s2_l4.cpp -- S2 control (iv): the validator's positive control on CKMJ Thm 3 (arXiv:2205.03922v2 §7.4): PCRTBP,
// mu = 1/2, the L4 level E = 3, a transverse homoclinic to L4 through B(p-bar, 1.66e-9). MPFR intervals only, under
// proof_guard.h; the same Krawczyk inequality (CKMJ Thm 30), the same cone lemma (A11, here in its 2+2 form, A12), the
// same MPFR-128 / order 20 / tolerance 1e-24 as the MN runs. Written by Claude Opus 5.5 (Quantum), 2026-11-27.
//
// Field (CKMJ eqs. 26-27), state (x, p, y, q): x' = p, p' = 2q + Om_x, y' = q, q' = -2p + Om_y,
//   Om = (1-mu)(r1^2/2 + 1/r1) + mu (r2^2/2 + 1/r2), r1^2 = (x-mu)^2 + y^2, r2^2 = (x+1-mu)^2 + y^2;
//   E = -(p^2 + q^2) + 2 Om (E(L4) = 3). Unfolding (CKMJ Example 15 / Thm 16): z' = f + alpha grad E.
// Extended system for the BVP: (x, p, y, q, alpha, T), d/ds z = sigma T (f + alpha grad E), alpha' = T' = 0, integrated
// over s in [0, 1] (so T and alpha are state; their derivatives come from the C^1 data). sigma = +1 (or -1 for the
// stable-manifold cone map). Domain: r1, r2 >= 1/100 on every step enclosure (fail closed).
// Modes: cone <spec>  (keys: sigma tau delta T(4x4 frame, columns u1 u2 s1 s2))
//        bvp  <spec>  (keys: n theta phi rho Tseg x(n-1 x 4) Tu(4x4) Lu Ts(4x4) Ls A rmin [pointonly] pbar(4) tshift kk)
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
static MpInterval mag(const MpInterval& a) { R l = a.leftBound(), h = a.rightBound(); if (l < 0) l = -l; if (h < 0) h = -h; return MpInterval(l > h ? l : h); }
static MpInterval sym(const MpInterval& r) { return MpInterval(-r.rightBound(), r.rightBound()); }
static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
static double T0;

// extended field, dim 6: (x, p, y, q, alpha, T); par[0] = mu, par[1] = sigma
void l4_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node mu = par[0], sg = par[1], x = in[0], p = in[1], y = in[2], q = in[3], al = in[4], T = in[5];
  Node r1s = (x - mu) * (x - mu) + y * y, r2s = (x + 1 - mu) * (x + 1 - mu) + y * y;
  Node r1 = sqrt(r1s), r2 = sqrt(r2s), i1 = 1 / (r1s * r1), i2 = 1 / (r2s * r2);
  Node Ox = (1 - mu) * (x - mu) * (1 - i1) + mu * (x + 1 - mu) * (1 - i2), Oy = (1 - mu) * y * (1 - i1) + mu * y * (1 - i2);
  o[0] = sg * T * (p + al * 2 * Ox); o[1] = sg * T * (2 * q + Ox - al * 2 * p);
  o[2] = sg * T * (q + al * 2 * Oy); o[3] = sg * T * (-2 * p + Oy - al * 2 * q);
  o[4] = 0 * x; o[5] = 0 * x;
}
static MpInterval MU;
static void l4_domain(const IV& b) {
  capd_proof::require_finite_all(b, "L4 enclosure");
  MpInterval r1s = (b[0] - MU) * (b[0] - MU) + b[2] * b[2], r2s = (b[0] + 1 - MU) * (b[0] + 1 - MU) + b[2] * b[2], lim = MpInterval(1) / 10000;
  if (!(r1s.leftBound() > lim.rightBound() && r2s.leftBound() > lim.rightBound())) throw std::runtime_error("domain: r1 or r2 < 1/100 possible");
}
static MpInterval Efn(const IV& z) {
  MpInterval x = z[0], p = z[1], y = z[2], q = z[3];
  MpInterval r1 = sqrt((x - MU) * (x - MU) + y * y), r2 = sqrt((x + 1 - MU) * (x + 1 - MU) + y * y);
  MpInterval Om = (1 - MU) * (r1 * r1 / 2 + 1 / r1) + MU * (r2 * r2 / 2 + 1 / r2);
  return -(p * p + q * q) + 2 * Om;
}
static int ORDER = 20; static double TOL = 1e-24;

struct Pass { IV P; IM D; };
// flow of the extended field over s in [0, 1] from the box Z0 (dim 6); c1: also the 6x6 derivative
static Pass pass(capd::MpIMap& f, const IV& Z0, bool c1, const std::string& tag) {
  double t0 = now();
  capd::MpIOdeSolver solver(f, ORDER); solver.setAbsoluteTolerance(TOL); solver.setRelativeTolerance(TOL);
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true); MpInterval T(1); Pass out; long steps = 0;
  if (c1) {
    IV c(6); for (int i = 0; i < 6; ++i) c[i] = MpInterval(Z0[i].mid().leftBound());
    capd::MpC1Rect2Set s(c, IV(Z0 - c));
    do { tm(T, s); l4_domain(s.getLastEnclosure()); ++steps; } while (!tm.completed());
    out.P = (IV)s; out.D = (IM)s;
  } else {
    capd::MpC0TripletonSet s(Z0);
    do { tm(T, s); l4_domain(s.getLastEnclosure()); ++steps; } while (!tm.completed());
    out.P = (IV)s;
  }
  capd_proof::require_finite_all(out.P, (tag + " image").c_str());
  std::printf("PASS %s %s steps %ld wall %.1f s (total %.1f s)\n", tag.c_str(), c1 ? "C1" : "C0", steps, now() - t0, now() - T0); std::fflush(stdout);
  return out;
}

struct Spec { std::map<std::string, std::vector<std::string>> kv; bool has(const std::string& k) const { return kv.count(k); }
  const std::vector<std::string>& v(const std::string& k) const { auto it = kv.find(k); if (it == kv.end()) throw std::runtime_error("spec: missing " + k); return it->second; }
  MpInterval q(const std::string& k, size_t i = 0) const { return Q(v(k).at(i)); }
  int n(const std::string& k) const { return std::stoi(v(k).at(0)); } };
static Spec readspec(const char* fn) {
  Spec S; std::ifstream in(fn); if (!in) throw std::runtime_error("cannot open spec"); std::string line;
  while (std::getline(in, line)) { if (line.empty() || line[0] == '#') continue; std::istringstream ss(line); std::string k, t; ss >> k; std::vector<std::string> vals; while (ss >> t) vals.push_back(t); S.kv[k] = vals; }
  return S;
}
static IM readmat(const Spec& S, const std::string& k, int n, int m) { const auto& v = S.v(k); if ((int)v.size() != n * m) throw std::runtime_error("spec: " + k + " size"); IM A(n, m); for (int i = 0; i < n; ++i) for (int j = 0; j < m; ++j) A[i][j] = Q(v[i * m + j]); return A; }
static MpInterval normInf(const IM& A) { MpInterval best(0); for (int i = 0; i < (int)A.numberOfRows(); ++i) { MpInterval s(0); for (int j = 0; j < (int)A.numberOfColumns(); ++j) s += mag(A[i][j]); if (s.rightBound() > best.rightBound()) best = MpInterval(s.rightBound()); } return best; }
static MpInterval normInfV(const IV& v) { MpInterval b(0); for (int i = 0; i < (int)v.dimension(); ++i) { MpInterval m = mag(v[i]); if (m.rightBound() > b.rightBound()) b = MpInterval(m.rightBound()); } return b; }
static MpInterval frob(const IM& A) { MpInterval s(0); for (int i = 0; i < (int)A.numberOfRows(); ++i) for (int j = 0; j < (int)A.numberOfColumns(); ++j) { MpInterval m = mag(A[i][j]); s += m * m; } return MpInterval(sqrt(s).rightBound()); }
// interval Gauss-Jordan inverse (no pivot search needed for our well-conditioned frames; fails closed on a zero pivot)
static IM ginv(const IM& A0) {
  int n = A0.numberOfRows(); IM A = A0, B(n, n); for (int i = 0; i < n; ++i) B[i][i] = 1;
  for (int k = 0; k < n; ++k) {
    int piv = k; for (int i = k + 1; i < n; ++i) if (mag(A[i][k]).leftBound() > mag(A[piv][k]).leftBound()) piv = i;
    if (piv != k) for (int j = 0; j < n; ++j) { std::swap(A[k][j], A[piv][j]); std::swap(B[k][j], B[piv][j]); }
    if (A[k][k].contains(MpInterval(0))) throw std::runtime_error("ginv: pivot contains 0");
    MpInterval d = A[k][k];
    for (int j = 0; j < n; ++j) { A[k][j] /= d; B[k][j] /= d; }
    for (int i = 0; i < n; ++i) if (i != k) { MpInterval fct = A[i][k]; for (int j = 0; j < n; ++j) { A[i][j] -= fct * A[k][j]; B[i][j] -= fct * B[k][j]; } }
  }
  return B;
}
static IM blk(const IM& M, int r0, int c0) { IM B(2, 2); for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) B[i][j] = M[r0 + i][c0 + j]; return B; }
static IV L4pt() { IV z(4); z[0] = MU - MpInterval(1) / 2; z[1] = 0; z[2] = sqrt(MpInterval(3)) / 2; z[3] = 0; return z; }

// ---------------- cone (A12: the 2+2 form of the A11 lemma, for the time-tau map at L4)
static int run_cone(const Spec& S) {
  MpInterval sg = S.q("sigma"), tau = S.q("tau"), delta = S.q("delta"); IM Te = readmat(S, "T", 4, 4), Ti = ginv(Te);
  capd::MpIMap f(l4_vf, 6, 6, 2); f.setParameter(0, MU); f.setParameter(1, sg);
  IV L = L4pt(); IV Z0(6);
  for (int i = 0; i < 4; ++i) { MpInterval rs(0); for (int j = 0; j < 4; ++j) rs += mag(Te[i][j]); Z0[i] = L[i] + sym(rs * delta); }
  Z0[4] = 0; Z0[5] = tau;
  Pass b = pass(f, Z0, true, sg.leftBound() > 0 ? "cone_u" : "cone_s");
  IM DP(4, 4); for (int i = 0; i < 4; ++i) for (int j = 0; j < 4; ++j) DP[i][j] = b.D[i][j];
  IM Mm = Ti * DP * Te;
  IM A = blk(Mm, 0, 0), B = blk(Mm, 0, 2), C = blk(Mm, 2, 0), Dd = blk(Mm, 2, 2);
  MpInterval det = A[0][0] * A[1][1] - A[0][1] * A[1][0]; if (det.contains(MpInterval(0))) { std::printf("RESULT cone FAIL det A\n"); return 3; }
  IM Ai(2, 2); Ai[0][0] = A[1][1] / det; Ai[0][1] = -A[0][1] / det; Ai[1][0] = -A[1][0] / det; Ai[1][1] = A[0][0] / det;
  MpInterval mA = MpInterval(1) / frob(Ai), nA = frob(A), nB = frob(B), nC = frob(C), nD = frob(Dd);
  MpInterval rhop = normInf(Ti) * MpInterval(Q("1e-36").rightBound());      // L4 is exact up to its interval enclosure (< 1e-36)
  std::printf("CONEDATA mA >= %s |A| <= %s |B| <= %s |C| <= %s |D| <= %s\n", bnd(mA.leftBound(), false).c_str(), bnd(nA.rightBound(), true).c_str(), bnd(nB.rightBound(), true).c_str(), bnd(nC.rightBound(), true).c_str(), bnd(nD.rightBound(), true).c_str());
  for (int k = 0; k < 40; ++k) {
    if (!(nD.rightBound() < 1)) break;                       // (H2) impossible
    MpInterval Lc = (nC * 2 / (1 - MpInterval(nD.rightBound()))) * MpInterval(1 << (k % 20)) * (k >= 20 ? MpInterval(1048576) : MpInterval(1));   // L0 = 2|C|/(1 - |D|): (H2) by construction
    if (!(Lc.leftBound() > 0)) continue;
    MpInterval mu = MpInterval(mA.leftBound()) - nB * Lc, nu = nC / Lc + nD;
    bool h1 = mu.leftBound() > 1 && (nC + nD * Lc - Lc * mu).rightBound() <= 0, h2 = nu.rightBound() < 1;
    if (h1 && h2) {
      MpInterval kappa = nA + nB * Lc, mx = Lc.rightBound() > 1 ? Lc : MpInterval(1), dstar = (delta - rhop) / (kappa * mx);
      std::printf("RESULT cone CERTIFIED L %s mu %s nu %s deltastar %s\n", bnd(Lc.rightBound(), true).c_str(), bnd(mu.leftBound(), false).c_str(), bnd(nu.rightBound(), true).c_str(), bnd(dstar.leftBound(), false).c_str());
      return 0;
    }
  }
  std::printf("RESULT cone FAIL (H1/H2)\n"); return 3;
}

// ---------------- bvp: X = (theta, x_1..x_{n-1} (4 each), phi, T, alpha), dim 4n
static int run_bvp(const Spec& S) {
  int n = S.n("n"), D = 4 * n; IM Tu = readmat(S, "Tu", 4, 4), Ts = readmat(S, "Ts", 4, 4); MpInterval Lu = S.q("Lu"), Ls = S.q("Ls"), rho = S.q("rho");
  MpInterval th = S.q("theta"), ph = S.q("phi"), Tg = S.q("Tseg"); IV L = L4pt();
  std::vector<MpInterval> cf(n); for (int i = 0; i < n; ++i) cf[i] = S.has("cfrac") ? S.q("cfrac", i) : MpInterval(1);   // segment i flows c_i T
  std::vector<IV> xs(n + 1); for (int i = 1; i < n; ++i) { xs[i] = IV(4); for (int k = 0; k < 4; ++k) xs[i][k] = S.q("x", 4 * (i - 1) + k); }
  capd::MpIMap f(l4_vf, 6, 6, 2); f.setParameter(0, MU); f.setParameter(1, MpInterval(1));
  // endpoints: w(theta) = L4 + Tu[:,0:2] rho (cos, sin) + Tu[:,2:4] h, |h| <= L rho (Euclidean), so each s-coordinate in [-L rho, L rho]
  auto wpt = [&](const IM& Tf, const MpInterval& a, const MpInterval& hr) { IV w(4); MpInterval c = capd_proof::checked_cos(a) * rho, s = capd_proof::checked_sin(a) * rho;
    for (int i = 0; i < 4; ++i) w[i] = L[i] + Tf[i][0] * c + Tf[i][1] * s + sym((mag(Tf[i][2]) + mag(Tf[i][3])) * hr); return w; };
  auto wdt = [&](const IM& Tf, const MpInterval& a, const MpInterval& Lh) { IV d(4); MpInterval c = -capd_proof::checked_sin(a) * rho, s = capd_proof::checked_cos(a) * rho;   // tangent along theta
    for (int i = 0; i < 4; ++i) d[i] = Tf[i][0] * c + Tf[i][1] * s + sym((mag(Tf[i][2]) + mag(Tf[i][3])) * Lh * rho); return d; };
  auto ext = [&](const IV& z, const MpInterval& T, const MpInterval& al) { IV e(6); for (int i = 0; i < 4; ++i) e[i] = z[i]; e[4] = al; e[5] = T; return e; };
  IV w0c = wpt(Tu, th, MpInterval(0)), wec = wpt(Ts, ph, MpInterval(0));        // centres (h = 0); h terms by mean value
  std::vector<Pass> pt(n);
  pt[0] = pass(f, ext(w0c, Tg * cf[0], MpInterval(0)), false, "l4_pt0");
  for (int i = 1; i < n; ++i) pt[i] = pass(f, ext(xs[i], Tg * cf[i], MpInterval(0)), false, "l4_pt" + std::to_string(i));
  IV F(D);
  for (int i = 0; i < n; ++i) { const IV& tgt = i < n - 1 ? xs[i + 1] : wec; for (int k = 0; k < 4; ++k) F[4 * i + k] = pt[i].P[k] - tgt[k]; }
  for (int i = 0; i < D; ++i) std::printf("F[%d] %s mid %s\n", i, iv(F[i]).c_str(), mid40(F[i]).c_str());
  if (S.has("pointonly")) return 0;
  IM A = readmat(S, "A", D, D);
  MpInterval hu = Lu * rho, hs = Ls * rho;
  IV e1(D), e2(D), e3(D), e4(D);                              // structured endpoint-uncertainty directions (thin)
  for (int k = 0; k < 4; ++k) { e1[k] = Tu[k][2]; e2[k] = Tu[k][3]; e3[4 * (n - 1) + k] = Ts[k][2]; e4[4 * (n - 1) + k] = Ts[k][3]; }
  IV Ye = A * F + (A * e1) * sym(hu) + (A * e2) * sym(hu) + (A * e3) * sym(hs) + (A * e4) * sym(hs);
  R r = (normInfV(Ye) * 4).rightBound(); R rmin = S.q("rmin").rightBound(); if (r < rmin) r = rmin;
  MpInterval R1(r);
  std::printf("BALL r %s hu %s hs %s\n", bnd(r, true).c_str(), bnd(hu.rightBound(), true).c_str(), bnd(hs.rightBound(), true).c_str());
  std::vector<Pass> bl(n);
  MpInterval Ra = R1 / rho;                                   // the angle half-width (scaled unknowns)
  { IV W = wpt(Tu, th + sym(Ra), hu); bl[0] = pass(f, ext(W, (Tg + sym(R1)) * cf[0], sym(R1)), true, "l4_ball0"); }
  for (int i = 1; i < n; ++i) { IV Bx(4); for (int k = 0; k < 4; ++k) Bx[k] = xs[i][k] + sym(R1); bl[i] = pass(f, ext(Bx, (Tg + sym(R1)) * cf[i], sym(R1)), true, "l4_ball" + std::to_string(i)); }
  // mean-value h-terms are kept OUT of F (structured, applied after A below): start D_z Phi(ball0) Tu_s h, end -Ts_s h
  IM Dz0(4, 4); for (int a = 0; a < 4; ++a) for (int b = 0; b < 4; ++b) Dz0[a][b] = bl[0].D[a][b];
  IV su1(4), su2(4), ss1(4), ss2(4); for (int k = 0; k < 4; ++k) { su1[k] = Tu[k][2]; su2[k] = Tu[k][3]; ss1[k] = Ts[k][2]; ss2[k] = Ts[k][3]; }
  IV q1 = Dz0 * su1, q2 = Dz0 * su2;                 // thin
  IV E1(D), E2(D), E3(D), E4(D); for (int k = 0; k < 4; ++k) { E1[k] = q1[k]; E2[k] = q2[k]; E3[4 * (n - 1) + k] = -ss1[k]; E4[4 * (n - 1) + k] = -ss2[k]; }
  IM DF(D, D);
  auto put = [&](int r0, int c0, const IM& M, int rows, int cols) { for (int a = 0; a < rows; ++a) for (int b = 0; b < cols; ++b) DF[r0 + a][c0 + b] = M[a][b]; };
  for (int i = 0; i < n; ++i) {
    IM Dz(4, 4), DT(4, 1), Da(4, 1); for (int a = 0; a < 4; ++a) { for (int b = 0; b < 4; ++b) Dz[a][b] = bl[i].D[a][b]; Da[a][0] = bl[i].D[a][4]; DT[a][0] = bl[i].D[a][5] * cf[i]; }
    if (i == 0) { IV du(4), s1v(4), s2v(4); MpInterval ct = -capd_proof::checked_sin(th + sym(Ra)), st_ = capd_proof::checked_cos(th + sym(Ra));   // d/d(rho theta)
      for (int a = 0; a < 4; ++a) { du[a] = Tu[a][0] * ct + Tu[a][1] * st_; s1v[a] = Tu[a][2]; s2v[a] = Tu[a][3]; }
      IV c = Dz * du; for (int a = 0; a < 4; ++a) DF[a][0] = c[a]; }
    else put(4 * i, 1 + 4 * (i - 1), Dz, 4, 4);
    if (i < n - 1) for (int a = 0; a < 4; ++a) DF[4 * i + a][1 + 4 * i + a] = -1;
    else { MpInterval ct = -capd_proof::checked_sin(ph + sym(Ra)), st_ = capd_proof::checked_cos(ph + sym(Ra));
      for (int a = 0; a < 4; ++a) DF[4 * i + a][D - 3] = -(Ts[a][0] * ct + Ts[a][1] * st_); }   // d/d(rho phi), thin part
    put(4 * i, D - 2, DT, 4, 1); put(4 * i, D - 1, Da, 4, 1);
  }
  IM ID(D, D); for (int i = 0; i < D; ++i) ID[i][i] = 1;
  IV AE1 = A * E1, AE2 = A * E2, AE3 = A * E3, AE4 = A * E4;      // thin columns first, then the uncertainty factors
  IV YV = A * F + AE1 * sym(hu) + AE2 * sym(hu) + AE3 * sym(hs) + AE4 * sym(hs);
  IM AM = A * DF;
  for (int a = 0; a < D; ++a) { AM[a][0] += (AE1[a] + AE2[a]) * sym(Lu) * 0 + AE1[a] * sym(Lu) + AE2[a] * sym(Lu);   // theta column: Dz Tu_s Dh (|Dh| <= L)
                                AM[a][D - 3] += AE3[a] * sym(Ls) + AE4[a] * sym(Ls); }                              // phi column: -Ts_s Dh
  MpInterval Y = normInfV(YV), Z = normInf(ID - AM), v = Z * R1 - R1 + Y;
  bool ok = Z.rightBound() < 1 && v.rightBound() < 0;
  std::printf("KRAWCZYK Y %s Z %s r %s  Zr - r + Y <= %s\n", bnd(Y.rightBound(), true).c_str(), bnd(Z.rightBound(), true).c_str(), bnd(r, true).c_str(), bnd(v.rightBound(), true).c_str());
  // unfolding: E is constant along alpha = 0 orbits; both endpoints are on W^{u,s}(L4) in {E = 3}: CKMJ Thm 16 => alpha = 0
  MpInterval Eu = Efn(wpt(Tu, th + sym(Ra), hu)), Es = Efn(wpt(Ts, ph + sym(Ra), hs));
  std::printf("ENERGY at the endpoint enclosures: %s / %s (the manifolds lie in E = 3 exactly)\n", iv(Eu).c_str(), iv(Es).c_str());
  // CKMJ ball check: the certified orbit point near p-bar: node kk shifted by the flow time tshift (alpha = 0 field), C^0
  bool meets = false;
  if (S.has("pbar")) {
    int kk = S.n("kk"); MpInterval tsh = S.q("tshift"); IV pb(4); for (int k = 0; k < 4; ++k) pb[k] = S.q("pbar", k);
    IV Bx(4); for (int k = 0; k < 4; ++k) Bx[k] = xs[kk][k] + sym(R1);
    capd::MpIMap g(l4_vf, 6, 6, 2); g.setParameter(0, MU); g.setParameter(1, MpInterval(tsh.leftBound() >= 0 ? 1 : -1));
    Pass sh = pass(g, ext(Bx, mag(tsh), MpInterval(0)), false, "ckmj_shift");
    MpInterval d2(0); for (int k = 0; k < 4; ++k) { MpInterval d = sh.P[k] - pb[k]; d2 += d * d; } MpInterval dist = sqrt(MpInterval(d2.rightBound()));
    meets = dist.rightBound() <= Q("1.66e-9").leftBound();
    std::printf("CKMJ distance from p-bar to the certified orbit point: <= %s (CKMJ r = 1.659e-9) -> %s\n", bnd(dist.rightBound(), true).c_str(), meets ? "MEETS" : "does not meet");
  }
  std::printf("RESULT l4bvp krawczyk %s ckmj %s\n", ok ? "CERTIFIED" : "FAIL", meets ? "MEETS" : "NO");
  return ok && meets ? 0 : 3;
}


// ---------------- bvp2: X = (u in R^2, x_1..x_{n-1}, s in R^2, alpha), dim 4n + 1; segment times FIXED (Tseg c_i);
// endpoints w_u(u) = L4 + Tu_u u + Tu_s h_u(u) (|h| <= L|u|, ||Dh|| <= L), w_s(s) likewise; phase row <g, x_kk - xbar_kk> = 0.
static int run_bvp2(const Spec& S) {
  int n = S.n("n"), D = 4 * n + 1, kk = S.n("kk"); IM Tu = readmat(S, "Tu", 4, 4), Ts = readmat(S, "Ts", 4, 4);
  MpInterval Lu = S.q("Lu"), Ls = S.q("Ls"), dsu = S.q("deltastar_u"), dss = S.q("deltastar_s"), Tg = S.q("Tseg"); IV L = L4pt();
  IV ub(2), sb(2); ub[0] = S.q("u", 0); ub[1] = S.q("u", 1); sb[0] = S.q("s", 0); sb[1] = S.q("s", 1);
  std::vector<MpInterval> cf(n); for (int i = 0; i < n; ++i) cf[i] = S.q("cfrac", i);
  std::vector<IV> xs(n + 1); for (int i = 1; i < n; ++i) { xs[i] = IV(4); for (int k = 0; k < 4; ++k) xs[i][k] = S.q("x", 4 * (i - 1) + k); }
  IV gph(4); for (int k = 0; k < 4; ++k) gph[k] = S.q("g", k);
  capd::MpIMap f(l4_vf, 6, 6, 2); f.setParameter(0, MU); f.setParameter(1, MpInterval(1));
  auto ext = [&](const IV& z, const MpInterval& T, const MpInterval& al) { IV e(6); for (int i = 0; i < 4; ++i) e[i] = z[i]; e[4] = al; e[5] = T; return e; };
  auto col = [&](const IM& T, int j) { IV c(4); for (int k = 0; k < 4; ++k) c[k] = T[k][j]; return c; };
  auto nrm2 = [&](const IV& v) { MpInterval s2(0); for (int i = 0; i < (int)v.dimension(); ++i) s2 += mag(v[i]) * mag(v[i]); return MpInterval(sqrt(s2).rightBound()); };
  IV w0c = L + col(Tu, 0) * ub[0] + col(Tu, 1) * ub[1], wec = L + col(Ts, 0) * sb[0] + col(Ts, 1) * sb[1];
  std::vector<Pass> pt(n);
  pt[0] = pass(f, ext(w0c, Tg * cf[0], MpInterval(0)), false, "l4b_pt0");
  for (int i = 1; i < n; ++i) pt[i] = pass(f, ext(xs[i], Tg * cf[i], MpInterval(0)), false, "l4b_pt" + std::to_string(i));
  IV F(D);
  for (int i = 0; i < n; ++i) { const IV& tgt = i < n - 1 ? xs[i + 1] : wec; for (int k = 0; k < 4; ++k) F[4 * i + k] = pt[i].P[k] - tgt[k]; }
  { IV xr(4); for (int k = 0; k < 4; ++k) xr[k] = S.q("xref", k); MpInterval ph(0); for (int k = 0; k < 4; ++k) ph += gph[k] * (xs[kk][k] - xr[k]); F[D - 1] = ph; }   // phase row
  for (int i = 0; i < D; ++i) std::printf("F[%d] %s mid %s\n", i, iv(F[i]).c_str(), mid40(F[i]).c_str());
  if (S.has("pointonly")) return 0;
  IM A = readmat(S, "A", D, D);
  MpInterval hu = Lu * nrm2(ub), hs = Ls * nrm2(sb);                 // |h(u)| <= L |u| (L4 exact)
  IV e1(D), e2(D), e3(D), e4(D); for (int k = 0; k < 4; ++k) { e1[k] = Tu[k][2]; e2[k] = Tu[k][3]; e3[4 * (n - 1) + k] = -Ts[k][2]; e4[4 * (n - 1) + k] = -Ts[k][3]; }
  R r = ((normInfV(A * F + (A * e1) * sym(hu) + (A * e2) * sym(hu) + (A * e3) * sym(hs) + (A * e4) * sym(hs))) * 4).rightBound();
  R rmin = S.q("rmin").rightBound(); if (r < rmin) r = rmin; MpInterval R1(r), sq2 = sqrt(MpInterval(2));
  if (!((nrm2(ub) + sq2 * R1).rightBound() <= dsu.leftBound() && (nrm2(sb) + sq2 * R1).rightBound() <= dss.leftBound())) { std::printf("RESULT l4bvp2 FAIL reach (|u|, |s| + sqrt2 r > deltastar)\n"); return 3; }
  std::printf("BALL r %s hu %s hs %s |u| %s |s| %s\n", bnd(r, true).c_str(), bnd(hu.rightBound(), true).c_str(), bnd(hs.rightBound(), true).c_str(), bnd(nrm2(ub).rightBound(), true).c_str(), bnd(nrm2(sb).rightBound(), true).c_str());
  std::vector<Pass> bl(n);
  { IV uu(2); uu[0] = ub[0] + sym(R1); uu[1] = ub[1] + sym(R1); MpInterval hb = Lu * (nrm2(ub) + sq2 * R1);
    IV W = L + col(Tu, 0) * uu[0] + col(Tu, 1) * uu[1]; for (int k = 0; k < 4; ++k) W[k] += sym((mag(Tu[k][2]) + mag(Tu[k][3])) * hb);
    bl[0] = pass(f, ext(W, Tg * cf[0], sym(R1)), true, "l4b_ball0"); }
  for (int i = 1; i < n; ++i) { IV Bx(4); for (int k = 0; k < 4; ++k) Bx[k] = xs[i][k] + sym(R1); bl[i] = pass(f, ext(Bx, Tg * cf[i], sym(R1)), true, "l4b_ball" + std::to_string(i)); }
  IM Dz0(4, 4); for (int a = 0; a < 4; ++a) for (int b = 0; b < 4; ++b) Dz0[a][b] = bl[0].D[a][b];
  IV E1(D), E2(D), E3(D), E4(D); IV q1 = Dz0 * col(Tu, 2), q2 = Dz0 * col(Tu, 3);
  for (int k = 0; k < 4; ++k) { E1[k] = q1[k]; E2[k] = q2[k]; E3[4 * (n - 1) + k] = -Ts[k][2]; E4[4 * (n - 1) + k] = -Ts[k][3]; }
  IM DF(D, D); const int cs = 2 + 4 * (n - 1);                   // columns: u 0,1 ; x_i at 2 + 4(i-1) ; s at cs, cs+1 ; alpha D-1
  for (int i = 0; i < n; ++i) {
    IM Dz(4, 4); for (int a = 0; a < 4; ++a) for (int b = 0; b < 4; ++b) Dz[a][b] = bl[i].D[a][b];
    if (i == 0) { IV c0 = Dz * col(Tu, 0), c1 = Dz * col(Tu, 1); for (int a = 0; a < 4; ++a) { DF[a][0] = c0[a]; DF[a][1] = c1[a]; } }
    else for (int a = 0; a < 4; ++a) for (int b = 0; b < 4; ++b) DF[4 * i + a][2 + 4 * (i - 1) + b] = Dz[a][b];
    if (i < n - 1) for (int a = 0; a < 4; ++a) DF[4 * i + a][2 + 4 * i + a] = -1;
    else for (int a = 0; a < 4; ++a) { DF[4 * i + a][cs] = -Ts[a][0]; DF[4 * i + a][cs + 1] = -Ts[a][1]; }
    for (int a = 0; a < 4; ++a) DF[4 * i + a][D - 1] = bl[i].D[a][4];
  }
  for (int b = 0; b < 4; ++b) DF[D - 1][2 + 4 * (kk - 1) + b] = gph[b];
  IM ID(D, D); for (int i = 0; i < D; ++i) ID[i][i] = 1;
  IV AE1 = A * E1, AE2 = A * E2, AE3 = A * E3, AE4 = A * E4;
  IV YV = A * F + AE1 * sym(hu) + AE2 * sym(hu) + AE3 * sym(hs) + AE4 * sym(hs);
  IM AM = A * DF;
  for (int a = 0; a < D; ++a) for (int j = 0; j < 2; ++j) { AM[a][j] += AE1[a] * sym(Lu) + AE2[a] * sym(Lu); AM[a][cs + j] += AE3[a] * sym(Ls) + AE4[a] * sym(Ls); }
  MpInterval Y = normInfV(YV), Z = normInf(ID - AM), v = Z * R1 - R1 + Y;
  bool ok = Z.rightBound() < 1 && v.rightBound() < 0;
  std::printf("KRAWCZYK Y %s Z %s r %s  Zr - r + Y <= %s\n", bnd(Y.rightBound(), true).c_str(), bnd(Z.rightBound(), true).c_str(), bnd(r, true).c_str(), bnd(v.rightBound(), true).c_str());
  bool meets = false;
  { MpInterval tsh = S.q("tshift"); IV pb(4); for (int k = 0; k < 4; ++k) pb[k] = S.q("pbar", k);
    IV Bx(4); for (int k = 0; k < 4; ++k) Bx[k] = xs[kk][k] + sym(R1);
    capd::MpIMap g(l4_vf, 6, 6, 2); g.setParameter(0, MU); g.setParameter(1, MpInterval(tsh.leftBound() >= 0 ? 1 : -1));
    Pass sh = pass(g, ext(Bx, mag(tsh), MpInterval(0)), false, "ckmj_shift");
    MpInterval d2(0); for (int k = 0; k < 4; ++k) { MpInterval d = sh.P[k] - pb[k]; d2 += d * d; }
    MpInterval dist = sqrt(MpInterval(d2.rightBound()));
    meets = dist.rightBound() <= Q("1.66e-9").leftBound();
    std::printf("CKMJ distance from p-bar to the certified orbit point: <= %s (CKMJ r = 1.659e-9) -> %s\n", bnd(dist.rightBound(), true).c_str(), meets ? "MEETS" : "does not meet"); }
  std::printf("RESULT l4bvp krawczyk %s ckmj %s\n", ok ? "CERTIFIED" : "FAIL", meets ? "MEETS" : "NO");
  return ok && meets ? 0 : 3;
}

int main(int argc, char** argv) {
  try {
    T0 = now();
    if (argc < 3) { std::cerr << "usage: s2_l4 cone|bvp spec\n"; return 2; }
    Spec S = readspec(argv[2]);
    R::setDefaultPrecision(S.has("prec") ? S.n("prec") : 128); if (S.has("order")) ORDER = S.n("order"); if (S.has("tol")) TOL = std::stod(S.v("tol")[0]);
    MU = Q("1/2");
    std::printf("RUN l4 %s spec %s prec %d order %d tol %.1e\n", argv[1], argv[2], (int)R::getDefaultPrecision(), ORDER, TOL); std::fflush(stdout);
    std::string mode = argv[1]; int rc = mode == "cone" ? run_cone(S) : mode == "bvp" ? run_bvp(S) : mode == "bvp2" ? run_bvp2(S) : 2;
    std::printf("END rc %d total wall %.1f s\n", rc, now() - T0); return rc;
  } catch (std::exception& e) { std::printf("FAIL %s\n", e.what()); return 1; }
}
