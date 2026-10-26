// so_thin_probe.cpp -- DIAGNOSTIC (the Bridge's point 2 for the SO swing-1 throw; no verdicts, no set). The W0 = 0 centre
// orbit (the lift at r = 0, propagated by the C0 solver as a tripleton set, as b17_check's reference runs do; the probe
// point is the mid point of its enclosure at t_k; a diagnostic centre) is probed at given
// times t_k with the THIN Cn (degree 2) call alone, at the SO run's step h_k, in four variants:
//   single call (order 20); 2 x h/2 and 4 x h/4 composed by the interval chain rule (value by the mean-value form over the
//   previous value enclosure, D1 and D2 composed exactly); single call at order 25.
// Reported per variant: width of the value enclosure, max radius of D1 and of D2 (full second derivatives), and the width
// of the step enclosure enc. For the composed variants D1/D2 of each substep come from the call over the previous value
// box (x = xx = box), which is what a composed thin call in so::step would use.
// Usage: so_thin_probe t1:h1 t2:h2 ...   (times increasing, > 0)   -- NEIGHBOURING-orbit mode (C0 centre)
//        so_thin_probe --state <mn_so state file> [t_next_checkpoint]   -- EXACT mode (the Bridge, 2026-10-26): the SO
//        set's own thin centre X.x; the step h chosen exactly as so::step does (hull call on X.hull() with step control,
//        primed by adjustTimeStep(LAST_H), max step clamped to the next checkpoint); then the thin call at that h and the
//        variants. Also reports the hull call's encK width and the radii of its D1K / D2K.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include "so_set.h"
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
using so::RepA;
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepA::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepA::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
// width taken about the mid point, so it is not floored by rounding each endpoint to double separately (the first
// version printed the double floor, ~2^-53 |v|, instead of the 128-bit width)
static double w(const MpInterval& v) { MpInterval d = v - v.mid(); return so::hi(d) - so::lo(d); }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
#include "../gen/mn_field8.h"
static MpInterval MNC[5];
void mn8_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn8_field<Node>(in, o, c); }
void lift_vf(Node, Node in[], int, Node o[], int, Node par[], int) {     // identical to mn_so's (gated)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c);
  Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1];
  Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c);
  o[0] = x; o[1] = zero; o[2] = px; o[3] = sqrt(rad); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i];
}
struct Res { double val = 0, d1 = 0, d2 = 0, enc = 0; bool nv = false; IM A; std::vector<IM> H; };   // nv: CAPD did not validate the fixed step
static IV midv(const IV& v) { IV m(v.dimension()); for (int i = 0; i < v.dimension(); ++i) m[i] = v[i].mid(); return m; }
// one Cn call at fixed step h over the box xx (x = mid of xx); returns value enclosure over xx (mean value), D1, D2 over xx
static void call(so::Solver& s, const IV& xx, double h, IV& val, IM& D1, std::vector<IM>& D2, double& encw) {
  const int n = xx.dimension(); so::JetT phi(n, 2), rem(n, 2), enc(n, 2);
  s.turnOffStepControl(); s.setStep(MpInterval(h));
  IV c = midv(xx);
  so::JetT phc(n, 2), rmc(n, 2), enc2(n, 2);
  IV yc = s.encloseCnMap(MpInterval(0), c, c, phc, rmc, enc2);     // centre value
  if (so::md(s.getStep()) != h) throw std::runtime_error("NOT VALIDATED");
  s.encloseCnMap(MpInterval(0), xx, xx, phi, rem, enc);            // derivatives over the box
  D1 = IM(n, n); D2.assign(n, IM(n, n)); encw = 0;
  for (int i = 0; i < n; ++i) { encw = std::max(encw, w(enc(i)));
    for (int j = 0; j < n; ++j) { D1[i][j] = phi(i, j) + rem(i, j); for (int k = 0; k < n; ++k) D2[i][j][k] = so::d2(phi, i, j, k) + so::d2(rem, i, j, k); } }
  val = IV(n); IV dx = xx - c;
  for (int i = 0; i < n; ++i) { val[i] = yc[i] + rmc(i); for (int j = 0; j < n; ++j) val[i] += D1[i][j] * dx[j]; }
}
static Res probe(so::Solver& s, const IV& p, double h, int m) {
  const int n = p.dimension(); IV v = p; IM A(n, n); A.setToIdentity(); std::vector<IM> H(n, IM(n, n)); Res r;
  for (int sub = 0; sub < m; ++sub) {
    IV val; IM D1; std::vector<IM> D2; double encw;
    try { call(s, v, h / m, val, D1, D2, encw); } catch (std::exception& e) { r.nv = true; return r; }
    r.enc = std::max(r.enc, encw);
    std::vector<IM> Hn(n, IM(n, n));
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) for (int k = 0; k < n; ++k) {
      MpInterval acc(0); for (int l = 0; l < n; ++l) { acc += D1[i][l] * H[l][j][k]; for (int q = 0; q < n; ++q) acc += D2[i][l][q] * A[l][j] * A[q][k]; }
      Hn[i][j][k] = acc; }
    A = D1 * A; H = Hn; v = val;
  }
  r.A = A; r.H = H;
  for (int i = 0; i < n; ++i) { r.val = std::max(r.val, w(v[i]));
    for (int j = 0; j < n; ++j) { r.d1 = std::max(r.d1, w(A[i][j]) / 2); for (int k = 0; k < n; ++k) r.d2 = std::max(r.d2, w(H[i][j][k]) / 2); } }
  return r;
}
static MpInterval unhx(std::istream& in) { std::string a, b; in >> a >> b; R lo, hi;      // copied from mn_common.h
  if (mpfr_set_str(lo.*RepA::rep, a.c_str(), 0, MPFR_RNDN) || mpfr_set_str(hi.*RepA::rep, b.c_str(), 0, MPFR_RNDN)) throw std::runtime_error("state: bad hex");
  return MpInterval(lo, hi); }
static bool load_state(const char* path, so::Set& X, MpInterval& last_h) {                // the same format as mn_common.h load()
  std::ifstream in(path); if (!in) return false; long steps; size_t ncp;
  in >> steps >> ncp; X.t = unhx(in); last_h = unhx(in);
  for (int i = 0; i < 8; ++i) X.x[i] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) X.C[i][a] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) X.H[i][a][b] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) X.B[i][j] = unhx(in);
  for (int i = 0; i < 8; ++i) X.re[i] = unhx(in);
  std::string end; in >> end; if (end != "END") throw std::runtime_error("state: truncated file");
  return true;
}
int main(int argc, char** argv) {
  R::setDefaultPrecision(128);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  if (argc > 2 && std::string(argv[1]) == "--state") {
    so::Set X(8); MpInterval lh; if (!load_state(argv[2], X, lh)) { std::printf("cannot read %s\n", argv[2]); return 1; }
    double tnext = argc > 3 ? std::stod(argv[3]) : 1e300;
    capd::MpIMap fK(mn8_vf, 8, 8, 5, 2), fT(mn8_vf, 8, 8, 5, 2), f25(mn8_vf, 8, 8, 5, 2);
    for (int i = 0; i < 5; ++i) { fK.setParameter(i, MNC[i]); fT.setParameter(i, MNC[i]); f25.setParameter(i, MNC[i]); }
    so::Solver solK(fK, 20), solT(fT, 20), s25(f25, 25);
    if (so::md(lh) > 0) solK.adjustTimeStep(lh);
    solK.setMaxStep(MpInterval(tnext - so::md(X.t) > 0 ? tnext - so::md(X.t) : 1e300));
    IV K = X.hull(); so::JetT pK(8, 2), rK(8, 2), eK(8, 2);
    std::printf("# hull K per component [lo, hi]:"); for (int i = 0; i < 8; ++i) std::printf(" [%.4g, %.4g]", so::lo(K[i]), so::hi(K[i])); std::printf("\n"); std::fflush(stdout);
    solK.turnOnStepControl(); solK.encloseCnMap(X.t, K, K, pK, rK, eK); double h = so::md(solK.getStep());
    double ew = 0, d1K = 0, d2K = 0, Kw = 0;
    for (int i = 0; i < 8; ++i) { ew = std::max(ew, w(eK(i))); Kw = std::max(Kw, w(K[i]));
      for (int j = 0; j < 8; ++j) { d1K = std::max(d1K, w(pK(i, j) + rK(i, j)) / 2); for (int k = 0; k < 8; ++k) d2K = std::max(d2K, w(so::d2(pK, i, j, k) + so::d2(rK, i, j, k)) / 2); } }
    std::printf("# EXACT mode: %s  t=%.6f LAST_H=%.4e -> hull-chosen h=%.4e | hull K width %.3e | hull call: encK %.3e  rad D1K %.3e  rad D2K %.3e\n",
                argv[2], so::md(X.t), so::md(lh), h, Kw, ew, d1K, d2K);
    IV x = X.x;
    Res r[4] = {probe(solT, x, h, 1), probe(solT, x, h, 2), probe(solT, x, h, 4), probe(s25, x, h, 1)};
    const char* nm[4] = {"single (order 20)", "2 x h/2", "4 x h/4", "single (order 25)"};
    std::printf("  THIN call from X.x:\n");
    for (int k = 0; k < 4; ++k) { if (r[k].nv) std::printf("  %-18s step NOT VALIDATED by CAPD\n", nm[k]);
      else std::printf("  %-18s val_w %.3e  rad D1 %.3e  rad D2 %.3e  enc_w %.3e\n", nm[k], r[k].val, r[k].d1, r[k].d2, r[k].enc); }
    // the Bridge's discriminator: the HULL call over K at h, 2 x h/2, 4 x h/4 (composed over the value boxes), and the
    // resulting box2 (1/2 (hK - mid)[r, r], hK = D2K[DxR, DxR] + D1K H) and dD.e ((D1K - D1c) e) per unit time
    so::Solver solK2(fK, 20); if (so::md(lh) > 0) solK2.adjustTimeStep(lh);
    IM DxR(8, 2); for (int j = 0; j < 8; ++j) for (int a = 0; a < 2; ++a) DxR[j][a] = X.C[j][a] + X.H[j][a][0] * so::sym(1) + X.H[j][a][1] * so::sym(1);
    IV e = X.B * X.re;
    std::printf("  HULL call over K:\n");
    for (int m : {1, 2, 4}) {
      Res q = probe(solK2, K, h, m); if (q.nv) { std::printf("  %d x h/%d: step NOT VALIDATED\n", m, m); continue; }
      Res tc = probe(solT, x, h, m);
      double b2 = 0, dde = 0;
      for (int i = 0; i < 8; ++i) {
        MpInterval qq(0);
        for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) { MpInterval hk(0);
          for (int j = 0; j < 8; ++j) { hk += q.A[i][j] * X.H[j][a][b]; for (int k = 0; k < 8; ++k) hk += q.H[i][j][k] * DxR[j][a] * DxR[k][b]; }
          qq += (hk - hk.mid()) * so::Set::rr(a, b); }
        b2 = std::max(b2, w(qq / 2));
        if (!tc.nv) { MpInterval de(0); for (int j = 0; j < 8; ++j) de += (q.A[i][j] - tc.A[i][j]) * e[j]; dde = std::max(dde, w(de)); }
      }
      if (tc.nv) std::printf("  %d x h/%d: encK %.3e  rad D1K %.3e  rad D2K %.3e | box2 %.3e (%.3e per unit t)  dD.e NOT COMPUTED (the thin comparison call at this step was NOT VALIDATED)\n", m, m, q.enc, q.d1, q.d2, b2, b2 / h);
      else std::printf("  %d x h/%d: encK %.3e  rad D1K %.3e  rad D2K %.3e | box2 %.3e (%.3e per unit t)  dD.e %.3e (%.3e per unit t)\n", m, m, q.enc, q.d1, q.d2, b2, b2 / h, dde, dde / h);
    }
    // the Bridge's split (2026-10-26): for the single hull call at h, D2K = Taylor part (phiK, degree 2) + remainder part
    // (remK, degree 2); box2 computed from each part alone (with the D1K of the same part), and the Lohner pivot order
    for (double hf : {1.0, 0.5}) {
      so::Solver sk(fK, 20); if (so::md(lh) > 0) sk.adjustTimeStep(lh); sk.turnOffStepControl(); sk.setStep(MpInterval(h * hf));
      so::JetT ph(8, 2), rm(8, 2), en(8, 2);
      try { sk.encloseCnMap(X.t, K, K, ph, rm, en); if (so::md(sk.getStep()) != h * hf) throw std::runtime_error("nv"); }
      catch (std::exception&) { std::printf("  split at %.2f h: NOT VALIDATED\n", hf); continue; }
      double rP = 0, rR = 0, bP = 0, bR = 0;
      for (int i = 0; i < 8; ++i) {
        MpInterval qP(0), qR(0);
        for (int a2 = 0; a2 < 2; ++a2) for (int b2 = 0; b2 < 2; ++b2) { MpInterval hP(0), hR(0);
          for (int j = 0; j < 8; ++j) { hP += ph(i, j) * X.H[j][a2][b2]; hR += rm(i, j) * X.H[j][a2][b2];
            for (int k = 0; k < 8; ++k) { MpInterval dP = so::d2(ph, i, j, k), dR = so::d2(rm, i, j, k);
              rP = std::max(rP, w(dP) / 2); rR = std::max(rR, w(dR) / 2); hP += dP * DxR[j][a2] * DxR[k][b2]; hR += dR * DxR[j][a2] * DxR[k][b2]; } }
          qP += (hP - hP.mid()) * so::Set::rr(a2, b2); qR += (hR - hR.mid()) * so::Set::rr(a2, b2); }
        bP = std::max(bP, w(qP / 2)); bR = std::max(bR, w(qR / 2));
      }
      std::printf("  split at %.2f h: rad D2 Taylor(phiK) %.3e  remainder(remK) %.3e | box2 from Taylor %.3e  from remainder %.3e\n", hf, rP, rR, bP, bR);
    }
    { so::JetT pt(8, 2), rt(8, 2), et(8, 2); so::Solver st(fT, 20); st.turnOffStepControl(); st.setStep(MpInterval(h));   // Lohner pivot order
      try { st.encloseCnMap(X.t, x, x, pt, rt, et); IM D1c(8, 8); for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) D1c[i][j] = pt(i, j) + rt(i, j);
        IM AB = D1c * X.B; std::vector<std::pair<double, int>> ord;
        for (int j = 0; j < 8; ++j) { double nn = 0; for (int i = 0; i < 8; ++i) nn += so::md(AB[i][j]) * so::md(AB[i][j]); ord.push_back({-std::sqrt(nn) * (so::hi(X.re[j]) - so::lo(X.re[j])) / 2, j}); }
        std::sort(ord.begin(), ord.end()); std::printf("  Lohner pivot order (|A col| rad re):"); for (auto& o : ord) std::printf(" %d(%.1e)", o.second, -o.first); std::printf("\n"); }
      catch (std::exception&) { std::printf("  pivot order: thin call not validated\n"); } }
    // how far h sits below the largest fixed step the hull call validates (coarse: factors 1.25, 1.5, 2, 3)
    double kmax = 1; for (double f : {1.25, 1.5, 2.0, 3.0}) { so::Solver sv(fK, 20); so::JetT a1(8, 2), a2(8, 2), a3(8, 2);
      try { sv.turnOffStepControl(); sv.setStep(MpInterval(h * f)); sv.encloseCnMap(X.t, K, K, a1, a2, a3); if (so::md(sv.getStep()) == h * f) kmax = f; else break; } catch (std::exception&) { break; } }
    std::printf("  largest validated fixed step tested: %.2f x h  (h / h_max_tested >= %.2f)\n", kmax, 1 / kmax);
    return 0;
  }
  capd::MpIMap L(lift_vf, 2, 8, 8, 3); for (int i = 0; i < 5; ++i) L.setParameter(i, MNC[i]);
  L.setParameter(5, Q("36419361737/10000000000")); L.setParameter(6, Q("60360992808/10000000000")); L.setParameter(7, Q("0"));
  IV r0(2); capd::diffAlgebra::Jet<IM, 0> j0(8, 2, 3); L(r0, j0);
  IV x(8); for (int i = 0; i < 8; ++i) x[i] = j0(i);
  capd::MpIMap f0(mn8_vf, 8, 8, 5), f20(mn8_vf, 8, 8, 5, 2), f25(mn8_vf, 8, 8, 5, 2);
  for (int i = 0; i < 5; ++i) { f0.setParameter(i, MNC[i]); f20.setParameter(i, MNC[i]); f25.setParameter(i, MNC[i]); }
  capd::MpIOdeSolver s0(f0, 20); capd::MpITimeMap tm(s0); capd::MpC0TripletonSet S0(x);
  so::Solver s20(f20, 20), s25(f25, 25);
  std::printf("# so_thin_probe: W0 = 0 centre orbit; thin Cn calls at the SO run's h. columns per variant: val_w D1_rad D2_rad enc_w\n");
  std::printf("%9s %9s | %-41s | %-41s | %-41s | %-41s\n", "t", "h", "single (order 20)", "2 x h/2", "4 x h/4", "single (order 25)");
  double t = 0;
  for (int a = 1; a < argc; ++a) {
    std::string s = argv[a]; double tk = std::stod(s.substr(0, s.find(':'))), hk = std::stod(s.substr(s.find(':') + 1));
    tm(MpInterval(tk), S0); IV y = IV(S0); double ymax = 0; for (int i = 0; i < 8; ++i) ymax = std::max(ymax, w(y[i]));
    x = midv(y); t = tk;
    Res r[4] = {probe(s20, x, hk, 1), probe(s20, x, hk, 2), probe(s20, x, hk, 4), probe(s25, x, hk, 1)};
    std::printf("%9.4f %9.3e |", tk, hk);
    for (auto& q : r) { if (q.nv) std::printf(" %-39s |", "  step NOT VALIDATED by CAPD"); else std::printf(" %9.2e %9.2e %9.2e %9.2e |", q.val, q.d1, q.d2, q.enc); }
    std::printf("  (centre enclosure width %.1e)\n", ymax);
    std::fflush(stdout);
  }
}
