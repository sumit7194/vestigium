// mn_common.h -- shared by mn_sec (copied VERBATIM from mn_so.cpp, where the long runs use the same code): rational
// enclosures, the 8-D field, aux, domain and lift maps, S4 (B9/B18/B18a) and S9, the checkpoint file, and the state I/O.
#pragma once
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "so_set.h"
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpFloat R; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
using so::RepA;
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q); if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s); mpq_canonicalize(q);
  R lo, hi; mpfr_set_q(lo.*RepA::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepA::rep, q, MPFR_RNDU); mpq_clear(q); return MpInterval(lo, hi);
}
static double w(const MpInterval& v) { return so::hi(v) - so::lo(v); }
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
#include "../gen/mn_field8.h"
static MpInterval MNC[5];
void mn8_vf(Node, Node in[], int, Node o[], int, Node par[], int) { Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; mn8_field<Node>(in, o, c); }
void aux_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]}; mn8_aux<Node>(z, o, c); }
void dom_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}, z[8] = {in[0], in[1], in[0], in[0], in[0], in[0], in[0], in[0]}; mn8_domain<Node>(z, o, c); }
void lift_vf(Node, Node in[], int, Node o[], int, Node par[], int) {     // identical to mn_lift_so (gated)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c);
  Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1];
  Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c);
  o[0] = x; o[1] = zero; o[2] = px; o[3] = sqrt(rad); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i];
}
// ---- S4 (B9 predicate; B18/B18a: structured form, mean-value per sub-box, bisection to depth 12) and S9
static std::unique_ptr<capd::MpIMap> DOM;
static const int S4_DEPTH = 12; static long S4_LEAVES = 0; static double S4_GMIN = 1e300;
static bool certify(const MpInterval& x, const MpInterval& y, int which, int depth) {
  bool ok = false; MpInterval lowg;
  try {
    MpInterval z(0), in[8] = {x, y, z, z, z, z, z, z}, out[2];
    mn8_domain<MpInterval>(in, out, MNC);
    IV box(2), c(2); box[0] = x; box[1] = y; c[0] = x.mid(); c[1] = y.mid(); IM D(2, 2); (*DOM)(box, D); IV vc = (*DOM)(c);
    for (int i = 0; i < 2; ++i) { MpInterval mv = vc[i] + D[i][0] * (x - c[0]) + D[i][1] * (y - c[1]);
      if (!intersection(out[i], mv, out[i])) throw std::runtime_error("S4: empty intersection of two enclosures (BUG)"); }
    capd_proof::require_finite(out[which], "S4 domain function");
    ok = out[which].leftBound() > 0 && (which == 0 || out[0].leftBound() > 0); lowg = out[1];
  } catch (std::exception& e) { if (std::string(e.what()).find("BUG") != std::string::npos) throw; ok = false; }
  if (ok) { ++S4_LEAVES; if (which == 1) S4_GMIN = std::min(S4_GMIN, so::lo(lowg)); return true; }
  if (depth >= S4_DEPTH) return false;
  bool sx = w(x) >= w(y); MpInterval a = sx ? x : y, m = MpInterval(a.mid().leftBound()), lo(a.leftBound(), m.rightBound()), hi(m.leftBound(), a.rightBound());
  return sx ? (certify(lo, y, which, depth + 1) && certify(hi, y, which, depth + 1)) : (certify(x, lo, which, depth + 1) && certify(x, hi, which, depth + 1));
}
static void mn_domain(const IV& b) {
  capd_proof::require_finite_all(b, "S4 enclosure");
  const MpInterval &x = b[0], &y = b[1];
  if (!((x - 1).leftBound() >= MpInterval(1) / 20)) throw std::runtime_error("S4: x - 1 < 0.05 possible");
  if (!((x * x + y * y - 1).leftBound() >= MpInterval(1) / 4)) throw std::runtime_error("S4: R^2 < 0.25 possible");
  if (!((1 - y * y).leftBound() > 0)) throw std::runtime_error("S4: 1 - y^2 > 0 not certified");
  if (!certify(x, y, 0, 0)) throw std::runtime_error("S4: B > 0 (det g < 0) not certified at the depth cap");
  MpInterval dd = MpInterval(1) / 40, ir(-dd.rightBound(), dd.rightBound());
  if (!certify(x + ir, y + ir, 1, 0)) throw std::runtime_error("S4: g_phiphi > 0 on the inflated box not certified at the depth cap");
}
static void s9(const IV& b) { MpInterval in[4] = {b[0], b[1], b[2], b[3]}, out[1]; mn_H<MpInterval>(in, out, MNC);
  if (!out[0].contains(MpInterval(-1) / 2)) throw std::runtime_error("S9: enclosure misses H = -1/2 (BUG)"); }
// ---- checkpoint file (time checkpoints only)
struct Checkpoint { std::string kind; double t; IV u1, u2, nH; double tu1, tu2; double g[7]; double centre[4]; };
static std::vector<Checkpoint> read_cps(const char* path) {
  std::ifstream in(path); std::vector<Checkpoint> v; std::string kind;
  while (in >> kind) { Checkpoint c; c.kind = kind; in >> c.t;
    for (IV* u : {&c.u1, &c.u2, &c.nH}) { *u = IV(8); for (int i = 0; i < 8; ++i) { double x; in >> x; (*u)[i] = MpInterval(x); } }
    in >> c.tu1 >> c.tu2; for (double& g : c.g) in >> g; for (double& x : c.centre) in >> x; v.push_back(c); }
  return v;
}
// ---- state serialisation (MPFR hex, exact round trip)
static std::string hx(const MpInterval& v) { char *a = nullptr, *b = nullptr; mpfr_asprintf(&a, "%Ra", v.leftBound().*RepA::rep); mpfr_asprintf(&b, "%Ra", v.rightBound().*RepA::rep);
  std::string s = std::string(a) + " " + b; mpfr_free_str(a); mpfr_free_str(b); return s; }
static MpInterval unhx(std::istream& in) { std::string a, b; in >> a >> b; R lo, hi;
  if (mpfr_set_str(lo.*RepA::rep, a.c_str(), 0, MPFR_RNDN) || mpfr_set_str(hi.*RepA::rep, b.c_str(), 0, MPFR_RNDN)) throw std::runtime_error("state: bad hex");
  return MpInterval(lo, hi); }
static MpInterval LAST_H(0);                                     // the solver's previous step (restored on resume: determinism)
static void save(const char* path, const so::Set& X, long steps, size_t next_cp) {
  std::string tmp = std::string(path) + ".tmp"; std::ofstream o(tmp);
  o << steps << " " << next_cp << " " << hx(X.t) << " " << hx(LAST_H) << "\n";
  for (int i = 0; i < 8; ++i) o << hx(X.x[i]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) o << hx(X.C[i][a]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) o << hx(X.H[i][a][b]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) o << hx(X.B[i][j]) << " "; o << "\n";
  for (int i = 0; i < 8; ++i) o << hx(X.re[i]) << " "; o << "\nEND\n"; o.close();
  std::rename(tmp.c_str(), path);                                    // atomic replace
}
static bool load(const char* path, so::Set& X, long& steps, size_t& next_cp) {
  std::ifstream in(path); if (!in) return false;
  in >> steps >> next_cp; X.t = unhx(in); LAST_H = unhx(in);
  for (int i = 0; i < 8; ++i) X.x[i] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) X.C[i][a] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) X.H[i][a][b] = unhx(in);
  for (int i = 0; i < 8; ++i) for (int j = 0; j < 8; ++j) X.B[i][j] = unhx(in);
  for (int i = 0; i < 8; ++i) X.re[i] = unhx(in);
  std::string end; in >> end; if (end != "END") throw std::runtime_error("state: truncated file");
  return true;
}

