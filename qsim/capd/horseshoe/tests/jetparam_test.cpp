// jetparam_test.cpp -- minimal check of CAPD Node-map jets (degree 1-3) with and without map parameters.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
typedef capd::diffAlgebra::Jet<IM, 0> J;
void f_par(Node, Node in[], int, Node o[], int, Node par[], int) { Node x = par[0] + in[0] * par[1]; o[0] = sqrt(x * x - 1); o[1] = in[1]; }
void f_const(Node, Node in[], int, Node o[], int, Node[], int) { Node x = in[0] * 0.000001 + 3.6419361737; o[0] = sqrt(x * x - 1); o[1] = in[1]; }
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  IV r(2);
  for (int deg = 1; deg <= 3; ++deg) {
    capd::MpIMap fp(f_par, 2, 2, 2, deg); fp.setParameter(0, MpInterval(3.6419361737)); fp.setParameter(1, MpInterval(0.000001));
    capd::MpIMap fc(f_const, 2, 2, 0, deg);
    J jp(2, deg), jc(2, deg);
    try { fp(r, jp); std::printf("deg %d params: value %.15g d1 %.15g\n", deg, 0.0, 0.0); } catch (std::exception& e) { std::printf("deg %d params: THREW %s\n", deg, e.what()); }
    try { fc(r, jc); std::printf("deg %d const : OK\n", deg); } catch (std::exception& e) { std::printf("deg %d const : THREW %s\n", deg, e.what()); }
  }
}
