// CAPD third replay of the Morales-Ramis certificates (Arb-free: CAPD MpInterval on MPFR only).
// Generic driver; the row-specific vector field comes from the generated header REPLAY_FIELD (mr_replay.py), which
// defines:  NE (number of exp-factors E_k carried as ODE state), NPAR_COEF, and
//   void field(Node s, Node in[], int, Node out[], int, Node par[], int)
//   void w_at(int k, const MpInterval& tre, const MpInterval& tim, const std::vector<MpInterval>& C,
//             MpInterval& wre, MpInterval& wim)       (w_k at a point, MPFR interval arithmetic, coefficients C)
// with par[0..3] = segment endpoints a_re, a_im, b_re, b_im (t = a + (b - a) s, s in [0,1]) and par[4..] the exact
// coefficient enclosures. State: Phi (2x2 complex, 8 reals) then E_k (re, im) for k < NE.
// Input (stdin, from mr_replay.py), all numbers exact MPFR hex:
//   PREC p | ORDER n | PAR i lo hi | LOOP name nvert | V re im (one line per vertex, exact) ...
// E_k at each vertex is enclosed HERE (no Arb): E = exp(w) = e^Re(w) (cos Im w + i sin Im w), with MPFR exp and the
// guarded capd_proof::checked_cos / checked_sin.
//   WORD g a*b*... | WORD h ...  | END
// Output: per-loop matrices and the certificate quantities, each "key lo hi" (exact %Ra), then VERDICT.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
#include <iostream>
#include <chrono>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include REPLAY_FIELD

using capd::MpInterval;
typedef capd::MpFloat R;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static mpfr_ptr rep_mut(R& r) { return r.*RepAccess::rep; }
static std::string hexof(const R& r) {
  char* s = nullptr; mpfr_asprintf(&s, "%Ra", r.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o;
}
static R exact(const std::string& s) {
  R out; mpfr_t t; mpfr_init2(t, mpfr_get_prec(rep_mut(out)));
  char* end = nullptr;
  int tern = mpfr_strtofr(t, s.c_str(), &end, 16, MPFR_RNDN);
  if (!(end && *end == '\0' && tern == 0 && mpfr_number_p(t))) throw std::runtime_error("inexact input " + s);
  if (mpfr_set(rep_mut(out), t, MPFR_RNDN) != 0) throw std::runtime_error("copy inexact " + s);
  mpfr_clear(t); return out;
}
static MpInterval ival(const std::string& lo, const std::string& hi) {
  MpInterval x(exact(lo), exact(hi)); capd_proof::require_finite(x, "input"); return x;
}
static void out(const std::string& key, const MpInterval& x) {
  capd_proof::require_finite(x, key.c_str());
  std::cout << key << " " << hexof(x.leftBound()) << " " << hexof(x.rightBound()) << "\n";
}

struct CI { MpInterval re, im; };
static CI cmul(const CI& a, const CI& b) { return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re}; }
static CI cadd(const CI& a, const CI& b) { return {a.re + b.re, a.im + b.im}; }
static CI csub(const CI& a, const CI& b) { return {a.re - b.re, a.im - b.im}; }
static CI cdiv(const CI& a, const CI& b) {
  MpInterval d = b.re * b.re + b.im * b.im;
  if (!capd_proof::certainly_positive(d)) throw std::runtime_error("complex division by a box containing 0");
  return {(a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d};
}
struct M2 { CI a[2][2]; };
static M2 mmul(const M2& x, const M2& y) {
  M2 z; for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) z.a[i][j] = cadd(cmul(x.a[i][0], y.a[0][j]), cmul(x.a[i][1], y.a[1][j]));
  return z;
}
static CI mdet(const M2& x) { return csub(cmul(x.a[0][0], x.a[1][1]), cmul(x.a[0][1], x.a[1][0])); }
static CI mtr(const M2& x) { return cadd(x.a[0][0], x.a[1][1]); }
static M2 minv(const M2& x) {
  CI d = mdet(x), zero{MpInterval(0), MpInterval(0)}; M2 z;
  z.a[0][0] = cdiv(x.a[1][1], d); z.a[1][1] = cdiv(x.a[0][0], d);
  z.a[0][1] = cdiv(csub(zero, x.a[0][1]), d); z.a[1][0] = cdiv(csub(zero, x.a[1][0]), d);
  return z;
}
static M2 ident() { M2 m; CI o{MpInterval(1), MpInterval(0)}, z{MpInterval(0), MpInterval(0)}; m.a[0][0] = o; m.a[1][1] = o; m.a[0][1] = z; m.a[1][0] = z; return m; }

static int ORDER = 30;
static double TOL = 0;   // 0: CAPD default (10^-(digits+3), ~1e-80 at 256 bits); set by "TOL x"
static double FIXSTEP = 0;
static int SUBSEG = 1;          // A5: sub-segments per straight segment (power of 2), used with codegen 3 (LOCAL_SHIFT)
static const int MAXHALV = 4;    // A5 rule (pre-registered): a sub-segment whose CAPD transport throws is halved dyadically, at most 4 times, then fail closed
static double MAXCOEFW = 0;      // A5: largest absolute width of any shifted coefficient (reported)   // diagnostic: "FIXSTEP h" turns CAPD step control off and uses a fixed step h
static int STEPLOG = 0;   // "STEPLOG 1": count CAPD steps per segment; "STEPLOG 2": also print each step (probe)
static std::vector<MpInterval> COEF;
// Per-segment checkpoint ("CKPT path"): each finished segment matrix is appended as exact hex (8 intervals) and
// reloaded on restart, so an interrupted row resumes with bit-identical values (no recomputation, no rounding).
static std::string CKPT_PATH;
static std::map<std::string, std::vector<std::string>> CKPT;   // "loop#idx" -> 16 hex endpoints

struct Vertex { CI t; std::vector<CI> E; };

// transport Phi = I (and E from its value at a) along the straight segment a -> b
static M2 segment(const Vertex& a, const Vertex& b) {
  capd::MpIMap map(field, 8 + 2 * NE, 8 + 2 * NE, 4 + NPAR_COEF);
  map.setParameter(0, a.t.re); map.setParameter(1, a.t.im); map.setParameter(2, b.t.re); map.setParameter(3, b.t.im);
  for (int k = 0; k < NPAR_COEF; ++k) map.setParameter(4 + k, COEF[k]);
  capd::MpIOdeSolver solver(map, ORDER);
  if (TOL > 0) { solver.setAbsoluteTolerance(TOL); solver.setRelativeTolerance(TOL); }  // step size only; rigour unaffected
  if (FIXSTEP > 0) { solver.turnOffStepControl(); solver.setStep(MpInterval(FIXSTEP)); }
  capd::MpITimeMap tm(solver);
  capd::MpIVector x(8 + 2 * NE);
  x[0] = 1; x[6] = 1;
  for (int k = 0; k < NE; ++k) { x[8 + 2 * k] = a.E[k].re; x[9 + 2 * k] = a.E[k].im; }
  capd::MpC0Rect2Set set(x, MpInterval(0));
  capd::MpIVector y;
  if (STEPLOG) {
    tm.stopAfterStep(true); long steps = 0;
    auto w0 = std::chrono::steady_clock::now();
    do {
      y = tm(MpInterval(1), set); ++steps;
      if (STEPLOG >= 2) {
        double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - w0).count();
        std::cerr << "    step " << steps << " s=" << hexof(set.getCurrentTime().rightBound()) << " wall " << el << std::endl;
      }
    } while (!tm.completed());
    std::cerr << "    steps " << steps << std::endl;
  } else {
    y = tm(MpInterval(1), set);
  }
  capd_proof::require_finite_all(y, "segment transport");
  // consistency: the transported E must overlap the independently enclosed E at b (single-valued exp)
  for (int k = 0; k < NE; ++k) {
    MpInterval er = y[8 + 2 * k], ei = y[9 + 2 * k];
    if (capd_proof::certainly_disjoint(er, b.E[k].re) || capd_proof::certainly_disjoint(ei, b.E[k].im))
      throw std::runtime_error("transported E disagrees with exp(w(b)): field/exp-factor mismatch (fail closed)");
  }
  M2 m; m.a[0][0] = {y[0], y[1]}; m.a[0][1] = {y[2], y[3]}; m.a[1][0] = {y[4], y[5]}; m.a[1][1] = {y[6], y[7]};
  return m;
}

#ifdef LOCAL_SHIFT
// ---- A5: local re-expansion. For each polynomial P(t) = sum_j c_j t^j (exact base coefficients COEF), the field on a
// sub-segment t = c + D sigma, sigma in [0, 1], uses P(c + D sigma) = sum_k e_k sigma^k with e_k = P^(k)(c)/k! * D^k,
// computed here by Taylor shift (synthetic division) in MPFR complex INTERVAL arithmetic: each e_k is an enclosure, so
// CAPD integrates an interval-parameter family that contains the true field.
struct ShiftGateError : std::logic_error { using std::logic_error::logic_error; };   // never caught by the halving rule
static CI ci(const MpInterval& r) { return {r, MpInterval(0)}; }
static std::vector<CI> base_poly(int i) {
  std::vector<CI> f(POLY_DEG[i] + 1);
  for (int j = 0; j <= POLY_DEG[i]; ++j) { int b = POLY_BASE[POLY_BASE_START[i] + j]; f[j] = ci(b >= 0 ? COEF[b] : MpInterval(0)); }
  return f;
}
static CI horner_c(const std::vector<CI>& f, const CI& z) {
  CI acc = f.back();
  for (int k = (int)f.size() - 2; k >= 0; --k) acc = cadd(cmul(acc, z), f[k]);
  return acc;
}
static bool overlap(const CI& a, const CI& b) {
  return !(capd_proof::certainly_disjoint(a.re, b.re) || capd_proof::certainly_disjoint(a.im, b.im));
}
static std::vector<CI> shifted(int i, const CI& c, const CI& D) {
  std::vector<CI> f = base_poly(i);
  const int d = POLY_DEG[i];
  for (int k = 0; k < d; ++k)                                  // Taylor shift at c (repeated synthetic division)
    for (int j = d - 1; j >= k; --j) f[j] = cadd(f[j], cmul(c, f[j + 1]));
  CI Dk = ci(MpInterval(1));
  for (int k = 0; k <= d; ++k) { f[k] = cmul(f[k], Dk); Dk = cmul(Dk, D); }
  // A5 consistency gate (bridge addition 2): sigma = 0, 0.5, 1 against direct evaluation of the ORIGINAL polynomial
  const std::vector<CI> orig = base_poly(i);
  for (double sg : {0.0, 0.5, 1.0}) {
    CI z = cadd(c, cmul(D, ci(MpInterval(sg))));
    CI direct = horner_c(orig, z), viaShift = horner_c(f, ci(MpInterval(sg)));
    if (!overlap(direct, viaShift)) throw ShiftGateError("A5 shift gate: shifted polynomial disagrees with direct evaluation (fail closed)");
  }
  for (auto& e : f) {
    capd_proof::require_finite(e.re, "shifted coefficient"); capd_proof::require_finite(e.im, "shifted coefficient");
    double w = std::max(toDouble(diam(e.re).rightBound()), toDouble(diam(e.im).rightBound()));
    if (w > MAXCOEFW) MAXCOEFW = w;
  }
  return f;
}
static M2 transport_local(const CI& c, const CI& D) {
  capd::MpIMap map(field, 8, 8, NPAR_MAP);
  map.setParameter(0, D.re); map.setParameter(1, D.im);
  for (int i = 0; i < NPOLY; ++i) {
    std::vector<CI> e = shifted(i, c, D);
    for (int k = 0; k <= POLY_DEG[i]; ++k) { map.setParameter(POLY_SLOT[i] + 2 * k, e[k].re); map.setParameter(POLY_SLOT[i] + 2 * k + 1, e[k].im); }
  }
  capd::MpIOdeSolver solver(map, ORDER);
  if (TOL > 0) { solver.setAbsoluteTolerance(TOL); solver.setRelativeTolerance(TOL); }
  capd::MpITimeMap tm(solver);
  capd::MpIVector x(8); x[0] = 1; x[6] = 1;
  capd::MpC0Rect2Set set(x, MpInterval(0));
  capd::MpIVector y = tm(MpInterval(1), set);
  capd_proof::require_finite_all(y, "sub-segment transport");
  M2 m; m.a[0][0] = {y[0], y[1]}; m.a[0][1] = {y[2], y[3]}; m.a[1][0] = {y[4], y[5]}; m.a[1][1] = {y[6], y[7]};
  return m;
}
static long HALVINGS = 0;
static M2 sub_rule(const CI& c, const CI& D, int depth) {     // pre-registered dyadic halving rule (A5)
  try { return transport_local(c, D); }
  catch (ShiftGateError&) { throw; }
  catch (std::exception& e) {
    if (depth >= MAXHALV) throw;
    ++HALVINGS;
    CI h = cmul(D, ci(MpInterval(1) / 2));
    M2 a = sub_rule(c, h, depth + 1), b = sub_rule(cadd(c, h), h, depth + 1);
    return mmul(b, a);
  }
}
#endif

int main() {
  capd_proof::watchdog(24 * 3600);   // A2 (MR_REPLAY.md): 6 h -> 24 h after C1 hit the 6 h limit (fail-closed)
  std::string line, kw;
  std::map<std::string, M2> loops;
  std::map<std::string, std::string> words;
  std::vector<std::string> order;
  std::set<std::string> only; bool nocert = false;
  while (std::getline(std::cin, line)) {
    std::istringstream in(line); in >> kw;
    if (kw == "PREC") { long p; in >> p; R::setDefaultPrecision(p); }
    else if (kw == "ORDER") { in >> ORDER; }
    else if (kw == "TOL") { in >> TOL; }
    else if (kw == "STEPLOG") { in >> STEPLOG; }
    else if (kw == "FIXSTEP") { in >> FIXSTEP; }
    else if (kw == "SUBSEG") { in >> SUBSEG; if (SUBSEG < 1 || (SUBSEG & (SUBSEG - 1))) throw std::runtime_error("SUBSEG must be a power of 2"); }
    else if (kw == "CKPT") {
      in >> CKPT_PATH;
      std::ifstream cf(CKPT_PATH); std::string cl;
      while (std::getline(cf, cl)) {
        std::istringstream ci(cl); std::string tag, key; ci >> tag >> key;
        if (tag != "SEG") continue;
        std::vector<std::string> h(16); bool full = true;
        for (auto& x : h) if (!(ci >> x)) full = false;
        if (full) CKPT[key] = h;            // a torn last line (interrupted write) is ignored and recomputed
      }
      std::cerr << "checkpoint " << CKPT_PATH << ": " << CKPT.size() << " segments loaded" << std::endl;
    }
    else if (kw == "ONLY") { std::string n; in >> n; only.insert(n); }
    else if (kw == "NOCERT") { nocert = true; }
    else if (kw == "MAT") {   // a loop matrix computed by a separate per-loop run: exact hex enclosures, 8 intervals
      std::string name; in >> name; M2 m;
      for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) {
        std::string a, b, c, d; in >> a >> b >> c >> d; m.a[i][j] = {ival(a, b), ival(c, d)};
      }
      loops[name] = m; order.push_back(name);
    }
    else if (kw == "PAR") { int i; std::string lo, hi; in >> i >> lo >> hi; if ((int)COEF.size() != i) throw std::runtime_error("PAR order"); COEF.push_back(ival(lo, hi)); }
    else if (kw == "LOOP") {
      if ((int)COEF.size() != NPAR_COEF) throw std::runtime_error("coefficient count mismatch");
      std::string name; int nv; in >> name >> nv;
      if (!only.empty() && !only.count(name)) {          // per-loop mode: skip loops not assigned to this process
        for (int v = 0; v < nv; ++v) std::getline(std::cin, line);
        continue;
      }
      std::vector<Vertex> vs;
      for (int v = 0; v < nv; ++v) {
        std::getline(std::cin, line); std::istringstream vi(line); std::string tag, re, im; vi >> tag >> re >> im;
        if (tag != "V") throw std::runtime_error("vertex line expected");
        Vertex V; V.t = {ival(re, re), ival(im, im)};
        for (int k = 0; k < NE; ++k) {
          MpInterval wr, wi; w_at(k, V.t.re, V.t.im, COEF, wr, wi);
          capd_proof::require_finite(wr, "w re"); capd_proof::require_finite(wi, "w im");
          MpInterval m = exp(wr);
          V.E.push_back({m * capd_proof::checked_cos(wi), m * capd_proof::checked_sin(wi)});
        }
        vs.push_back(V);
      }
      M2 M = ident();
      for (int v = 0; v + 1 < nv; ++v) {
        std::string key = name + "#" + std::to_string(v);
        M2 S;
        auto it = CKPT.find(key);
        if (it != CKPT.end()) {
          const auto& h = it->second; int q = 0;
          for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) { S.a[i][j] = {ival(h[q], h[q + 1]), ival(h[q + 2], h[q + 3])}; q += 4; }
          std::cerr << "  " << name << " segment " << v + 1 << "/" << nv - 1 << " (from checkpoint)" << std::endl;
        } else {
#ifdef LOCAL_SHIFT
          {
            CI a = vs[v].t, b = vs[v + 1].t, ba = csub(b, a);
            CI D = cmul(ba, ci(MpInterval(1) / SUBSEG));
            S = ident();
            for (int j = 0; j < SUBSEG; ++j) {
              CI c = cadd(a, cmul(ba, ci(MpInterval(j) / SUBSEG)));
              S = mmul(sub_rule(c, D, 0), S);
              if (STEPLOG) std::cerr << "    sub " << j + 1 << "/" << SUBSEG << " halvings " << HALVINGS << " maxcoefw " << MAXCOEFW << std::endl;
            }
          }
#else
          S = segment(vs[v], vs[v + 1]);
#endif
          if (!CKPT_PATH.empty()) {
            FILE* f = std::fopen(CKPT_PATH.c_str(), "a");
            if (!f) throw std::runtime_error("cannot append checkpoint " + CKPT_PATH);
            std::string ln = "SEG " + key;
            for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j)
              ln += " " + hexof(S.a[i][j].re.leftBound()) + " " + hexof(S.a[i][j].re.rightBound()) + " " +
                    hexof(S.a[i][j].im.leftBound()) + " " + hexof(S.a[i][j].im.rightBound());
            std::fprintf(f, "%s\n", ln.c_str()); std::fflush(f); std::fclose(f);
          }
          std::cerr << "  " << name << " segment " << v + 1 << "/" << nv - 1 << std::endl;
        }
        M = mmul(S, M);   // later segments act on the left
      }
      loops[name] = M; order.push_back(name);
      std::cerr << "loop " << name << " done\n";
    }
    else if (kw == "WORD") { std::string w, expr; in >> w >> expr; words[w] = expr; }
    else if (kw == "END") break;
  }
  for (auto& n : order) {
    const M2& M = loops[n];
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) {
      out("LOOP " + n + " M" + std::to_string(i) + std::to_string(j) + "re", M.a[i][j].re);
      out("LOOP " + n + " M" + std::to_string(i) + std::to_string(j) + "im", M.a[i][j].im);
    }
  }
#ifdef LOCAL_SHIFT
  std::cout << "A5_HALVINGS " << HALVINGS << "\nA5_MAX_SHIFTED_COEF_WIDTH " << MAXCOEFW << "\n";
#endif
  if (nocert) { std::cout << "VERDICT LOOPS_ONLY\n"; return 0; }
  auto elem = [&](const std::string& expr) {          // "a*b*c" -> M_a M_b M_c (same convention as v1/v2)
    std::vector<std::string> parts; std::string cur;
    for (char ch : expr) { if (ch == '*') { parts.push_back(cur); cur.clear(); } else cur += ch; }
    parts.push_back(cur);
    M2 Y = loops.at(parts[0]);
    for (size_t k = 1; k < parts.size(); ++k) Y = mmul(Y, loops.at(parts[k]));
    return Y;
  };
  M2 g = elem(words.at("g")), h = elem(words.at("h"));
  for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) {
    std::string ij = std::to_string(i) + std::to_string(j);
    out("G" + ij + "re", g.a[i][j].re); out("G" + ij + "im", g.a[i][j].im);
    out("H" + ij + "re", h.a[i][j].re); out("H" + ij + "im", h.a[i][j].im);
  }
  CI trg = mtr(g), trh = mtr(h), dg = mdet(g), dh = mdet(h);
  CI wg = cdiv(cmul(trg, trg), dg), wh = cdiv(cmul(trh, trh), dh);
  CI c = mtr(mmul(mmul(g, h), mmul(minv(g), minv(h))));
  out("tr_g_re", trg.re); out("tr_g_im", trg.im); out("tr_h_re", trh.re); out("tr_h_im", trh.im);
  out("det_g_re", dg.re); out("det_g_im", dg.im); out("det_h_re", dh.re); out("det_h_im", dh.im);
  out("w_g_re", wg.re); out("w_g_im", wg.im); out("w_h_re", wh.re); out("w_h_im", wh.im);
  out("tr_comm_re", c.re); out("tr_comm_im", c.im);
  // GL(2) certificate, exactly as v2's certificate_gl2: w = tr^2/det certainly outside [0,4] for g and h, and
  // tr[g,h] certainly != 2.  Every decision through the capd_proof helpers (finite endpoints, fail closed).
  const MpInterval zero(0), four(4), two(2);
  auto outside04 = [&](const CI& w) {
    return capd_proof::certainly_disjoint(w.im, zero) || capd_proof::certainly_less(w.re, zero) ||
           capd_proof::certainly_less(four, w.re);
  };
  bool lox_g = outside04(wg), lox_h = outside04(wh);
  bool ne2 = capd_proof::certainly_disjoint(c.re, two) || capd_proof::certainly_disjoint(c.im, zero);
  std::cout << "LOX_G " << lox_g << "\nLOX_H " << lox_h << "\nCOMM_NE_2 " << ne2 << "\n";
  std::cout << "VERDICT " << ((lox_g && lox_h && ne2) ? "REPLAYED" : "NOT_REPLAYED") << "\n";
  return 0;
}
