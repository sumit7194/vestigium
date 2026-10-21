// mn_fieldwidth.cpp -- DIAGNOSTIC ONLY: width of the interval field enclosure mn_field<MpInterval> on a box of
// half-width h around given points (no integration). Reads "t x y px py" lines on stdin; prints t and the 4 widths.
// Usage: mn_fieldwidth <prec> <h p/q> [beta p/q]
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <iostream>
#include <string>
using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s);
  mpq_canonicalize(q); R lo, hi;
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q);
  return MpInterval(lo, hi);
}
static double d(const R& r) { return mpfr_get_d(r.*RepAccess::rep, MPFR_RNDN); }
static double w(const MpInterval& x) { return d(x.rightBound()) - d(x.leftBound()); }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
int main(int argc, char** argv) {
  R::setDefaultPrecision(std::stoi(argv[1])); MpInterval h = Q(argv[2]), r(-h.rightBound(), h.rightBound());
  const char* cs[5] = {"39/1", "-5/8", argc > 3 ? argv[3] : "13394411/1186380", "19/20", "267/1"}; MpInterval c[5];   // argv[3]: beta override
  for (int i = 0; i < 5; ++i) c[i] = Q(cs[i]);
  double t, z[4];
  while (std::cin >> t >> z[0] >> z[1] >> z[2] >> z[3]) {
    MpInterval in[4], out[4];
    for (int i = 0; i < 4; ++i) in[i] = MpInterval(z[i]) + r;
    try { mn_field<MpInterval>(in, out, c); std::printf("%.3f %.3e %.3e %.3e %.3e\n", t, w(out[0]), w(out[1]), w(out[2]), w(out[3])); }
    catch (std::exception& e) { std::printf("%.3f THREW %s\n", t, e.what()); }
  }
}
