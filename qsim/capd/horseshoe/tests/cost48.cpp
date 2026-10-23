// cost48.cpp -- DIAGNOSTIC (planning): wall time of CAPD C0 steps of the 48-state extended field (gen/mn_field48.h),
// thin initial data at the smoke-box centre (X1, X2 = unit x / p_x directions, X_ij = 0). No verdicts.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <chrono>
#include <cstdio>
#include <string>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); mpq_set_str(q, s.c_str(), 10); mpq_canonicalize(q); R lo, hi;
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field8.h"
#include "../gen/mn_field48.h"
void vf48(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn48_field<Node>(in, o, c); }
int main(int argc, char** argv) {
  R::setDefaultPrecision(128); int nsteps = argc > 1 ? std::stoi(argv[1]) : 3;
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"}; MpInterval c[5]; for (int i = 0; i < 5; ++i) c[i] = Q(cs[i]);
  IV x(48); x[0] = Q("36419361737/10000000000"); x[2] = Q("60360992808/10000000000"); x[3] = MpInterval(93.70479329063444);
  MpInterval z(0), in8[8] = {x[0], z, z, z, z, z, z, z}, a[4]; mn8_aux<MpInterval>(in8, a, c); for (int i = 0; i < 4; ++i) x[4 + i] = a[i].mid();
  x[8 + 0] = 1; x[16 + 2] = 1;                                   // X1 = e_x, X2 = e_px
  capd::MpIMap f(vf48, 48, 48, 5); for (int i = 0; i < 5; ++i) f.setParameter(i, c[i]);
  capd::MpIOdeSolver solver(f, 20);
  capd::MpC0TripletonSet s(x);
  capd::MpITimeMap tm(solver); tm.stopAfterStep(true);
  auto t0 = std::chrono::steady_clock::now();
  for (int k = 0; k < nsteps; ++k) { tm(MpInterval(100), s); double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::printf("step %d t=%.4f h=%.3e cumulative %.1f s\n", k + 1, mpfr_get_d(s.getCurrentTime().leftBound().*RepAccess::rep, MPFR_RNDN), mpfr_get_d(solver.getStep().leftBound().*RepAccess::rep, MPFR_RNDN), sec); std::fflush(stdout); }
}
