// toy_sec.cpp -- gate for so_section.h on the Bridge's toy with a point-dependent return time:
//   xdot = -x + y, ydot = 1, section y = 1 crossed upward, start near y0 = 0:  P(x0, y0) = (x0 - y0 + 1) e^{y0 - 1}.
// Initial curved second-order set at t = 0 (r in [-1,1]^2, scale w): x0 = 1 + w r1 + 0.3 w r1 r2, y0 = w r2 + 0.3 w r1^2.
// Prints the section image (x, C, H, box) for toy_sec.py (pointwise containment against the exact P), and the hull P
// jets' [D2Psi(R0)] for the corner test. Negative controls: SEC_NO_DP=1 (raw flow jets), SEC_HULL_AT_CENTRE=1.
// Usage: toy_sec <w>
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <cstdio>
#include <cstdlib>
#include "so_section.h"
using capd::MpInterval; using capd::autodiff::Node;
void toy_vf(Node, Node in[], int, Node o[], int, Node[], int) { o[0] = -in[0] + in[1]; o[1] = Node(1) + in[0] * 0; }
static void pr(const MpInterval& v) { char *a = nullptr, *b = nullptr;
  mpfr_asprintf(&a, "%.60RDe", v.leftBound().*so::RepA::rep); mpfr_asprintf(&b, "%.60RUe", v.rightBound().*so::RepA::rep);
  std::printf(" %s %s", a, b); mpfr_free_str(a); mpfr_free_str(b); }
int main(int argc, char** argv) {
  capd::MpFloat::setDefaultPrecision(128);
  double w = std::stod(argv[1]);
  so::SEC_NO_DP = std::getenv("SEC_NO_DP") != nullptr; so::SEC_HULL_AT_CENTRE = std::getenv("SEC_HULL_AT_CENTRE") != nullptr;
  capd::MpIMap f(toy_vf, 2, 2, 0, 2);
  capd::MpICnOdeSolver solver(f, 20);
  capd::MpICoordinateSection sec(2, 1, MpInterval(1));          // y = 1
  capd::MpICnPoincareMap pm(solver, sec, capd::poincare::MinusPlus);
  so::Set X(2); X.x[0] = MpInterval(1); X.x[1] = MpInterval(0);
  double hs = std::getenv("SEC_H_W2") ? w : 1.0;               // SEC_H_W2: curvature ~ w^2 (as in the MN lift) instead of ~ w
  X.C[0][0] = w; X.C[1][1] = w; X.H[0][0][1] = 0.3 * w * hs; X.H[0][1][0] = 0.3 * w * hs; X.H[1][0][0] = 0.6 * w * hs;
  so::SectionImage S = so::section_image(pm, X);
  std::printf("# toy_sec w %g no_dp %d hull_at_centre %d ; return-time enclosures thin [%g, %g] hull [%g, %g]\nX", w, so::SEC_NO_DP, so::SEC_HULL_AT_CENTRE,
              so::lo(S.rtT), so::hi(S.rtT), so::lo(S.rtK), so::hi(S.rtK));
  for (int i = 0; i < 2; ++i) pr(S.x[i]);
  std::printf("\nC"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) pr(S.C[i][a]);
  std::printf("\nH"); for (int i = 0; i < 2; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) pr(S.H[i][a][b]);
  std::printf("\nBOX"); for (int i = 0; i < 2; ++i) pr(S.box[i]);
  std::printf("\nD2PSI"); for (auto& v : S.D2PsiR0) pr(v); std::printf("\nHS %.17e\n", hs);
}
