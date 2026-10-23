// jetparam_test2.cpp -- does mn_lift<Node> survive degree-2 jets, with the MN constants as map PARAMETERS vs literals?
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
#include <cstdio>
using capd::MpInterval; using capd::autodiff::Node; typedef capd::MpIVector IV; typedef capd::MpIMatrix IM;
typedef capd::diffAlgebra::Jet<IM, 0> J;
inline Node mn_exp(const Node& a) { return capd_proof::node_exp(a); }
inline MpInterval mn_exp(const MpInterval& a) { return exp(a); }
#include "../gen/mn_field.h"
void f_par(Node, Node in[], int, Node o[], int, Node par[], int) {
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; Node x = par[5] + in[0] * 0.000001, y = in[1] * 0;
  Node xy[2] = {x, y}, g[3]; mn_lift<Node>(xy, g, c); o[0] = g[0]; o[1] = g[1];
}
void f_xy(Node, Node in[], int, Node o[], int, Node par[], int) {       // x, y as true inputs (y evaluated at 0)
  Node c[5] = {par[0], par[1], par[2], par[3], par[4]}; Node xy[2] = {in[0], in[1]}, g[3]; mn_lift<Node>(xy, g, c); o[0] = g[0]; o[1] = g[1];
}
int main() {
  capd::MpFloat::setDefaultPrecision(128);
  const double cs[6] = {39, -0.625, 13394411.0 / 1186380.0, 0.95, 267, 3.6419361737};
  for (int deg = 1; deg <= 2; ++deg) {
    capd::MpIMap fp(f_par, 2, 2, 6, deg); for (int i = 0; i < 6; ++i) fp.setParameter(i, MpInterval(cs[i]));
    capd::MpIMap fx(f_xy, 2, 2, 5, deg); for (int i = 0; i < 5; ++i) fx.setParameter(i, MpInterval(cs[i]));
    J jp(2, deg), jx(2, deg); IV r(2), z(2); z[0] = MpInterval(3.6419361737);
    try { fp(r, jp); std::printf("deg %d par-x, y=in*0 : OK\n", deg); } catch (std::exception& e) { std::printf("deg %d par-x, y=in*0 : THREW %s\n", deg, e.what()); }
    try { fx(z, jx); std::printf("deg %d x,y inputs     : OK\n", deg); } catch (std::exception& e) { std::printf("deg %d x,y inputs     : THREW %s\n", deg, e.what()); }
  }
}
