// so_section.h -- DIAGNOSTIC STAGE: the image of a second-order set on a section Sigma, by the composed-map statement
// with the Poincare map P in place of phi_h (the Bridge's review, 2026-10-24):
//   Psi(r) = P(x(r)),  x(r) = x + C r + 1/2 H(r, r),
//   Psi(0) = P(x),  DPsi(0) = DP(x) C,  D2Psi(0) = D2P(x)[C, C] + DP(x) H,
//   [D2Psi(R0)] c [D2P(K)][Dx(R0), Dx(R0)] + [DP(K)] H,   Dx(R0) = C + H(R0, .),
//   Psi(r) in Psi(0) + DPsi(0) r + 1/2 [D2Psi(R0)][r, r];   P(x(r) + e) - P(x(r)) in [DP(K)] e   (final leg: boxed)
// P's jets come from CAPD's Cn Poincare map: pm(set, jet, rt) gives the FLOW's jet at the return time, and
// pm.computeDP(jet) "recomputes Taylor expansion of the flow into Taylor expansion of Poincare map" (BasicPoincareMap.h).
// Thin call: CnRect2Set at the thin centre x. Hull call: CnRect2Set initialised with the box K = hull of the WHOLE set.
// Negative-control hooks: SEC_NO_DP (use the flow jets without computeDP), SEC_HULL_AT_CENTRE (hull call at the centre).
#pragma once
#include "so_set.h"
namespace so {
typedef capd::MpCnRect2Set SoCnSet;
typedef SoCnSet::JetType SoPJet;
static bool SEC_NO_DP = false, SEC_HULL_AT_CENTRE = false;

struct SectionImage {                 // the image as a second-order polynomial set on Sigma plus a box, and diagnostics
  int n = 0; IV x; IM C; std::vector<IM> H; IV box; MpInterval rtT, rtK; IV crossEnc;
  std::vector<MpInterval> D2PsiR0;    // [D2Psi(R0)](i, a, b), row-major (for the corner test)
  MpInterval project(const IV& nv, int sub = 8) const {
    MpInterval cx(0); for (int i = 0; i < n; ++i) cx += nv[i] * x[i];
    MpInterval z0(0), l[2] = {z0, z0}, M[2][2] = {{z0, z0}, {z0, z0}};
    for (int i = 0; i < n; ++i) for (int a = 0; a < 2; ++a) { l[a] += nv[i] * C[i][a]; for (int b = 0; b < 2; ++b) M[a][b] += nv[i] * H[i][a][b]; }
    MpInterval poly; bool first = true;
    for (int p = 0; p < sub; ++p) for (int q = 0; q < sub; ++q) {
      MpInterval r1(-1 + 2.0 * p / sub, -1 + 2.0 * (p + 1) / sub), r2(-1 + 2.0 * q / sub, -1 + 2.0 * (q + 1) / sub);
      MpInterval v = l[0] * r1 + l[1] * r2 + (M[0][0] * sqr(r1) + 2 * M[0][1] * r1 * r2 + M[1][1] * sqr(r2)) / 2;
      poly = first ? v : intervalHull(poly, v); first = false;
    }
    MpInterval e(0); for (int i = 0; i < n; ++i) e += nv[i] * box[i];
    return cx + poly + e;
  }
  // pointwise value at a given r (for containment tests): x + C r + 1/2 H(r, r) + box
  IV at(const MpInterval& r1, const MpInterval& r2) const {
    IV v(n); for (int i = 0; i < n; ++i) v[i] = x[i] + C[i][0] * r1 + C[i][1] * r2 + (H[i][0][0] * sqr(r1) + 2 * H[i][0][1] * r1 * r2 + H[i][1][1] * sqr(r2)) / 2 + box[i];
    return v;
  }
};

// P jets (value, first and FULL second derivatives) over an initial set given as a box (thin or hull)
template <class PM>
inline void p_jets(PM& pm, const IV& start, const MpInterval& t0, IV& val, IM& D1, std::vector<IM>& D2, MpInterval& rt) {
  int n = (int)start.dimension();
  SoCnSet s(start, 2); s.setCurrentTime(t0);
  SoPJet jet(n, 2);
  IV Px = pm(s, jet, rt);
  SoPJet jp = SEC_NO_DP ? jet : pm.computeDP(jet);
  val = Px; D1 = IM(n, n); D2.assign(n, IM(n, n));
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
    D1[i][j] = jp(i, j);
    for (int k = 0; k < n; ++k) { int a = std::min(j, k), b = std::max(j, k); MpInterval c = jp(i, a, b); D2[i][j][k] = a == b ? c * SO_DIAG_FACTOR : c * SO_OFFDIAG_FACTOR; }
  }
}

template <class PM>
inline SectionImage section_image(PM& pm, const Set& X) {
  const int n = X.n; SectionImage S; S.n = n;
  IV K = X.hull();
  IV vT, vK; IM D1T, D1K; std::vector<IM> D2T, D2K;
  p_jets(pm, X.x, X.t, vT, D1T, D2T, S.rtT);
  p_jets(pm, SEC_HULL_AT_CENTRE ? X.x : K, X.t, vK, D1K, D2K, S.rtK);
  S.crossEnc = vK;
  S.x = IV(n); S.C = IM(n, 2); S.H.assign(n, IM(2, 2)); S.box = IV(n);
  for (int i = 0; i < n; ++i) { S.x[i] = vT[i].mid(); S.box[i] += vT[i] - S.x[i]; }
  IM Cc = D1T * X.C;
  for (int i = 0; i < n; ++i) for (int a = 0; a < 2; ++a) { S.C[i][a] = Cc[i][a].mid(); S.box[i] += (Cc[i][a] - S.C[i][a]) * sym(1); }
  IM DxR(n, 2);
  for (int j = 0; j < n; ++j) for (int a = 0; a < 2; ++a) DxR[j][a] = X.C[j][a] + X.H[j][a][0] * sym(1) + X.H[j][a][1] * sym(1);
  for (int i = 0; i < n; ++i) {
    MpInterval hc[2][2], hK[2][2];
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) {
      hc[a][b] = MpInterval(0); hK[a][b] = MpInterval(0);
      for (int j = 0; j < n; ++j) { hc[a][b] += D1T[i][j] * X.H[j][a][b]; hK[a][b] += D1K[i][j] * X.H[j][a][b];
        for (int k = 0; k < n; ++k) { hc[a][b] += D2T[i][j][k] * X.C[j][a] * X.C[k][b]; hK[a][b] += D2K[i][j][k] * DxR[j][a] * DxR[k][b]; } }
    }
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) S.D2PsiR0.push_back(hK[a][b]);
    MpInterval m01 = ((hc[0][1] + hc[1][0]) / 2).mid();
    S.H[i][0][0] = hc[0][0].mid(); S.H[i][1][1] = hc[1][1].mid(); S.H[i][0][1] = m01; S.H[i][1][0] = m01;
    MpInterval q(0);
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) q += (hK[a][b] - S.H[i][a][b]) * Set::rr(a, b);
    S.box[i] += q / 2;
  }
  IV e = X.B * X.re;                                   // final leg: [DP(K)] e, boxed
  S.box += D1K * e;
  return S;
}
}  // namespace so
