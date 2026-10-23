// mn_sec.cpp -- DIAGNOSTIC: the B17 SECTION checkpoint for a second-order MN set saved by mn_so at t_sec - 0.5
// (<state>.pre_<kind>), by so_section.h (CAPD Cn Poincare map, thin + hull CnRect2Set, computeDP; gated on the toy).
// Preconditions checked and logged (the Bridge's review): crossing-time enclosures near 0.5 (the intended, first
// crossing); transversality (sign of ydot over the image enclosure); S4 and S9 on the image enclosure; K = hull of the
// whole saved set (E included). Measurement: the B17 rows (plain, and flow-projected as in the C0 B17 runs: identical on
// Sigma up to the y-box) with the B17 rule (k = 5, gain-weighted fake directions); optional extra row file (target h-set
// coordinates on Sigma) printed as widths.
// Usage: mn_sec <state.pre_kind> <checkpoints.txt> <kind: sec_down|sec_return> [rows file]
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include "mn_common.h"
#include "so_section.h"
int main(int argc, char** argv) {
  if (argc < 4) { std::cerr << "usage: mn_sec state checkpoints kind [rows]\n"; return 2; }
  R::setDefaultPrecision(128);
  const char* cs[5] = {"39/1", "-5/8", "13394411/1186380", "19/20", "267/1"};
  for (int i = 0; i < 5; ++i) MNC[i] = Q(cs[i]);
  DOM.reset(new capd::MpIMap(dom_vf, 2, 2, 5)); for (int i = 0; i < 5; ++i) DOM->setParameter(i, MNC[i]);
  capd::MpIMap fa(aux_vf, 2, 4, 5); for (int i = 0; i < 5; ++i) fa.setParameter(i, MNC[i]);
  so::Set X(8); long steps; size_t ncp;
  if (!load(argv[1], X, steps, ncp)) { std::printf("cannot read %s\n", argv[1]); return 1; }
  std::string kind = argv[3]; auto cps = read_cps(argv[2]); const Checkpoint* c = nullptr;
  for (auto& cc : cps) if (cc.kind == kind) c = &cc;
  if (!c) { std::printf("no checkpoint %s\n", kind.c_str()); return 1; }
  std::printf("# mn_sec %s from %s (t = %.6f, %ld steps)\n", kind.c_str(), argv[1], so::md(X.t), steps);
  capd::MpIMap f(mn8_vf, 8, 8, 5, 2); for (int i = 0; i < 5; ++i) f.setParameter(i, MNC[i]);
  capd::MpICnOdeSolver solver(f, 20);
  capd::MpICoordinateSection sec(8, 1);                             // y = 0
  capd::MpICnPoincareMap pm(solver, sec, kind == "sec_down" ? capd::poincare::PlusMinus : capd::poincare::MinusPlus);
  auto t0 = std::chrono::steady_clock::now();
  try {
    so::SectionImage S = so::section_image(pm, X);
    std::printf("# crossing-time enclosures: thin [%.9f, %.9f], hull [%.9f, %.9f] (expected ~0.5 after t_sec - 0.5)\n",
                so::lo(S.rtT), so::hi(S.rtT), so::lo(S.rtK), so::hi(S.rtK));
    IV img = S.crossEnc, fx = f(img);
    std::printf("# transversality: ydot over the hull image in [%.6e, %.6e] (%s)\n", so::lo(fx[1]), so::hi(fx[1]),
                (kind == "sec_down" ? so::hi(fx[1]) < 0 : so::lo(fx[1]) > 0) ? "certified, correct direction" : "NOT CERTIFIED");
    mn_domain(img); s9(img);
    std::printf("# S4 and S9 hold on the hull image enclosure\n");
    IV xy(2); xy[0] = img[0]; xy[1] = img[1];
    auto offman = [&](int q) { IM Da(4, 2); IV xm(2); xm[0] = xy[0].mid(); xm[1] = xy[1].mid(); fa(xm, Da);
                               IV n(8); n[4 + q] = 1; n[0] = -Da[q][0].mid(); n[1] = -Da[q][1].mid(); return n; };
    auto projrow = [&](IV n) { IV fc(8); for (int i = 0; i < 4; ++i) fc[i] = MpInterval(c->centre[i]); IV z = f(fc); MpInterval nf(0);
                               for (int i = 0; i < 8; ++i) nf += n[i] * z[i]; n[1] = n[1] - (nf / z[1]).mid(); return n; };
    const double K = 5.0;
    for (int variant = 0; variant < 2; ++variant) {
      IV u1 = variant ? projrow(c->u1) : c->u1, u2 = variant ? projrow(c->u2) : c->u2, nH = variant ? projrow(c->nH) : c->nH;
      double W1 = so::hi(S.project(u1)) - so::lo(S.project(u1)), W2 = so::hi(S.project(u2)) - so::lo(S.project(u2));
      double Wf[5] = {so::hi(S.project(nH)) - so::lo(S.project(nH)), 0, 0, 0, 0};
      for (int q = 0; q < 4; ++q) { IV n = variant ? projrow(offman(q)) : offman(q); Wf[1 + q] = so::hi(S.project(n)) - so::lo(S.project(n)); }
      double fake = 0; for (int q = 0; q < 5; ++q) fake += Wf[q] * c->g[2 + q];
      bool ok = (W1 / c->tu1 <= K) && (W2 / c->tu2 <= K) && (fake <= K * c->tu2 * c->g[1]);
      std::printf("CHECKPOINT %-10s t=%10.4f rows %-9s u1 %.3e/%.3e=%.2f u2 %.3e/%.3e=%.2f fake %.3e vs %.3e  %s\n", kind.c_str(), c->t,
                  variant ? "projected" : "plain", W1, c->tu1, W1 / c->tu1, W2, c->tu2, W2 / c->tu2, fake, K * c->tu2 * c->g[1],
                  (W1 / c->tu1 < 0.98 || W2 / c->tu2 < 0.98) ? "HARNESS-ERROR" : (ok ? "PASS" : "FAIL"));
    }
    if (argc > 4) {                                               // target h-set rows on Sigma (one row of 8 numbers per line)
      std::ifstream in(argv[4]); std::string line; int k = 0;
      while (std::getline(in, line)) { std::istringstream is(line); IV n(8); for (int i = 0; i < 8; ++i) { double v; is >> v; n[i] = MpInterval(v); }
        MpInterval pj = S.project(n); std::printf("ROW %d width %.6e interval [%.12e, %.12e]\n", k++, so::hi(pj) - so::lo(pj), so::lo(pj), so::hi(pj)); }
    }
    std::printf("# box widths:"); for (int i = 0; i < 8; ++i) std::printf(" %.2e", so::hi(S.box[i]) - so::lo(S.box[i])); std::printf("\n");
  } catch (std::exception& e) { std::printf("THREW: %s\n", e.what()); }
  std::printf("# wall %.0f s\n", std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
}
