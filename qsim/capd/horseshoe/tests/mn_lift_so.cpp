// mn_lift_so.cpp -- the MN lift as a second-order set (SECOND_ORDER_STEP_DESIGN.md §2a): L : R0 = [-1,1]^2 -> R^8,
//   x = c_x + u h, y = 0, p_x = c_p + s h, p_y = sqrt((-1 - g^xx p_x^2 - 2 V) / g^yy) at y = 0, (a, b, E2, eG) = aux(x, 0),
// written as a CAPD Node map with jets: L(0), DL(0), D2L(0) at the thin point 0 (degree-2 jet), and the degree-3
// coefficients over the box R0 for the remainder E0 = sum_{|alpha| = 3} c_alpha(R0) r^alpha (integral remainder,
// normalised coefficients D^alpha / alpha!).  Prints x0, C0, H0, E0 for mn_lift_so.py (pointwise containment against
// 50-digit evaluation of the original formulas).  NEG_NOCUBIC drops E0's cubic part (negative control).
// Usage: mn_lift_so <h p/q>
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <cstdlib>
#include <string>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational"); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
#include "../gen/mn_field8.h"
// par: 0..4 = k, alpha, beta, E, L; 5 = c_x; 6 = c_p; 7 = h
static int VAR = 99;                                            // debug bisection level (99 = the full lift)
void lift_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  for (int i = 0; i < 8; ++i) o[i] = x;
  if (VAR == 0) return;
  Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c);
  if (VAR == 1) { o[0] = g[0]; o[1] = g[1]; o[2] = g[2]; return; }
  Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1];
  if (VAR == 2) { o[3] = rad; return; }
  if (VAR == 3) { o[3] = sqrt(rad); return; }
  Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c);
  if (VAR == 4) { for (int i = 0; i < 4; ++i) o[4 + i] = aux[i]; return; }
  o[0] = x; o[1] = zero; o[2] = px; o[3] = sqrt(rad); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i];
}
static void pr(const MpInterval& v) { char *a = nullptr, *b = nullptr;
  mpfr_asprintf(&a, "%.40Re", v.leftBound().*RepAccess::rep); mpfr_asprintf(&b, "%.40Re", v.rightBound().*RepAccess::rep);
  std::printf(" %s %s", a, b); mpfr_free_str(a); mpfr_free_str(b); }
int main(int argc, char** argv) {
  R::setDefaultPrecision(128);
  if (const char* v = std::getenv("VAR")) VAR = std::atoi(v);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  capd::MpIMap L(lift_vf, 2, 8, 8, 3);
  for (int i = 0; i < 5; ++i) L.setParameter(i, Q(cs[i]));
  L.setParameter(5, Q("36419361737/10000000000")); L.setParameter(6, Q("60360992808/10000000000")); L.setParameter(7, Q(argv[1]));
  typedef capd::diffAlgebra::Jet<IM, 0> J;
  IV r0(2), R0(2); R0[0] = MpInterval(-1, 1); R0[1] = MpInterval(-1, 1);
  if (std::getenv("DEBUG_VALUES")) {                           // plain evaluation, to see the components
    capd::MpIMap L1(lift_vf, 2, 8, 8, 1); for (int i = 0; i < 8; ++i) L1.setParameter(i, L.getParameter(i));
    IV v = L1(r0); for (int i = 0; i < 8; ++i) { pr(v[i]); std::printf("\n"); } return 0;
  }
  if (std::getenv("DEBUG_JET")) {
    IV v = L(r0); std::printf("# degree-3 map, plain eval p_y"); pr(v[3]); std::printf("\n"); std::fflush(stdout);
    J jt(8, 2, 1); try { L(r0, jt); std::printf("# jet degree 1 ok, p_y"); pr(jt(3)); std::printf("\n"); } catch (std::exception& e) { std::printf("# jet degree 1 THREW %s\n", e.what()); }
    std::fflush(stdout);
    J jt3(8, 2, 3); try { L(r0, jt3); std::printf("# jet degree 3 ok, p_y"); pr(jt3(3)); std::printf("\n"); } catch (std::exception& e) { std::printf("# jet degree 3 THREW %s\n", e.what()); }
    std::fflush(stdout);
    J jt2(8, 2, 2); try { L(r0, jt2); std::printf("# jet degree 2 ok, p_y"); pr(jt2(3)); std::printf("\n"); } catch (std::exception& e) { std::printf("# jet degree 2 THREW %s\n", e.what()); }
    return 0;
  }
  J j0(8, 2, 3), jR(8, 2, 3);           // 8 outputs in 2 variables (Jet(m, n, d))
  L(r0, j0); L(R0, jR);                                        // jets at the thin point 0, and over the box R0
  bool nocubic = std::getenv("NEG_NOCUBIC") != nullptr;
  std::printf("# MN lift as a second-order set, h %s, nocubic %d\nX", argv[1], nocubic);
  for (int i = 0; i < 8; ++i) pr(j0(i));
  std::printf("\nC"); for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) pr(j0(i, a));
  std::printf("\nH"); for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) {
    int lo = std::min(a, b), hi = std::max(a, b); MpInterval cf = j0(i, lo, hi); pr(lo == hi ? cf * 2 : cf); }     // full second derivatives
  std::printf("\nE3");                                          // sum_{|alpha|=3} c_alpha(R0) r^alpha over R0, componentwise
  for (int i = 0; i < 8; ++i) {
    MpInterval r1 = R0[0], r2 = R0[1];
    MpInterval e = jR(i, 0, 0, 0) * power(r1, 3) + jR(i, 0, 0, 1) * sqr(r1) * r2 + jR(i, 0, 1, 1) * r1 * sqr(r2) + jR(i, 1, 1, 1) * power(r2, 3);
    pr(nocubic ? MpInterval(0) : e);
  }
  std::printf("\n");
}
