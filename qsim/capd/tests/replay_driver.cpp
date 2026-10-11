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
static bool STEPLOG = false;   // "STEPLOG 1": count CAPD steps per segment (stopAfterStep loop; opt-in)
static std::vector<MpInterval> COEF;

struct Vertex { CI t; std::vector<CI> E; };

// transport Phi = I (and E from its value at a) along the straight segment a -> b
static M2 segment(const Vertex& a, const Vertex& b) {
  capd::MpIMap map(field, 8 + 2 * NE, 8 + 2 * NE, 4 + NPAR_COEF);
  map.setParameter(0, a.t.re); map.setParameter(1, a.t.im); map.setParameter(2, b.t.re); map.setParameter(3, b.t.im);
  for (int k = 0; k < NPAR_COEF; ++k) map.setParameter(4 + k, COEF[k]);
  capd::MpIOdeSolver solver(map, ORDER);
  if (TOL > 0) { solver.setAbsoluteTolerance(TOL); solver.setRelativeTolerance(TOL); }  // step size only; rigour unaffected
  capd::MpITimeMap tm(solver);
  capd::MpIVector x(8 + 2 * NE);
  x[0] = 1; x[6] = 1;
  for (int k = 0; k < NE; ++k) { x[8 + 2 * k] = a.E[k].re; x[9 + 2 * k] = a.E[k].im; }
  capd::MpC0Rect2Set set(x, MpInterval(0));
  capd::MpIVector y;
  if (STEPLOG) {
    tm.stopAfterStep(true); long steps = 0;
    do { y = tm(MpInterval(1), set); ++steps; } while (!tm.completed());
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

int main() {
  capd_proof::watchdog(6 * 3600);
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
    else if (kw == "STEPLOG") { int v; in >> v; STEPLOG = v != 0; }
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
        M = mmul(segment(vs[v], vs[v + 1]), M);   // later segments act on the left
        std::cerr << "  " << name << " segment " << v + 1 << "/" << nv - 1 << std::endl;
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
