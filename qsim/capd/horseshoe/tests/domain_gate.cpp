// domain_gate.cpp -- gate for the generated mn8_domain (B, g_phiphi in the structured form): at exact rational points
// (stdin: "p/q p/q" per line) prints the 160-bit enclosures; domain_gate.py checks they contain 60-digit mpmath values.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <iostream>
#include <string>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational");
  mpq_canonicalize(q); R lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q);
  return MpInterval(lo, hi);
}
static std::string hx(const R& r) { char* c = nullptr; mpfr_asprintf(&c, "%.60Re", r.*RepAccess::rep); std::string o(c); mpfr_free_str(c); return o; }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field8.h"
int main() {
  R::setDefaultPrecision(160);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"}; MpInterval c[5]; for (int i = 0; i < 5; ++i) c[i] = Q(cs[i]);
  std::string xs, ys;
  while (std::cin >> xs >> ys) {
    MpInterval z(0), in[8] = {Q(xs), Q(ys), z, z, z, z, z, z}, out[2];
    mn8_domain<MpInterval>(in, out, c);
    for (int i = 0; i < 2; ++i) std::printf("%s %s ", hx(out[i].leftBound()).c_str(), hx(out[i].rightBound()).c_str());
    std::printf("\n");
  }
}
