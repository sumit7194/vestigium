// hs_cover.cpp -- phase-2 covering-relation checker (PREREG_chaos_horseshoe_phase2.md; T0_HYPOTHESES.md).
// Generic planar t-set coverings for a Poincare map, on MPFR intervals only, under proof_guard.h.
//
// A t-set N is given in SECTION coordinates w (2-D) by an exact rational centre c and frame vectors U, S:
//   |N| = { c + u U + s S : |u| <= 1, |s| <= 1 },  left side N^l = {u <= -1},  right side N^r = {u >= 1},
// with the exact inverse chart (u, s) = Ainv (w - c) supplied by the spec (python computes it in exact rationals).
// Covering N_i => N_j (AZ 2001 Def. 2, as fixed by B8):
//   (a) every image box B of a piece of |N_i| misses F_j = {|u_j| <= 1, |s_j| >= 1}: certified if u_j(B) < -1 or
//       u_j(B) > 1 or |s_j(B)| < 1; the stronger |s_j(B)| < 1 is reported separately (data);
//   (b) both edge images certified inside the open opposite sides, one consistent orientation.
// Every rational in the spec is "p/q" and is enclosed outward from an exact mpq (no decimal parsing of floats).
// A piece whose Poincare map or replay throws FAILS (it is never skipped).
//
// Sets: MpC0TripletonSet (Lohner C0 tripleton). CAPD 2f06098 Hermite-Obreshkov sets (C0HO*) do not compile with MPFR
// scalars (HOData.h: ScalarType(sign)/binomial(...) is ambiguous for MpReal), so the HO set of the Rossler example
// is replaced by the plain tripleton; this changes enclosure tightness only, never the decisions logic.
// Systems: rossler (dim 3, section x=0 MinusPlus, w = (y, z)); hh (dim 4, section x=0 MinusPlus, w = (y, p_y),
// p_x lifted by the positive root of the energy constraint, radicand certified > 0; S9 checks).
//
// Commands in the spec (one per line, '#' comments):
//   system rossler|hh     prec <bits>     order <n>     iter <n>     param <name> <p/q>
//   tset <name> cy cw Uy Uw Sy Sw A11 A12 A21 A22 [special capL capR]   (all p/q; special = AZ M3 sides)
//   cover <src> <tgt> <nu> <ns> <ne>                         generic Def. 2 check, adaptive bisection within caps
//   caps <maxleaf_a> <maxleaf_edge>                          (default 65536, 4096 = the prereg 3.6 ladder)
//   ex_trap <l> <r> <bot> <top> <pieces>                     Rossler example: P(W) inside int W  (iteration 1)
//   ex_edge <name> <y> <bot> <top> <less|greater> <bound>    Rossler example: pi_y P^iter({y} x Z) vs bound
//   ex_cone <l> <r> <bot> <top> <pieces> <qz>                Rossler example: cone condition, Q = diag(1, qz)
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <gmp.h>
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <chrono>
#include <unistd.h>
#include <sstream>
#include <string>
#include <vector>

using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;
typedef capd::MpIVector IV;
typedef capd::MpIMatrix IM;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static MpInterval Q(const std::string& s) {
  mpq_t q; mpq_init(q);
  if (mpq_set_str(q, s.c_str(), 10) != 0) throw std::runtime_error("bad rational: " + s);
  mpq_canonicalize(q);
  R lo, hi;                                                 // default precision; directed rounding by MPFR itself
  mpfr_set_q(lo.*RepAccess::rep, q, MPFR_RNDD); mpfr_set_q(hi.*RepAccess::rep, q, MPFR_RNDU);
  mpq_clear(q);
  if (!(lo <= hi)) throw std::runtime_error("rational enclosure failed: " + s);
  return MpInterval(lo, hi);
}
static std::string dec(const R& r) { char* s = nullptr; mpfr_asprintf(&s, "%.12Re", r.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o; }
static std::string iv(const MpInterval& x) { return "[" + dec(x.leftBound()) + "," + dec(x.rightBound()) + "]"; }

// ------------------------------------------------------------------ vector fields
void rossler_vf(Node, Node in[], int, Node o[], int, Node par[], int) {
  o[0] = -(in[1] + in[2]); o[1] = in[0] + par[1] * in[1]; o[2] = par[1] + in[2] * (in[0] - par[0]);
}
void hh_vf(Node, Node in[], int, Node o[], int, Node[], int) {      // H = (px^2+py^2)/2 + (x^2+y^2)/2 + x^2 y - y^3/3
  o[0] = in[2]; o[1] = in[3]; o[2] = -in[0] - 2 * in[0] * in[1]; o[3] = -in[1] - in[0] * in[0] + in[1] * in[1];
}

struct TSet {
  MpInterval c[2], U[2], S[2], A[2][2];
  bool special = false; MpInterval capL, capR;   // AZ M3 sides: left = {u<=-1} U {w1>=capL}, right = {u>=1} n {w1<=capR}
};
// side tests on an image box (u, s in the target's chart, w1 = second section coordinate)
static bool in_left(const TSet& t, const MpInterval& u, const MpInterval& w1) {
  return u.rightBound() < -1 || (t.special && w1.leftBound() > t.capL.rightBound());
}
static bool in_right(const TSet& t, const MpInterval& u, const MpInterval& w1) {
  return u.leftBound() > 1 && (!t.special || w1.rightBound() < t.capR.leftBound());
}
// Def. 2(a): box misses F = R^2 minus (left u |N| u right)
static bool miss_F(const TSet& t, const MpInterval& u, const MpInterval& s, const MpInterval& w1) {
  bool s_in = s.leftBound() > -1 && s.rightBound() < 1;
  if (!t.special) return u.rightBound() < -1 || u.leftBound() > 1 || s_in;
  return (s_in && u.rightBound() < 1) || in_left(t, u, w1) || in_right(t, u, w1) ||
         (s_in && w1.rightBound() < t.capR.leftBound());
}
struct Sys {
  std::string name; int dim = 0, wi[2] = {0, 0};
  MpInterval level;                                   // hh energy
  bool hamiltonian = false;
};

static Sys SYS; static std::map<std::string, MpInterval> PAR; static std::map<std::string, TSet> TS;
static int ORDER = 20, ITER = 1;

static MpInterval hh_H(const IV& x) {
  return (x[2] * x[2] + x[3] * x[3]) / 2 + (x[0] * x[0] + x[1] * x[1]) / 2 + x[0] * x[0] * x[1] - x[1] * x[1] * x[1] / 3;
}
// radicand of p_x on {x = 0}: 2h - p_y^2 - y^2 + 2 y^3 / 3  (derived from H; AZ's printed y^3/3 is a slip, B7)
static MpInterval hh_rad(const MpInterval& y, const MpInterval& py) { return 2 * SYS.level - py * py - y * y + 2 * y * y * y / 3; }

// chart: section point for (u, s) intervals, as a set centre + frame (affine, no hull of the parallelogram)
struct Piece { IV x0; IM C; IV r0; };
static Piece lift(const TSet& t, const MpInterval& u, const MpInterval& s) {
  int d = SYS.dim; Piece p{IV(d), IM(d, d), IV(d)};
  MpInterval um = u.mid(), sm = s.mid(), ur = u - um, sr = s - sm;          // ur, sr: symmetric radii intervals
  MpInterval w[2], wh[2];
  for (int k = 0; k < 2; ++k) { w[k] = t.c[k] + um * t.U[k] + sm * t.S[k]; wh[k] = w[k] + ur * t.U[k] + sr * t.S[k]; }
  for (int k = 0; k < 2; ++k) { p.x0[SYS.wi[k]] = w[k]; p.C[SYS.wi[k]][0] = t.U[k]; p.C[SYS.wi[k]][1] = t.S[k]; }
  p.r0[0] = ur; p.r0[1] = sr;
  if (SYS.name == "rossler") { p.C[0][2] = 1; p.r0[2] = 0; }
  else {                                                                      // hh: p_x by the positive root
    MpInterval rad = hh_rad(wh[0], wh[1]);
    if (!capd_proof::certainly_positive(rad)) throw std::runtime_error("S9: radicand not certified > 0");
    MpInterval px = sqrt(rad), pm = px.mid();
    p.x0[2] = pm; p.C[2][2] = 1; p.r0[2] = px - pm; p.C[0][3] = 1; p.r0[3] = 0;
  }
  return p;
}
static void chart(const TSet& t, const MpInterval w[2], MpInterval& u, MpInterval& s) {
  MpInterval d0 = w[0] - t.c[0], d1 = w[1] - t.c[1];
  u = t.A[0][0] * d0 + t.A[0][1] * d1; s = t.A[1][0] * d0 + t.A[1][1] * d1;
}

struct Engine {
  capd::MpIMap f; capd::MpIOdeSolver solver; capd::MpICoordinateSection section; capd::MpIPoincareMap pm;
  capd::MpIOdeSolver rsolver;
  Engine(capd::MpIMap ff) : f(ff), solver(f, ORDER), section(SYS.dim, 0), pm(solver, section, capd::poincare::MinusPlus),
                            rsolver(f, ORDER) {}
};

// S9 in-flow replay (hamiltonian systems): every step enclosure up to T_hi must contain the energy level
// Per-piece cap (opt-in, "piececap <max_replay_steps> <max_seconds>"; 0 = off): a piece whose in-flow replay needs
// more steps or wall time than this THROWS, so the piece fails closed and is bisected or counted as a failure. The
// Poincare-map call itself is bounded by CAPD's own "minimal time step reached" exception on step collapse.
static long PIECE_MAXSTEPS = 0; static double PIECE_MAXSEC = 0;
static void replay(Engine& E, const Piece& p, const MpInterval& rt, long& nsteps) {
  const auto t0 = std::chrono::steady_clock::now(); long mysteps = 0;
  capd::MpC0TripletonSet s(p.x0, p.C, p.r0);
  capd::MpITimeMap tm(E.rsolver);                       // fresh time map per replay (no carried dense-output state)
  tm.stopAfterStep(true);
  MpInterval T(rt.rightBound());
  do {
    tm(T, s);
    IV b = s.getLastEnclosure();
    capd_proof::require_finite_all(b, "replay enclosure");
    MpInterval h = hh_H(b);
    if (!(h.contains(SYS.level))) throw std::runtime_error("S9: step enclosure misses the energy level (BUG)");
    ++nsteps; ++mysteps;
    if (PIECE_MAXSTEPS > 0 && mysteps > PIECE_MAXSTEPS) throw std::runtime_error("piece cap: replay steps exceeded");
    if (PIECE_MAXSEC > 0 && std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() > PIECE_MAXSEC)
      throw std::runtime_error("piece cap: replay wall time exceeded");
  } while (!tm.completed());
}

// map one piece; returns image in section coordinates; throws on any failure
static void image(Engine& E, const Piece& p, MpInterval w[2], MpInterval& rt, long& nsteps) {
  capd::MpC0TripletonSet s(p.x0, p.C, p.r0);
  IV y = E.pm(s, rt, ITER);
  capd_proof::require_finite_all(y, "image");
  capd_proof::require_finite(rt, "return time");
  if (SYS.hamiltonian) {
    if (!capd_proof::certainly_positive(y[2])) throw std::runtime_error("S9: p_x at return not certified > 0");
    if (!hh_H(y).contains(SYS.level)) throw std::runtime_error("S9: return enclosure misses the energy level (BUG)");
    replay(E, p, rt, nsteps);
  }
  w[0] = y[SYS.wi[0]]; w[1] = y[SYS.wi[1]];
}

static bool lt(const MpInterval& a, double b) { return a.rightBound() < b; }
static bool gt(const MpInterval& a, double b) { return a.leftBound() > b; }

// Adaptive version (prereg 3.6 ladder): a failing (or throwing) piece is bisected -- along the source's unstable
// direction u first (u-depth may lead s-depth by at most 3), then along s -- until it passes, or the per-covering
// caps are hit: <= MAXLEAF_A leaves for (a) (ladder: 2^16) and <= MAXLEAF_E leaves per edge for (b) (ladder: 2^12).
// A leaf that still fails at the caps is a FINAL failure; the covering is then "not certified within budget"
// unless some leaf failed CERTIFIABLY (recorded separately: certified_fail_a / certified_fail_b).
struct CovStat {
  long leaves = 0, fail = 0, strong_fail = 0, cert_fail = 0, nsteps = 0, maxdepth = 0; bool first = true; MpInterval rt;
  void hull(const MpInterval& r) { if (first) { rt = r; first = false; } else rt = intervalHull(rt, r); }
};
static long MAXLEAF_A = 65536, MAXLEAF_E = 4096;
// Depth limits (B13 fix): the leaf caps above count FINISHED leaves only, so without a depth bound a persistently
// failing box descended without limit. A box is bisected at most MAXDEPTH_A times (u- plus s-splits) below its
// top-level piece, an edge piece at most MAXDEPTH_E times; beyond that it is a final (counted) failure.
static int MAXDEPTH_A = 16, MAXDEPTH_E = 12;
// Optional checkpoint/restart and chunking (B13; opt-in, absent = original behaviour):
//   checkpoint <path>  every finished TOP-LEVEL (a)-piece is appended (with its FAILPIECE lines) and fsync'ed;
//                      a restart with the same spec reloads finished pieces instead of recomputing them.
//   arange <lo> <hi>   (a) only for top-level u-index i in [lo, hi)   (chunking; the caps apply per process)
//   noedges            skip (b) in this process (another chunk does the edges)
static std::string CKPT; static int A_LO = 0, A_HI = -1; static bool DO_EDGES = true; static std::string PIECE_FAILS;
static void failline(const std::string& l) { std::cout << l; PIECE_FAILS += l; }
static std::string hexr(const R& r) { char* c = nullptr; mpfr_asprintf(&c, "%Ra", r.*RepAccess::rep); std::string o(c); mpfr_free_str(c); return o; }
static R fromhex(const std::string& h) { R x; if (mpfr_set_str(x.*RepAccess::rep, h.c_str(), 0, MPFR_RNDN) != 0) throw std::runtime_error("ckpt: bad hex " + h); return x; }

// (a) on [u] x [s]; returns true if certified
static bool cover_a(Engine& E, const TSet& Ni, const TSet& Nj, const std::string& tag, MpInterval u, MpInterval s,
                    int du, int ds, CovStat& st) {
  bool ok = false, strong = false, threw = false; std::string why;
  try {
    MpInterval w[2], rt, uj, sj; image(E, lift(Ni, u, s), w, rt, st.nsteps); chart(Nj, w, uj, sj);
    strong = gt(sj, -1.0) && lt(sj, 1.0);
    ok = miss_F(Nj, uj, sj, w[1]);
    st.hull(rt);
    if (!ok) why = "u=" + iv(uj) + " s=" + iv(sj);
  } catch (std::exception& e) { why = e.what(); threw = true; }
  if (ok) { ++st.leaves; if (!strong) ++st.strong_fail; st.maxdepth = std::max<long>(st.maxdepth, du + ds); return true; }
  if (du + ds < MAXDEPTH_A && st.leaves + 2 <= MAXLEAF_A) {   // bisect within the depth and leaf caps
    bool along_u = (du <= ds + 3);
    MpInterval a = along_u ? u : s, m = MpInterval(a.mid().leftBound());
    MpInterval lo(a.leftBound(), m.rightBound()), hi(m.leftBound(), a.rightBound());
    bool r1 = along_u ? cover_a(E, Ni, Nj, tag, lo, s, du + 1, ds, st) : cover_a(E, Ni, Nj, tag, u, lo, du, ds + 1, st);
    bool r2 = along_u ? cover_a(E, Ni, Nj, tag, hi, s, du + 1, ds, st) : cover_a(E, Ni, Nj, tag, u, hi, du, ds + 1, st);
    return r1 && r2;
  }
  ++st.leaves; ++st.fail; ++st.strong_fail; (void)threw;
  failline("FAILPIECE " + tag + " a depth=" + std::to_string(du + ds) + (du + ds >= MAXDEPTH_A ? "(depth cap)" : "(leaf cap)") + " u=" + iv(u) + " s=" + iv(s) + " " + why + "\n");
  return false;
}
// (b) one edge piece; land: 0 = left side, 1 = right side, -1 = undecided/failed; counts landings into L/R
static void cover_b(Engine& E, const TSet& Ni, const TSet& Nj, const std::string& tag, int side, MpInterval s, int d,
                    long cnt[2], CovStat& st) {
  std::string why; int land = -1; bool certfail = false;
  try {
    MpInterval w[2], rt, uj, sj; image(E, lift(Ni, MpInterval(side == 0 ? -1 : 1), s), w, rt, st.nsteps); chart(Nj, w, uj, sj);
    if (in_left(Nj, uj, w[1])) land = 0; else if (in_right(Nj, uj, w[1])) land = 1;
    else { why = "u=" + iv(uj) + " w1=" + iv(w[1]); certfail = (gt(uj, -1.0) && lt(uj, 1.0)); }   // certainly in neither side
    st.hull(rt);
  } catch (std::exception& e) { why = e.what(); }
  if (land >= 0) { ++st.leaves; ++cnt[land]; return; }
  if (!certfail && d < MAXDEPTH_E && st.leaves + 2 <= 2 * MAXLEAF_E) {
    MpInterval m = MpInterval(s.mid().leftBound()), lo(s.leftBound(), m.rightBound()), hi(m.leftBound(), s.rightBound());
    cover_b(E, Ni, Nj, tag, side, lo, d + 1, cnt, st); cover_b(E, Ni, Nj, tag, side, hi, d + 1, cnt, st);
    return;
  }
  ++st.leaves; ++st.fail; if (certfail) ++st.cert_fail;
  failline("FAILPIECE " + tag + " b edge=" + (side ? "R" : "L") + " s=" + iv(s) + (certfail ? " CERTIFIED " : " ") + why + "\n");
}

static void do_cover(Engine& E, const std::string& a, const std::string& b, int nu, int ns, int ne) {
  const TSet &Ni = TS.at(a), &Nj = TS.at(b); std::string tag = a + ">" + b;
  CovStat A, Bs; bool oka = true;
  std::map<std::string, std::string> done; std::map<std::string, std::string> donefails;
  if (!CKPT.empty()) {                                   // reload finished pieces of THIS spec (the path is keyed by it)
    std::ifstream ci(CKPT); std::string l;
    while (std::getline(ci, l)) {
      if (l.rfind("F ", 0) == 0) { auto sp = l.find(' ', 2); donefails[l.substr(2, sp - 2)] += l.substr(sp + 1) + "\n"; }
      else if (l.rfind("P ", 0) == 0) { auto sp = l.find(' ', 2); done[l.substr(2, sp - 2)] = l.substr(sp + 1); }
    }
  }
  int ilo = A_LO, ihi = (A_HI < 0 ? nu : std::min(A_HI, nu)); long reloaded = 0;
  for (int i = ilo; i < ihi; ++i) for (int k = 0; k < ns; ++k) {
    std::string key = tag + "/" + std::to_string(i) + "/" + std::to_string(k);
    auto it = done.find(key);
    if (it != done.end()) {                              // P <key> ok leaves fail strong_fail maxdepth nsteps rtflag [lo hi]
      std::istringstream ps(it->second); int ok, rtf; long lv, fl, sf, md, ns_;
      ps >> ok >> lv >> fl >> sf >> md >> ns_ >> rtf;
      A.leaves += lv; A.fail += fl; A.strong_fail += sf; A.maxdepth = std::max(A.maxdepth, md); A.nsteps += ns_;
      if (rtf) { std::string lo, hi; ps >> lo >> hi; A.hull(MpInterval(fromhex(lo), fromhex(hi))); }
      std::cout << donefails[key];
      oka = oka && ok; ++reloaded; continue;
    }
    MpInterval u = -1 + MpInterval(2 * i, 2 * i + 2) / nu, s = -1 + MpInterval(2 * k, 2 * k + 2) / ns;
    CovStat P; P.leaves = A.leaves; const long before = A.leaves;   // piece-local stats; cap accounting continues from A
    PIECE_FAILS.clear();
    bool ok = cover_a(E, Ni, Nj, tag, u, s, 0, 0, P);
    A.leaves = P.leaves; A.fail += P.fail; A.strong_fail += P.strong_fail; A.maxdepth = std::max(A.maxdepth, P.maxdepth);
    A.nsteps += P.nsteps; if (!P.first) A.hull(P.rt);
    oka = ok && oka;
    if (!CKPT.empty()) {
      std::ostringstream o; std::istringstream fs(PIECE_FAILS); std::string fl;
      while (std::getline(fs, fl)) o << "F " << key << " " << fl << "\n";
      o << "P " << key << " " << ok << " " << (P.leaves - before) << " " << P.fail << " "
        << P.strong_fail << " " << P.maxdepth << " " << P.nsteps << " " << (P.first ? 0 : 1);
      if (!P.first) o << " " << hexr(P.rt.leftBound()) << " " << hexr(P.rt.rightBound());
      o << "\n";
      FILE* f = std::fopen(CKPT.c_str(), "a"); std::fputs(o.str().c_str(), f); std::fflush(f); ::fsync(fileno(f)); std::fclose(f);
    }
  }
  long Lto[2] = {0, 0}, Rto[2] = {0, 0};
  if (DO_EDGES) {
    for (int i = 0; i < ne; ++i) cover_b(E, Ni, Nj, tag, 0, -1 + MpInterval(2 * i, 2 * i + 2) / ne, 0, Lto, Bs);
    for (int i = 0; i < ne; ++i) cover_b(E, Ni, Nj, tag, 1, -1 + MpInterval(2 * i, 2 * i + 2) / ne, 0, Rto, Bs);
  }
  // orientation: all left-edge leaves in one side, all right-edge leaves in the other
  bool orient1 = Bs.fail == 0 && Lto[1] == 0 && Rto[0] == 0, orient2 = Bs.fail == 0 && Lto[0] == 0 && Rto[1] == 0;
  bool orient_certfail = (Lto[0] > 0 && Lto[1] > 0) || (Rto[0] > 0 && Rto[1] > 0) ||
                         (Lto[0] > 0 && Rto[0] > 0) || (Lto[1] > 0 && Rto[1] > 0);   // certified landings contradict
  bool okb = DO_EDGES && (orient1 || orient2);         // no edges checked in this process => (b) not certified here
  CovStat T = A; T.hull(Bs.first ? A.rt : Bs.rt);
  std::cout << "COVER " << a << " " << b << " a=" << oka << " b=" << (DO_EDGES ? std::to_string(okb) : std::string("skip"))
            << " strong_a=" << (A.strong_fail == 0)
            << " orient=" << (!DO_EDGES ? "skip" : orient1 ? "LR" : orient2 ? "RL" : "none") << " fail_a=" << A.fail << " fail_b=" << Bs.fail
            << " certified_fail_b=" << Bs.cert_fail << " orient_certified_fail=" << orient_certfail
            << " leaves_a=" << A.leaves << " leaves_b=" << Bs.leaves << " maxdepth_a=" << A.maxdepth
            << " replay_steps=" << A.nsteps + Bs.nsteps
            << " return_time=" << (A.first && Bs.first ? std::string("none") : iv(A.first ? Bs.rt : (Bs.first ? A.rt : intervalHull(A.rt, Bs.rt))))
            << " COVERS=" << (DO_EDGES ? std::to_string(oka && okb) : std::string("chunk-a-only"));
  if (!CKPT.empty() || A_HI >= 0 || !DO_EDGES)
    std::cout << " chunk_a=[" << ilo << "," << ihi << ") edges=" << (DO_EDGES ? "yes" : "no") << " reloaded_pieces=" << reloaded;
  std::cout << "\n";
}

// ---- Rossler example checks (exact port of RosslerChaoticDynamics.cpp, MPFR)
static IV rbox(const MpInterval& y, const MpInterval& z) { IV x(3); x[0] = 0; x[1] = y; x[2] = z; return x; }
static void ex_trap(Engine& E, MpInterval l, MpInterval r, MpInterval bot, MpInterval top, int n) {
  bool res = true; MpInterval p = (r - l) / n;
  for (int i = 0; i < n; ++i) {
    IV x = rbox(l + MpInterval(i, i + 1) * p, MpInterval(bot.leftBound(), top.rightBound()));
    bool ok = false;
    try {
      capd::MpC0TripletonSet s(x); IV y = E.pm(s, 1); capd_proof::require_finite_all(y, "trap");
      ok = y[2].leftBound() > bot.rightBound() && y[2].rightBound() < top.leftBound() &&
           y[1].leftBound() > l.rightBound() && y[1].rightBound() < r.leftBound();
    } catch (std::exception& e) { std::cout << "FAILPIECE trap i=" << i << " " << e.what() << "\n"; }
    if (!ok) std::cout << "FAILPIECE trap i=" << i << "\n";
    res = res && ok;
  }
  std::cout << "EX trap " << res << "\n";
}
static void ex_edge(Engine& E, const std::string& nm, MpInterval y0, MpInterval bot, MpInterval top, const std::string& rel, MpInterval bd) {
  bool ok = false; std::string img;
  try {
    IV x = rbox(y0, MpInterval(bot.leftBound(), top.rightBound()));
    capd::MpC0TripletonSet s(x); IV y = E.pm(s, ITER); capd_proof::require_finite_all(y, "edge");
    ok = rel == "less" ? y[1].rightBound() < bd.leftBound() : y[1].leftBound() > bd.rightBound();
    img = iv(y[1]);
  } catch (std::exception& e) { img = e.what(); }
  std::cout << "EX edge " << nm << " " << ok << " image_y=" << img << "\n";
}
static void ex_cone(Engine& E, MpInterval l, MpInterval r, MpInterval bot, MpInterval top, int n, MpInterval qz) {
  bool res = true; MpInterval p = (r - l) / n;
  IM Qf(3, 3); Qf[1][1] = 1; Qf[2][2] = qz;
  for (int i = 0; i < n && res; ++i) {
    IV x = rbox(l + MpInterval(i, i + 1) * p, MpInterval(bot.leftBound(), top.rightBound()));
    bool ok = false;
    try {
      capd::MpC1Rect2Set s(x); IM mono(3, 3); MpInterval rt;
      IV y = E.pm(s, mono, rt, ITER);
      IM DP = E.pm.computeDP(y, mono, rt);
      IM M = capd::vectalg::Transpose(DP) * Qf * DP - Qf;
      ok = M[1][1].leftBound() > 0 && (M[1][1] * M[2][2] - M[1][2] * M[1][2]).leftBound() > 0;
    } catch (std::exception& e) { std::cout << "FAILPIECE cone i=" << i << " " << e.what() << "\n"; }
    res = res && ok;
  }
  std::cout << "EX cone " << iv(l) << " " << res << "\n";
}

int main(int argc, char** argv) {
  capd_proof::watchdog(48 * 3600);
  if (argc < 2) { std::cerr << "usage: hs_cover spec\n"; return 2; }
  std::ifstream in(argv[1]); std::string line; std::vector<std::vector<std::string>> cmds;
  while (std::getline(in, line)) {
    auto h = line.find('#'); if (h != std::string::npos) line = line.substr(0, h);
    std::istringstream ss(line); std::vector<std::string> t; std::string w; while (ss >> w) t.push_back(w);
    if (!t.empty()) cmds.push_back(t);
  }
  for (auto& t : cmds) if (t[0] == "prec") R::setDefaultPrecision(std::stoi(t[1]));    // precision first
  try {
    std::unique_ptr<Engine> E;
    auto engine = [&]() -> Engine& {
      if (!E) {
        if (SYS.name == "rossler") {
          capd::MpIMap f(rossler_vf, 3, 3, 2); f.setParameter(0, PAR.at("a")); f.setParameter(1, PAR.at("b"));
          E.reset(new Engine(f));
        } else {
          capd::MpIMap f(hh_vf, 4, 4, 0); E.reset(new Engine(f));
        }
      }
      return *E;
    };
    for (auto& t : cmds) {
      const std::string& c = t[0];
      if (c == "prec") { std::cout << "PREC " << t[1] << "\n"; }
      else if (c == "system") {
        SYS.name = t[1];
        if (t[1] == "rossler") { SYS.dim = 3; SYS.wi[0] = 1; SYS.wi[1] = 2; }
        else if (t[1] == "hh") { SYS.dim = 4; SYS.wi[0] = 1; SYS.wi[1] = 3; SYS.hamiltonian = true; }
        else throw std::runtime_error("unknown system");
      }
      else if (c == "order") ORDER = std::stoi(t[1]);
      else if (c == "iter") ITER = std::stoi(t[1]);
      else if (c == "param") { PAR[t[1]] = Q(t[2]); if (t[1] == "level") SYS.level = PAR[t[1]]; }
      else if (c == "tset") {
        TSet s; int k = 2;
        s.c[0] = Q(t[k++]); s.c[1] = Q(t[k++]); s.U[0] = Q(t[k++]); s.U[1] = Q(t[k++]); s.S[0] = Q(t[k++]); s.S[1] = Q(t[k++]);
        s.A[0][0] = Q(t[k++]); s.A[0][1] = Q(t[k++]); s.A[1][0] = Q(t[k++]); s.A[1][1] = Q(t[k++]);
        if ((int)t.size() > k) { if (t[k] != "special") throw std::runtime_error("tset: bad tail");
          s.special = true; s.capL = Q(t[k + 1]); s.capR = Q(t[k + 2]); }
        TS[t[1]] = s;
      }
      else if (c == "checkpoint") CKPT = t[1];
      else if (c == "arange") { A_LO = std::stoi(t[1]); A_HI = std::stoi(t[2]); }
      else if (c == "noedges") DO_EDGES = false;
      else if (c == "piececap") { PIECE_MAXSTEPS = std::stol(t[1]); PIECE_MAXSEC = std::stod(t[2]); }
      else if (c == "depth") { MAXDEPTH_A = std::stoi(t[1]); MAXDEPTH_E = std::stoi(t[2]); }
      else if (c == "caps") { MAXLEAF_A = std::stol(t[1]); MAXLEAF_E = std::stol(t[2]); }
      else if (c == "cover") do_cover(engine(), t[1], t[2], std::stoi(t[3]), std::stoi(t[4]), std::stoi(t[5]));
      else if (c == "ex_trap") ex_trap(engine(), Q(t[1]), Q(t[2]), Q(t[3]), Q(t[4]), std::stoi(t[5]));
      else if (c == "ex_edge") ex_edge(engine(), t[1], Q(t[2]), Q(t[3]), Q(t[4]), t[5], Q(t[6]));
      else if (c == "ex_cone") ex_cone(engine(), Q(t[1]), Q(t[2]), Q(t[3]), Q(t[4]), std::stoi(t[5]), Q(t[6]));
      else throw std::runtime_error("unknown command " + c);
      std::cout.flush();
    }
  } catch (std::exception& e) { std::cout << "FATAL " << e.what() << "\n"; return 1; }
  std::cout << "DONE\n";
  return 0;
}
