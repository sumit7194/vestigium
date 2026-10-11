// CAPD ODE controls (ODE_CONTROLS.md): rigorous MPFR enclosures printed exactly (%Ra) for the Arb checker
// qsim/capd/ode_controls.py. Vector fields are C++ functors (no formula strings). Every printed interval passes
// capd_proof::require_finite first. Output lines: "<test> <key> <lo> <hi>".
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
#include <iostream>
#include <string>

using capd::MpInterval;
using capd::autodiff::Node;
typedef capd::MpFloat R;

struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static std::string hexof(const R& r) {
  char* s = nullptr; mpfr_asprintf(&s, "%Ra", r.*RepAccess::rep); std::string o(s); mpfr_free_str(s); return o;
}
static void out(const std::string& test, const std::string& key, const MpInterval& x) {
  capd_proof::require_finite(x, key.c_str());
  std::cout << test << " " << key << " " << hexof(x.leftBound()) << " " << hexof(x.rightBound()) << "\n";
}

// ------------------------------------------------------------------ real vector fields
void harm(Node, Node in[], int, Node o[], int, Node[], int) { o[0] = in[1]; o[1] = -in[0]; }
void sqf(Node, Node in[], int, Node o[], int, Node[], int) { o[0] = in[0] * in[0]; }
void hopf(Node, Node in[], int, Node o[], int, Node[], int) {
  Node r2 = in[0] * in[0] + in[1] * in[1];
  o[0] = in[0] - in[1] - in[0] * r2; o[1] = in[0] + in[1] - in[1] * r2;
}

// ------------------------------------------------------------------ complex helpers on Nodes
struct CN { Node re, im; };
static CN mul(const CN& a, const CN& b) { return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re}; }
static CN add(const CN& a, const CN& b) { return {a.re + b.re, a.im + b.im}; }
static CN scl(const CN& a, const Node& k) { return {a.re * k, a.im * k}; }
static CN inv(const CN& a) { Node d = a.re * a.re + a.im * a.im; return {a.re / d, -(a.im / d)}; }
// loop chart: t(s) = c + sigma r ((1 - s^2) + 2 i s)/(1 + s^2);  t'(s) = sigma r (-4s + 2i(1 - s^2))/(1 + s^2)^2
static void chart(const Node& s, const Node& c, const Node& r, const Node& sig, CN& t, CN& tp) {
  Node w = 1 + s * s, w2 = w * w, k = sig * r;
  t = {c + k * ((1 - s * s) / w), k * ((2 * s) / w)};
  tp = {k * ((-4 * s) / w2), k * ((2 * (1 - s * s)) / w2)};
}
// state: Phi entries (00, 01, 10, 11), each re, im -> in[0..7]
static void phi_rows(Node in[], CN row0[2], CN row1[2]) {
  row0[0] = {in[0], in[1]}; row0[1] = {in[2], in[3]}; row1[0] = {in[4], in[5]}; row1[1] = {in[6], in[7]};
}
static void put(Node o[], const CN d0[2], const CN d1[2]) {
  o[0] = d0[0].re; o[1] = d0[0].im; o[2] = d0[1].re; o[3] = d0[1].im;
  o[4] = d1[0].re; o[5] = d1[0].im; o[6] = d1[1].re; o[7] = d1[1].im;
}
// Euler: y'' + (p/t) y' + (q/t^2) y = 0;  params c, r, sigma, p, q
void euler(Node s, Node in[], int, Node o[], int, Node par[], int) {
  CN t, tp; chart(s, par[0], par[1], par[2], t, tp);
  CN it = inv(t), it2 = mul(it, it);
  CN row0[2], row1[2]; phi_rows(in, row0, row1);
  CN d0[2], d1[2];
  for (int j = 0; j < 2; ++j) {
    d0[j] = mul(tp, row1[j]);
    CN a = add(scl(mul(it2, row0[j]), -par[4]), scl(mul(it, row1[j]), -par[3]));
    d1[j] = mul(tp, a);
  }
  put(o, d0, d1);
}
// Airy: y'' = t y;  params c, r, sigma
void airy(Node s, Node in[], int, Node o[], int, Node par[], int) {
  CN t, tp; chart(s, par[0], par[1], par[2], t, tp);
  CN row0[2], row1[2]; phi_rows(in, row0, row1);
  CN d0[2], d1[2];
  for (int j = 0; j < 2; ++j) { d0[j] = mul(tp, row1[j]); d1[j] = mul(tp, mul(t, row0[j])); }
  put(o, d0, d1);
}

// ------------------------------------------------------------------ complex interval 2x2 matrices (CAPD arithmetic)
struct CI { MpInterval re, im; };
static CI cmul(const CI& a, const CI& b) { return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re}; }
static CI cadd(const CI& a, const CI& b) { return {a.re + b.re, a.im + b.im}; }
static CI csub(const CI& a, const CI& b) { return {a.re - b.re, a.im - b.im}; }
static CI cdiv(const CI& a, const CI& b) {
  MpInterval d = b.re * b.re + b.im * b.im;
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
  CI d = mdet(x); CI zero{MpInterval(0), MpInterval(0)}; M2 z;
  z.a[0][0] = cdiv(x.a[1][1], d); z.a[1][1] = cdiv(x.a[0][0], d);
  z.a[0][1] = cdiv(csub(zero, x.a[0][1]), d); z.a[1][0] = cdiv(csub(zero, x.a[1][0]), d);
  return z;
}

typedef void (*Field)(Node, Node[], int, Node[], int, Node[], int);
static const int ORDER = 30;

// transport Phi = I through one chart [s0, s1]
static M2 chart_matrix(Field f, int npar, const MpInterval par[], const MpInterval& s0, const MpInterval& s1) {
  capd::MpIMap map(f, 8, 8, npar);
  for (int k = 0; k < npar; ++k) map.setParameter(k, par[k]);
  capd::MpIOdeSolver solver(map, ORDER);
  capd::MpITimeMap tm(solver);
  capd::MpIVector x(8);
  x[0] = 1; x[6] = 1;
  capd::MpC0Rect2Set set(x, s0);
  capd::MpIVector y = tm(s1, set);
  capd_proof::require_finite_all(y, "chart transport");
  M2 m; m.a[0][0] = {y[0], y[1]}; m.a[0][1] = {y[2], y[3]}; m.a[1][0] = {y[4], y[5]}; m.a[1][1] = {y[6], y[7]};
  return m;
}
// full counterclockwise loop (centre c, radius r) based at c + r:  chart(+1, [0,1]), chart(-1, [-1,1]), chart(+1, [-1,0])
static M2 loop(Field f, MpInterval c, MpInterval r, const MpInterval extra[], int nextra) {
  MpInterval par[5]; par[0] = c; par[1] = r;
  for (int k = 0; k < nextra; ++k) par[3 + k] = extra[k];
  const int np = 3 + nextra;
  par[2] = 1;  M2 a = chart_matrix(f, np, par, MpInterval(0), MpInterval(1));
  par[2] = -1; M2 b = chart_matrix(f, np, par, MpInterval(-1), MpInterval(1));
  par[2] = 1;  M2 d = chart_matrix(f, np, par, MpInterval(-1), MpInterval(0));
  return mmul(d, mmul(b, a));   // later charts act on the left
}
static void out_m(const std::string& test, const M2& m) {
  const char* nm[2][2] = {{"00", "01"}, {"10", "11"}};
  for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) {
    out(test, std::string("M") + nm[i][j] + "re", m.a[i][j].re); out(test, std::string("M") + nm[i][j] + "im", m.a[i][j].im);
  }
  CI tr = mtr(m), de = mdet(m), q = cdiv(cmul(tr, tr), de);
  out(test, "trre", tr.re); out(test, "trim", tr.im); out(test, "detre", de.re); out(test, "detim", de.im);
  out(test, "tr2detre", q.re); out(test, "tr2detim", q.im);
}

int main() {
  capd_proof::watchdog(4 * 3600);  // first run hit a 1800 s watchdog during M4 (fail closed, rc 124)
  R::setDefaultPrecision(256);
  std::cout << "# precision 256, order " << ORDER << "\n";
  const MpInterval eps = MpInterval(R("1e-20"));  // a box half-width (decimal rounded: any fixed value is fine)
  // ---- R1 harmonic, C0, from the box (1,0) +- eps
  for (int T : {1, 10, 100}) {
    capd::MpIMap f(harm, 2, 2, 0); capd::MpIOdeSolver so(f, ORDER); capd::MpITimeMap tm(so);
    capd::MpIVector x(2); x[0] = MpInterval(1) + MpInterval(-1, 1) * eps; x[1] = MpInterval(-1, 1) * eps;
    out("R1_t" + std::to_string(T), "box0", x[0]); out("R1_t" + std::to_string(T), "box1", x[1]);
    capd::MpC0Rect2Set set(x, MpInterval(0)); capd::MpIVector y = tm(MpInterval(T), set);
    out("R1_t" + std::to_string(T), "x", y[0]); out("R1_t" + std::to_string(T), "y", y[1]);
  }
  // ---- R2 x' = x^2, C0 + C1
  {
    capd::MpIMap f(sqf, 1, 1, 0); capd::MpIOdeSolver so(f, ORDER); capd::MpITimeMap tm(so);
    capd::MpIVector x(1); x[0] = MpInterval(R(0.5), R(0.5) + eps.rightBound());
    out("R2", "box0", x[0]);
    capd::MpC1Rect2Set set(x, MpInterval(0)); capd::MpIVector y = tm(MpInterval(3) / 2, set);
    capd::MpIMatrix D = (capd::MpIMatrix)set;
    out("R2", "x", y[0]); out("R2", "dxdx0", D[0][0]);
  }
  // ---- R3 Hopf, C0
  {
    capd::MpIMap f(hopf, 2, 2, 0); capd::MpIOdeSolver so(f, ORDER); capd::MpITimeMap tm(so);
    capd::MpIVector x(2); x[0] = MpInterval(1) / 2 + MpInterval(-1, 1) * eps; x[1] = MpInterval(-1, 1) * eps;
    out("R3", "box0", x[0]); out("R3", "box1", x[1]);
    capd::MpC0Rect2Set set(x, MpInterval(0)); capd::MpIVector y = tm(MpInterval(2), set);
    out("R3", "x", y[0]); out("R3", "y", y[1]);
  }
  // ---- R4 harmonic, C1 from a point (Jacobian is the rotation matrix)
  for (int T : {1, 10}) {
    capd::MpIMap f(harm, 2, 2, 0); capd::MpIOdeSolver so(f, ORDER); capd::MpITimeMap tm(so);
    capd::MpIVector x(2); x[0] = 1; x[1] = MpInterval(0) + MpInterval(-1, 1) * eps;
    capd::MpC1Rect2Set set(x, MpInterval(0)); tm(MpInterval(T), set);
    capd::MpIMatrix D = (capd::MpIMatrix)set;
    std::string t = "R4_t" + std::to_string(T);
    out(t, "D00", D[0][0]); out(t, "D01", D[0][1]); out(t, "D10", D[1][0]); out(t, "D11", D[1][1]);
  }
  // ---- complex monodromy
  const MpInterval p = MpInterval(11) / 12, q = MpInterval(-1) / 12;
  MpInterval pq[2] = {p, q};
  M2 A = loop(euler, MpInterval(0), MpInterval(1), pq, 2);
  out_m("M1_A", A);
  M2 B = loop(euler, MpInterval(1) / 4, MpInterval(3) / 4, pq, 2);
  out_m("M1_B", B);
  M2 C = mmul(mmul(A, B), mmul(minv(A), minv(B)));   // M2: commutator must enclose I
  out_m("M2_comm", C);
  out_m("M3_AA", mmul(A, A));
  out_m("M4_noSing", loop(euler, MpInterval(2), MpInterval(1) / 2, pq, 2));
  out_m("M5_airy", loop(airy, MpInterval(0), MpInterval(3), nullptr, 0));
  // ---- fired control (ii): wrong equation, p + 1e-20
  MpInterval pq2[2] = {p + MpInterval(R("1e-20")), q};
  out_m("CTRL_wrong_p", loop(euler, MpInterval(0), MpInterval(1), pq2, 2));
  std::cout << "# done\n";
  return 0;
}
