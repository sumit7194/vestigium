// jetparam_test3.cpp -- reproduce mn_lift_so's lift_vf step by step under degree-2 jets.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
#include <string>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
typedef capd::diffAlgebra::Jet<IM, 0> J;
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
#include "../gen/mn_field8.h"
static int VAR = 0;
void lv(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]};
  Node x = par[5] + in[0] * par[7], px = par[6] + in[1] * par[7], zero = in[0] * 0;
  for (int i = 0; i < 8; ++i) o[i] = x;
  if (VAR >= 1) { Node xy[2] = {x, zero}, g[3]; mn_lift<Node>(xy, g, c); o[0] = g[0]; o[1] = g[1]; o[2] = g[2];
    if (VAR >= 2) { Node rad = (Node(-1) - g[0] * px * px - Node(2) * g[2]) / g[1]; o[3] = rad;
      if (VAR >= 3) o[3] = sqrt(rad); } }
  if (VAR >= 4) { Node z8[8] = {x, zero, x, x, x, x, x, x}, aux[4]; mn8_aux<Node>(z8, aux, c); for (int i = 0; i < 4; ++i) o[4 + i] = aux[i]; }
}
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  const double cs[8] = {39, -0.625, 13394411.0 / 1186380.0, 0.95, 267, 3.6419361737, 6.0360992808, 1e-6};
  for (VAR = 0; VAR <= 4; ++VAR) {
    capd::MpIMap L(lv, 2, 8, 8, 2); for (int i = 0; i < 8; ++i) L.setParameter(i, MpInterval(cs[i]));
    J j(8, 2); IV r(2);
    try { L(r, j); std::printf("VAR %d: OK\n", VAR); } catch (std::exception& e) { std::printf("VAR %d: THREW %s\n", VAR, std::string(e.what()).substr(0, 70).c_str()); }
  }
}
