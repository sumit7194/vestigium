// Codegen gate harness: evaluate every generated MN/Kerr function on MPFR intervals at points read from stdin
// (exact decimals as p q pairs) and print each enclosure as hex bounds. Not proof code; a test of gen/mn_field.h.
#include "capd/mpcapdlib.h"
#include <gmp.h>
#include <iostream>
#include <string>
using capd::MpInterval; typedef capd::MpFloat R;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "gen/mn_field.h"
static MpInterval Qr(const std::string& s) {
  mpq_t q; mpq_init(q); mpq_set_str(q, s.c_str(), 10); mpq_canonicalize(q); R lo, hi;
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
static void pr(const char* tag, const MpInterval& v) {
  char *a = nullptr, *b = nullptr; mpfr_asprintf(&a, "%Ra", v.leftBound().*RepAccess::rep); mpfr_asprintf(&b, "%Ra", v.rightBound().*RepAccess::rep);
  std::cout << tag << " " << a << " " << b << "\n"; mpfr_free_str(a); mpfr_free_str(b);
}
int main() {
  R::setDefaultPrecision(160);
  std::string k, al, be, E, L; std::cin >> k >> al >> be >> E >> L;
  MpInterval c[5] = {Qr(k), Qr(al), Qr(be), Qr(E), Qr(L)};
  std::string a, b, cc, d;
  while (std::cin >> a >> b >> cc >> d) {
    MpInterval in[4] = {Qr(a), Qr(b), Qr(cc), Qr(d)}, o4[4], o1[1], o3[3];
    mn_field<MpInterval>(in, o4, c); for (int i = 0; i < 4; ++i) pr(("f" + std::to_string(i)).c_str(), o4[i]);
    mn_H<MpInterval>(in, o1, c); pr("H", o1[0]);
    mn_gpp<MpInterval>(in, o1, c); pr("gpp", o1[0]);
    mn_B<MpInterval>(in, o1, c); pr("B", o1[0]);
    mn_lift<MpInterval>(in, o3, c); pr("gxx", o3[0]); pr("gyy", o3[1]); pr("V", o3[2]);
    std::cout << "END\n";
  }
}
