"""DIAGNOSTIC: how the CAPD initial set's components grow. The set is x0 + (dx, dpx, dpy) with INDEPENDENT radii
(h, h, r_py), r_py the p_y enclosure's radius (off-shell spread). Width_i(t) = sum_j |Phi_ij(t)| * 2 r_j split into the
contribution of each initial radius, versus the on-shell (true) width of the box.
Usage: offshell.py h r_py t1 t2 dt"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
h, rpy = float(sys.argv[1]), float(sys.argv[2]); t1, t2, dt = (float(v) for v in sys.argv[3:6])
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
ts = np.arange(t1, t2 + 1e-9, dt)
sv = solve_ivp(f.rhs, (0, t2), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13, t_eval=ts)
print("h %g, r_py %g;  px-width contributions: from dx, dpx, dpy (independent) | on-shell true px width" % (h, rpy))
for j, t in enumerate(ts):
    P = sv.y[4:, j].reshape(4, 4)
    cx, cp, cy = abs(P[2, 0]) * 2 * h, abs(P[2, 2]) * 2 * h, abs(P[2, 3]) * 2 * rpy
    on = np.abs(P @ D_in)[2].sum() * 2 * h
    print("t=%7.2f  dx %.2e  dpx %.2e  dpy %.2e  | on-shell %.2e   (x-width from dpy %.2e)" % (t, cx, cp, cy, on, abs(P[0, 3]) * 2 * rpy))
