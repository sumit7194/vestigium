// so_set.h -- DIAGNOSTIC STAGE (SECOND_ORDER_STEP_DESIGN.md, P1'/P2' with the Bridge's composed-map statement):
// a second-order set  X = { x + C r + 1/2 H(r, r) + B re : r in R0 = [-1,1]^2 }  propagated by one CAPD Cn (degree 2)
// call over the hull (P2', x = xx = K) and one over the thin centre (P1', same step h), with the chain-rule contraction
//   Psi(r) = phi(x(r)),  DPsi(0) = Dphi(x) C,  D2Psi(0) = D2phi(x)[C, C] + Dphi(x) H,
//   [D2Psi(R0)] c [D2phi(K)][Dx(R0), Dx(R0)] + [Dphi(K)] H,   Dx(R0) = C + H(R0, .),
//   Psi(r) in Psi(0) + DPsi(0) r + 1/2 [D2Psi(R0)][r, r]                  (integral remainder on convex R0)
//   phi(x(r) + e) - phi(x(r)) in [Dphi(K)] e  = Dphi(x) e  (Lohner frame)  + ([Dphi(K)] - Dphi(x)) e  (box)
// Step rule (the Bridge): h is chosen by CAPD on the hull call; the thin call is made at the SAME fixed h; if either
// fails to validate, h is halved and BOTH are redone (counter SO_RESTEPS); never a mixed step, never a silent fallback.
// The second-order jet convention is a parameter (SO_JET_FULL = true: coefficient(i,j,k) is the full second derivative
// for j != k and HALF of it for j == k, i.e. Taylor coefficients); the toys pin it, the negative control flips it.
#pragma once
#include <cmath>
#include <stdexcept>
#include <vector>
#include <algorithm>
#include <string>

namespace so {
using capd::MpInterval; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
struct RepA : capd::multiPrec::MpReal { static constexpr auto rep = &RepA::mpfr_rep; };
inline double lo(const MpInterval& v) { return mpfr_get_d(v.leftBound().*RepA::rep, MPFR_RNDD); }
inline double hi(const MpInterval& v) { return mpfr_get_d(v.rightBound().*RepA::rep, MPFR_RNDU); }
inline double md(const MpInterval& v) { return mpfr_get_d(v.mid().leftBound().*RepA::rep, MPFR_RNDN); }
typedef capd::MpICnOdeSolver Solver;
typedef capd::diffAlgebra::Jet<IM, 0> JetT;

static long SO_RESTEPS = 0;
static double SO_OFFDIAG_FACTOR = 1.0;        // multiplier applied to off-diagonal second-order coefficients (1 = CAPD as is)
static double SO_DIAG_FACTOR = 2.0;           // multiplier applied to diagonal coefficients to get full d2f/dx_j^2

inline MpInterval sym(double r) { return MpInterval(-r, r); }

struct Set {
  int n = 0;                                  // state dimension; parameters m = 2
  IV x;                                       // thin centre
  IM C;                                       // n x 2, point
  std::vector<IM> H;                          // n matrices 2 x 2, symmetric, point: d2 x_i / dr_a dr_b
  IM B; IV re;                                // error part  e in B re
  MpInterval t;
  Set() {}
  explicit Set(int n_) : n(n_), x(n_), C(n_, 2), H(n_, IM(2, 2)), B(n_, n_), re(n_), t(0) { B.setToIdentity(); }
  // interval values of r_a r_b over R0 = [-1, 1]^2
  static MpInterval rr(int a, int b) { return a == b ? MpInterval(0, 1) : MpInterval(-1, 1); }
  IV quad() const {                           // 1/2 H(r, r) over R0, componentwise
    IV q(n);
    for (int i = 0; i < n; ++i) { MpInterval s(0); for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) s += H[i][a][b] * rr(a, b); q[i] = s / 2; }
    return q;
  }
  IV hull() const {                           // interval hull of the whole set (K)
    IV h = x; IV R(2); R[0] = sym(1); R[1] = sym(1);
    h += C * R; h += quad(); h += B * re; return h;
  }
  // tighter projection of the set on a covector nv: sub-boxes of R0 for the polynomial part (diagnostics)
  MpInterval project(const IV& nv, int sub = 8) const {
    MpInterval cx(0); for (int i = 0; i < n; ++i) cx += nv[i] * x[i];
    MpInterval z0(0), l[2] = {z0, z0}, M[2][2] = {{z0, z0}, {z0, z0}};
    for (int i = 0; i < n; ++i) { for (int a = 0; a < 2; ++a) { l[a] += nv[i] * C[i][a]; for (int b = 0; b < 2; ++b) M[a][b] += nv[i] * H[i][a][b]; } }
    MpInterval poly; bool first = true;
    for (int p = 0; p < sub; ++p) for (int q = 0; q < sub; ++q) {
      MpInterval r1(-1 + 2.0 * p / sub, -1 + 2.0 * (p + 1) / sub), r2(-1 + 2.0 * q / sub, -1 + 2.0 * (q + 1) / sub);
      MpInterval v = l[0] * r1 + l[1] * r2 + (M[0][0] * sqr(r1) + 2 * M[0][1] * r1 * r2 + M[1][1] * sqr(r2)) / 2;
      poly = first ? v : intervalHull(poly, v); first = false;
    }
    IV nB = transpose(B) * nv; MpInterval e(0); for (int j = 0; j < n; ++j) e += nB[j] * re[j];
    return cx + poly + e;
  }
};

// full second derivative from a degree-2 jet, with the convention multipliers
inline MpInterval d2(const JetT& J, int i, int j, int k) {
  int a = std::min(j, k), b = std::max(j, k);
  MpInterval c = J(i, a, b);
  return a == b ? c * SO_DIAG_FACTOR : c * SO_OFFDIAG_FACTOR;
}

// Gram-Schmidt of mid(A) as a point matrix: the Lohner frame. Columns are ordered by |A_col j| * rad(re_j) (Lohner's
// pivot; the Bridge's review), and a column is dropped only if it is negligible RELATIVE to the largest column norm.
inline IM qr_frame(const IM& A, const IV& re) {
  int n = (int)A.numberOfRows(); std::vector<std::pair<double, std::vector<double>>> cols; std::vector<std::vector<double>> P;
  double nmax = 0;
  for (int j = 0; j < n; ++j) { std::vector<double> c(n); double nn = 0; for (int i = 0; i < n; ++i) { c[i] = md(A[i][j]); nn += c[i] * c[i]; }
    nmax = std::max(nmax, std::sqrt(nn)); cols.push_back({std::sqrt(nn) * (hi(re[j]) - lo(re[j])) / 2, c}); }
  std::stable_sort(cols.begin(), cols.end(), [](const auto& u, const auto& v) { return u.first > v.first; });
  const double tol = 1e-12 * (nmax > 0 ? nmax : 1.0);
  auto add = [&](std::vector<double> v) {
    for (auto& p : P) { double d = 0; for (int i = 0; i < n; ++i) d += v[i] * p[i]; for (int i = 0; i < n; ++i) v[i] -= d * p[i]; }
    double nn = 0; for (double x : v) nn += x * x; nn = std::sqrt(nn); if (nn < tol || (int)P.size() == n) return;
    for (double& x : v) x /= nn; P.push_back(v);
  };
  for (auto& c : cols) add(c.second);
  for (int i = 0; i < n; ++i) { std::vector<double> e(n, 0.0); e[i] = nmax > 0 ? nmax : 1.0; add(e); }
  IM Q(n, n); for (int j = 0; j < n; ++j) for (int i = 0; i < n; ++i) Q[i][j] = MpInterval(P[j][i]);
  return Q;
}

struct StepLog { double h = 0, w_D2K_contrib = 0, maxE = 0; std::vector<MpInterval> hK; IV enc; };   // enc: C0 enclosure over the step from K   // hK: [D2Psi(R0)] (i, a, b) row-major
static double SO_REMAINDER_SCALE = 1.0;      // NEGATIVE-CONTROL hook only: scales the P2' remainder box (1 = correct)

// one step of the second-order set; solK and solT are two Cn (degree 2) solvers on the same vector field
inline StepLog step(Solver& solK, Solver& solT, Set& X, bool hull_X_with_H_spread = true) {
  const int n = X.n; StepLog lg;
  IV K = X.hull();
  JetT phiK(n, 2), remK(n, 2), encK(n, 2), phiT(n, 2), remT(n, 2), encT(n, 2);
  IV yT(n);
  double hfix = -1;
  for (int attempt = 0; ; ++attempt) {
    if (attempt > 40) throw std::runtime_error("so::step: could not validate both calls (step halved 40 times)");
    try {
      if (hfix < 0) { solK.turnOnStepControl(); }
      else { solK.turnOffStepControl(); solK.setStep(MpInterval(hfix)); }
      solK.encloseCnMap(X.t, K, K, phiK, remK, encK);
      double h = md(solK.getStep());
      if (hfix > 0 && h != hfix) throw std::runtime_error("so::step: hull call changed a fixed step (BUG)");
      solT.turnOffStepControl(); solT.setStep(solK.getStep());
      yT = solT.encloseCnMap(X.t, X.x, X.x, phiT, remT, encT);
      if (md(solT.getStep()) != h) throw std::runtime_error("so::step: thin call did not use the fixed step");   // -> halve, redo both
      hfix = h; break;
    } catch (std::exception& e) {
      if (std::string(e.what()).find("BUG") != std::string::npos) throw;
      ++SO_RESTEPS;
      hfix = (hfix < 0 ? md(solK.getStep()) : hfix) / 2;
    }
  }
  lg.h = hfix;
  lg.enc = IV(n); for (int i = 0; i < n; ++i) lg.enc[i] = encK(i);       // trajectories from the hull K over [t, t+h] (for S4/S9)
  // enclosures of the flow and its derivatives: phi + rem (CnRect2Set convention).
  // CAPD source (dynsys/CnOdeSolver_templateMembers.h, encloseCnMap): the RETURN value is the Taylor polynomial summed at
  //   the centre, WITHOUT the remainder:
  //     "VectorType v = this->getCoefficientsAtCenter()[this->getOrder()]; for(r = order-1..0) v = v*step + coeffAtCenter[r];
  //      ... return v;"   while the remainder is computed separately: "computeAndApproveRemainder(*this,t,xx,rem,enc);"
  //   and CnRect2Set::move adds them: "y += VectorType(result.rem());" and "Phi += Rem". So val = y + rem(i) (no double
  //   count). phi's order-0 coefficient is the same Taylor sum but with initial condition xx; for the thin call x = xx, so
  //   phiT(i) and yT coincide (checked in the toys: identical to print precision).
  IV val(n); IM D1c(n, n), D1K(n, n);
  for (int i = 0; i < n; ++i) {
    val[i] = yT[i] + remT(i);
    for (int j = 0; j < n; ++j) { D1c[i][j] = phiT(i, j) + remT(i, j); D1K[i][j] = phiK(i, j) + remK(i, j); }
  }
  auto D2c = [&](int i, int j, int k) { return d2(phiT, i, j, k) + d2(remT, i, j, k); };
  auto D2K = [&](int i, int j, int k) { return d2(phiK, i, j, k) + d2(remK, i, j, k); };
  IV s(n);                                                     // boxes accumulated into the error part
  // order 0
  IV xn(n); for (int i = 0; i < n; ++i) { xn[i] = val[i].mid(); s[i] += val[i] - xn[i]; }
  // order 1
  IM Cc = D1c * X.C, Cn(n, 2);
  for (int i = 0; i < n; ++i) for (int a = 0; a < 2; ++a) { Cn[i][a] = Cc[i][a].mid(); s[i] += (Cc[i][a] - Cn[i][a]) * sym(1); }
  // order 2 at the centre, and the hull second derivative of Psi
  IM DxR(n, 2);                                                // Dx(R0) = C + H(R0, .)
  for (int j = 0; j < n; ++j) for (int a = 0; a < 2; ++a)
    DxR[j][a] = hull_X_with_H_spread ? X.C[j][a] + X.H[j][a][0] * sym(1) + X.H[j][a][1] * sym(1) : X.C[j][a];
  std::vector<IM> Hn(n, IM(2, 2));
  double wmax = 0;
  for (int i = 0; i < n; ++i) {
    MpInterval hc[2][2], hK[2][2];
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) {
      hc[a][b] = MpInterval(0); hK[a][b] = MpInterval(0);
      for (int j = 0; j < n; ++j) { hc[a][b] += D1c[i][j] * X.H[j][a][b]; hK[a][b] += D1K[i][j] * X.H[j][a][b];
        for (int k = 0; k < n; ++k) { hc[a][b] += D2c(i, j, k) * X.C[j][a] * X.C[k][b]; hK[a][b] += D2K(i, j, k) * DxR[j][a] * DxR[k][b]; } }
    }
    // symmetrise the stored H' FIRST (the Bridge's review fix), then take every remainder delta against exactly it
    MpInterval m01 = ((hc[0][1] + hc[1][0]) / 2).mid();
    Hn[i][0][0] = hc[0][0].mid(); Hn[i][1][1] = hc[1][1].mid(); Hn[i][0][1] = m01; Hn[i][1][0] = m01;
    MpInterval q(0);
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) {
      MpInterval delta = hK[a][b] - Hn[i][a][b];               // [D2Psi(R0)](a, b) - H'(a, b), H' as stored
      q += delta * Set::rr(a, b);
      wmax = std::max(wmax, hi(delta) - lo(delta)); lg.hK.push_back(hK[a][b]);
    }
    s[i] += q / 2 * SO_REMAINDER_SCALE;
  }
  lg.w_D2K_contrib = wmax;
  // error part: D1c (B re) in the Lohner frame, ([Dphi(K)] - D1c) e boxed
  IV e = X.B * X.re;
  IM dD = D1K - D1c; s += dD * e;
  IM AB = D1c * X.B;
  IM Bn = qr_frame(AB, X.re);
  IM iBn = capd::matrixAlgorithms::krawczykInverse(Bn);
  IV ren = (iBn * AB) * X.re + iBn * s;
  X.x = xn; X.C = Cn; X.H = Hn; X.B = Bn; X.re = ren; X.t = X.t + solK.getStep();
  for (int i = 0; i < n; ++i) lg.maxE = std::max(lg.maxE, hi(ren[i]) - lo(ren[i]));
  return lg;
}
}  // namespace so
