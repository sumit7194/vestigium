// so_thin_probe.cpp -- DIAGNOSTIC (the Bridge's point 2 for the SO swing-1 throw; no verdicts, no set). The W0 = 0 centre
// orbit (the lift at r = 0, propagated by the same Cn solver with step control, re-centred at the mid point of each step's
// value, the last step clamped to land on t_k; a diagnostic centre, not an enclosure) is probed at given
// times t_k with the THIN Cn (degree 2) call alone, at the SO run's step h_k, in four variants:
//   single call (order 20); 2 x h/2 and 4 x h/4 composed by the interval chain rule (value by the mean-value form over the
//   previous value enclosure, D1 and D2 composed exactly); single call at order 25.
// Reported per variant: width of the value enclosure, max radius of D1 and of D2 (full second derivatives), and the width
// of the step enclosure enc. For the composed variants D1/D2 of each substep come from the call over the previous value
// box (x = xx = box), which is what a composed thin call in so::step would use.
// Usage: so_thin_probe t1:h1 t2:h2 ...   (times increasing, > 0)
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <cstdlib>
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
void lift_vf(Node, Node in[], int, Node o[], int, Node par[], int) {     // identical to mn_so's (gated)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c);
  Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1];
  Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c);
  o[0] = x; o[1] = zero; o[2] = px; o[3] = sqrt(rad); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i];
}
struct Res { double val = 0, d1 = 0, d2 = 0, enc = 0; };
static IV midv(const IV& v) { IV m(v.dimension()); for (int i = 0; i < v.dimension(); ++i) m[i] = v[i].mid(); return m; }
// one Cn call at fixed step h over the box xx (x = mid of xx); returns value enclosure over xx (mean value), D1, D2 over xx
static void call(so::Solver& s, const IV& xx, double h, IV& val, IM& D1, std::vector<IM>& D2, double& encw) {
  const int n = xx.dimension(); so::JetT phi(n, 2), rem(n, 2), enc(n, 2);
  s.turnOffStepControl(); s.setStep(MpInterval(h));
  IV c = midv(xx);
  so::JetT phc(n, 2), rmc(n, 2), enc2(n, 2);
  IV yc = s.encloseCnMap(MpInterval(0), c, c, phc, rmc, enc2);     // centre value
  if (so::md(s.getStep()) != h) throw std::runtime_error("probe: step changed");
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
    IV val; IM D1; std::vector<IM> D2; double encw; call(s, v, h / m, val, D1, D2, encw); r.enc = std::max(r.enc, encw);
    std::vector<IM> Hn(n, IM(n, n));
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) for (int k = 0; k < n; ++k) {
      MpInterval acc(0); for (int l = 0; l < n; ++l) { acc += D1[i][l] * H[l][j][k]; for (int q = 0; q < n; ++q) acc += D2[i][l][q] * A[l][j] * A[q][k]; }
      Hn[i][j][k] = acc; }
    A = D1 * A; H = Hn; v = val;
  }
  for (int i = 0; i < n; ++i) { r.val = std::max(r.val, w(v[i]));
    for (int j = 0; j < n; ++j) { r.d1 = std::max(r.d1, w(A[i][j]) / 2); for (int k = 0; k < n; ++k) r.d2 = std::max(r.d2, w(H[i][j][k]) / 2); } }
  return r;
}
int main(int argc, char** argv) {
  R::setDefaultPrecision(128);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  capd::MpIMap L(lift_vf, 2, 8, 8, 3); for (int i = 0; i < 5; ++i) L.setParameter(i, MNC[i]);
  L.setParameter(5, Q("36419361737/10000000000")); L.setParameter(6, Q("60360992808/10000000000")); L.setParameter(7, Q("0"));
  IV r0(2); capd::diffAlgebra::Jet<IM, 0> j0(8, 2, 3); L(r0, j0);
  IV x(8); for (int i = 0; i < 8; ++i) x[i] = j0(i);
  capd::MpIMap fp(mn8_vf, 8, 8, 5, 2), f20(mn8_vf, 8, 8, 5, 2), f25(mn8_vf, 8, 8, 5, 2);
  for (int i = 0; i < 5; ++i) { fp.setParameter(i, MNC[i]); f20.setParameter(i, MNC[i]); f25.setParameter(i, MNC[i]); }
  so::Solver sp(fp, 20);
  so::Solver s20(f20, 20), s25(f25, 25);
  std::printf("# so_thin_probe: W0 = 0 centre orbit; thin Cn calls at the SO run's h. columns per variant: val_w D1_rad D2_rad enc_w\n");
  std::printf("%9s %9s | %-41s | %-41s | %-41s | %-41s\n", "t", "h", "single (order 20)", "2 x h/2", "4 x h/4", "single (order 25)");
  double t = 0;
  for (int a = 1; a < argc; ++a) {
    std::string s = argv[a]; double tk = std::stod(s.substr(0, s.find(':'))), hk = std::stod(s.substr(s.find(':') + 1));
    double ymax = 0; long nst = 0;
    while (t < tk) {                                                    // adaptive steps, re-centred each step
      so::JetT ph(8, 2), rm(8, 2), en(8, 2);
      sp.turnOnStepControl(); sp.encloseCnMap(MpInterval(0), x, x, ph, rm, en); double hs = so::md(sp.getStep());
      if (t + hs > tk) { sp.turnOffStepControl(); sp.setStep(MpInterval(tk - t)); hs = tk - t; }
      IV yv = sp.encloseCnMap(MpInterval(0), x, x, ph, rm, en);
      for (int i = 0; i < 8; ++i) { yv[i] += rm(i); ymax = std::max(ymax, w(yv[i])); }
      x = midv(yv); t += hs; ++nst; if (tk - t < 1e-12) t = tk;
    }
    IV y = x; (void)nst;
    Res r[4] = {probe(s20, x, hk, 1), probe(s20, x, hk, 2), probe(s20, x, hk, 4), probe(s25, x, hk, 1)};
    std::printf("%9.4f %9.3e |", tk, hk);
    for (auto& q : r) std::printf(" %9.2e %9.2e %9.2e %9.2e |", q.val, q.d1, q.d2, q.enc);
    std::printf("  (max per-step centre width %.1e)\n", ymax); (void)y;
    std::fflush(stdout);
  }
}
