// erep_bench.cpp -- T3b timing (E_REP_PREREG.md, amended T3): the per-step cost of the zonotope error part alone, as a
// function of the column count N, on 8-D MPFR-128 data shaped like the MN run's. One "step" = what so::step() adds in
// SO_EREP=zsym on top of the shared part: G <- D1c G (N interval mat-vecs), append the injected columns, ehull (for K and
// dDe, called twice per step: X.hull() at the start and for e), plus the 7 checkpoint projections (counted per step as an
// upper bound; the run only projects at checkpoints). Timing only: no widths are produced or read.
// Usage: erep_bench N1 N2 ...   (prints N and seconds per step, median of 5)
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <vector>
#include "so_set.h"
using capd::MpInterval; typedef capd::MpFloat R;
int main(int argc, char** argv) {
  R::setDefaultPrecision(128);
  const int n = 8; so::SO_EREP = 1;
  so::IM D(n, n); for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) { MpInterval v = MpInterval(((i * 7 + j * 3) % 11) - 5) / 7; D[i][j] = v + MpInterval(-1, 1) * MpInterval(1e-30); }
  so::IV s(n); for (int i = 0; i < n; ++i) s[i] = MpInterval(-1, 2) * MpInterval(1e-9);
  so::IV u(n); for (int i = 0; i < n; ++i) u[i] = MpInterval(i + 1) / 10;
  for (int a = 1; a < argc; ++a) {
    const int N = std::atoi(argv[a]);
    std::vector<double> ts;
    for (int rep = 0; rep < 5; ++rep) {
      so::Set X(n); X.G.assign(N, so::IV(n));
      for (int j = 0; j < N; ++j) for (int i = 0; i < n; ++i) X.G[j][i] = MpInterval((i + j) % 13 + 1) / 1000;
      auto t0 = std::chrono::steady_clock::now();
      so::IV h1 = X.ehull();                                  // X.hull() at the start of the step
      so::IV e = X.ehull();                                   // e for dDe
      for (so::IV& g : X.G) g = D * g;                        // propagate
      for (int i = 0; i < n; ++i) { so::IV g(n); g[i] = so::magI(s[i]); X.G.push_back(g); }
      so::IV h2 = X.hull();                                   // the driver's per-step hull (S4/S9/consistency)
      for (int k = 0; k < 7; ++k) { MpInterval p = X.project(u); (void)p; }
      ts.push_back(std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
      (void)h1; (void)e; (void)h2;
    }
    std::sort(ts.begin(), ts.end());
    std::printf("N %d  seconds per step (median of 5) %.4f  min %.4f  max %.4f\n", N, ts[2], ts[0], ts[4]); std::fflush(stdout);
  }
}
