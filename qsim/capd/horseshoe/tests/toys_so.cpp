// toys_so.cpp -- gates for so_set.h on 2-D toys with closed-form flows (SECOND_ORDER_STEP_DESIGN.md §4, §7):
//   A: xdot = -x + 5 y + y^2   B: xdot = -x + 5 y + y^3   C, E: xdot = -x + y^4   D: xdot = -x + x y      (ydot = -y)
//   (E = C's field with the curvature in y0, so that the H-spread of the hull run matters: the Toy C negative control
//    for NEG_NOSPREAD cannot fail by construction, because C's field is linear in x where C's curvature sits)
// initial sets (r in [-1,1]^2, scale w):  A, B: x0 = 1 + w r1;  C: x0 = w (r1 + 0.3 r2^2);  D: x0 = 1 + w (r1 + 0.3 r1 r2);
// y0 = w r2.  Prints step 1's [D2Psi(R0)] (for the corner test) and the final set (for pointwise containment);
// toys_so.py does the checks against the exact flows at 50 digits.
// Negative-control switches (environment): NEG_NOSPREAD (hull run with X_i = C_i only), NEG_OFFDIAG=<f> (off-diagonal
// jet coefficients scaled by f), NEG_REMSCALE=<f> (remainder box scaled by f).
// Usage: toys_so <A|B|C|D> <w> <T>
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include "so_set.h"
using capd::MpInterval; using capd::autodiff::Node;
static char TOY = 'A';
void toy_vf(Node, Node in[], int, Node o[], int, Node[], int) {
  Node x = in[0], y = in[1];
  if (TOY == 'A') o[0] = -x + 5 * y + y * y;
  else if (TOY == 'B') o[0] = -x + 5 * y + y * y * y;
  else if (TOY == 'C' || TOY == 'E') o[0] = -x + y * y * y * y;
  else o[0] = -x + x * y;
  o[1] = -y;
}
static void pr(const MpInterval& v) { char *a = nullptr, *b = nullptr;
  mpfr_asprintf(&a, "%.60RDe", v.leftBound().*so::RepA::rep); mpfr_asprintf(&b, "%.60RUe", v.rightBound().*so::RepA::rep);
  std::printf(" %s %s", a, b); mpfr_free_str(a); mpfr_free_str(b); }
int main(int argc, char** argv) {
  capd::MpFloat::setDefaultPrecision(128);
  TOY = argv[1][0]; double w = std::stod(argv[2]); double T = std::stod(argv[3]);
  bool nospread = std::getenv("NEG_NOSPREAD") != nullptr;
  if (const char* f = std::getenv("NEG_OFFDIAG")) so::SO_OFFDIAG_FACTOR = std::stod(f);
  if (const char* f = std::getenv("NEG_REMSCALE")) so::SO_REMAINDER_SCALE = std::stod(f);
  capd::MpIMap fK(toy_vf, 2, 2, 0, 2), fT(toy_vf, 2, 2, 0, 2);
  so::Solver solK(fK, 20), solT(fT, 20);
  if (const char* c = std::getenv("NEG_TCAP")) solT.setMaxStep(MpInterval(std::stod(c)));   // forced test of the step rule
  so::Set X(2);
  X.x[0] = (TOY == 'C' || TOY == 'E') ? MpInterval(0) : MpInterval(1); X.x[1] = MpInterval(0);
  X.C[0][0] = w; X.C[1][1] = w;
  if (TOY == 'C') X.H[0][1][1] = 0.6 * w;
  if (TOY == 'D') { X.H[0][0][1] = 0.3 * w; X.H[0][1][0] = 0.3 * w; }
  if (TOY == 'E') X.H[1][0][0] = 0.6 * w;                    // Toy E: Toy C's field, curvature in y0 (y0 = w r2 + 0.3 w r1^2)
  std::printf("# toy %c w %g T %g nospread %d offdiag %g remscale %g\n", TOY, w, T, nospread, so::SO_OFFDIAG_FACTOR, so::SO_REMAINDER_SCALE);
  int k = 0, cstep = std::getenv("CORNER_STEP") ? std::atoi(std::getenv("CORNER_STEP")) : 20;
  while (so::md(X.t) < T - 1e-12) {
    so::Set before = X;
    so::StepLog lg = so::step(solK, solT, X, !nospread); ++k;
    if (k == cstep) {                                          // the set BEFORE this step, the step size, and [D2Psi(R0)]
      std::printf("CORNER step %d t0", k); pr(before.t); std::printf(" h %.30e\nCX", lg.h);
      for (int i = 0; i < 2; ++i) pr(before.x[i]);
      std::printf("\nCC"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) pr(before.C[i][a]);
      std::printf("\nCH"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) pr(before.H[i][a][b]);
      std::printf("\nCK"); for (auto& v : lg.hK) pr(v); std::printf("\n");
    }
    if (so::md(X.t) > T) break;
  }
  std::printf("FINAL t"); pr(X.t); std::printf(" steps %d resteps %ld\nX", k, so::SO_RESTEPS);
  for (int i = 0; i < 2; ++i) pr(X.x[i]);
  std::printf("\nC"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) pr(X.C[i][a]);
  std::printf("\nH"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) pr(X.H[i][a][b]);
  std::printf("\nB"); for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) pr(X.B[i][j]);
  std::printf("\nRE"); for (int i = 0; i < 2; ++i) pr(X.re[i]); std::printf("\n");
}
