// Route-1 pilot, development harness 1 (NOT proof code; no claims). Claude Opus 5.5 (Quantum), 2026-11-28.
// The MN field with beta carried as a 5th STATE variable (beta' = 0), so that d/dbeta comes out of CAPD's C^2 jet.
// mode "jet": integrate the C^2 time map over [0, T] from a thin point (x, y, px, py, beta) and print the value,
// the Jacobian column d/dbeta, and selected Hessian entries, for comparison with float finite differences.
// Usage: r1_dev jet T x y px py beta
#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include <gmp.h>
#include <cstdio>
#include <iostream>
#include <string>
#include "proof_guard.h"
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Qs(const std::string& s) {   // exact rational "p/q" or integer, outward-rounded
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational " + s); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
static std::string e(const MpInterval& x) { R m = x.mid().leftBound(); char* s = nullptr; mpfr_asprintf(&s, "%.30Re", m.*RepAccess::rep); std::string o(s); mpfr_free_str(s);
  R w = x.rightBound() - x.leftBound(); char* t = nullptr; mpfr_asprintf(&t, "%.2Re", w.*RepAccess::rep); o += " w " + std::string(t); mpfr_free_str(t); return o; }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "gen/mn_field.h"
// state (x, y, px, py, beta); params (k, alpha, E, L, zero)
void mn_vf5(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], in[4], par[2], par[3]}; mn_field<Node>(in, o, c); o[4] = par[4];
}
int main(int argc, char** argv) {
  try {
    if (argc < 8) { std::cerr << "usage: r1_dev jet T x y px py beta (exact rationals)\n"; return 2; }
    R::setDefaultPrecision(128);
    capd::MpIMap f(mn_vf5, 5, 5, 5);
    f.setParameter(0, Qs("4")); f.setParameter(1, Qs("-1/3")); f.setParameter(2, Qs("93528150456799871854/100000000000000000000"));
    f.setParameter(3, Qs("12972532035607280691/1000000000000000000")); f.setParameter(4, MpInterval(0));
    IV x0(5); for (int i = 0; i < 5; ++i) x0[i] = Qs(argv[3 + i]);
    capd::MpIC2OdeSolver solver(f, 20); solver.setAbsoluteTolerance(1e-24); solver.setRelativeTolerance(1e-24);   // step control only (double, as in S2)
    capd::MpIC2TimeMap tm(solver);
    capd::MpC2Rect2Set s(x0);
    MpInterval T = Qs(argv[2]);
    IV v = tm(T, s);
    IM D = (IM)s;
    capd_proof::require_finite_all(v, "value"); capd_proof::require_finite_all(D, "D");
    for (int i = 0; i < 5; ++i) std::printf("VAL %d %s\n", i, e(v[i]).c_str());
    for (int i = 0; i < 5; ++i) std::printf("DBETA %d %s\n", i, e(D[i][4]).c_str());
    for (int i = 0; i < 4; ++i) std::printf("DX %d %s\n", i, e(D[i][0]).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_x_beta %d %s\n", i, e(s(i, 0, 4)).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_x_x %d %s\n", i, e(s(i, 0, 0)).c_str());
    for (int i = 0; i < 4; ++i) std::printf("H_beta_beta %d %s\n", i, e(s(i, 4, 4)).c_str());
    return 0;
  } catch (std::exception& ex) { std::printf("FAIL %s\n", ex.what()); return 1; }
}
