// d2f_gate.cpp -- the D2f gate (SECOND_ORDER_STEP_DESIGN.md §4): CAPD degree-2 jets of the 8-D MN field (mn8_field) at
// points read from stdin (8 numbers per line, exact decimal strings); prints value, first and FULL second derivatives
// for d2f_gate.py (comparison with sympy's exact derivatives at 50 digits, and symmetry).
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
#include <iostream>
#include <string>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field8.h"
void vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn8_field<Node>(in, o, c); }
static void pr(const MpInterval& v) { char *a = nullptr, *b = nullptr;
  mpfr_asprintf(&a, "%.40Re", v.leftBound().*RepAccess::rep); mpfr_asprintf(&b, "%.40Re", v.rightBound().*RepAccess::rep);
  std::printf(" %s %s", a, b); mpfr_free_str(a); mpfr_free_str(b); }
int main() {
  capd::MpFloat::setDefaultPrecision(160);
  capd::MpIMap f(vf, 8, 8, 5, 2);
  const char* cs[5] = {"39", "-0.625", "11.290239215765269", "0.95", "267"};
  // exact rationals for the parameters
  mpq_t q; mpq_init(q); const char* qs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) { mpq_set_str(q, qs[i], 10); mpq_canonicalize(q); capd::MpFloat lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); f.setParameter(i, MpInterval(lo, hi)); }
  mpq_clear(q); (void)cs;
  std::string tok;
  while (true) {
    IV z(8); bool ok = true;
    for (int i = 0; i < 8; ++i) { if (!(std::cin >> tok)) { ok = false; break; } capd::MpFloat v; mpfr_set_str(v.*RepAccess::rep, tok.c_str(), 10, MPFR_RNDN); z[i] = MpInterval(v); }
    if (!ok) break;
    capd::diffAlgebra::Jet<IM, 0> J(8, 8, 2); f(z, J);
    std::printf("P");
    for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) for (int k = 0; k < 8; ++k) {
      int a = std::min(j, k), b = std::max(j, k); MpInterval c = J(i, a, b); pr(a == b ? c * 2 : c); }
    std::printf("\n"); std::fflush(stdout);
  }
}
