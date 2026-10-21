"""DIAGNOSTIC: true (linearised) widths of the image of the smoke box (x, p_x in c +- h, y = 0, p_y on shell) along the
UPO-2 orbit, from the variational equation: width_i(t) = sum_j |(Phi(t) D_in)_ij| 2h, D_in the on-shell lift Jacobian.
Usage: true_widths.py h t1 t2 dt"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
h, t1, t2, dt = (float(v) for v in sys.argv[1:5])
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sol = solve_ivp(f.rhs, (0, t2), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-12, atol=1e-12, dense_output=True)
for t in np.arange(t1, t2 + 1e-9, dt):
    s = sol.sol(t); Phi = s[4:].reshape(4, 4); M = Phi @ D_in
    wd = np.abs(M).sum(axis=1) * 2 * h
    print("t=%7.2f x=%.4f  true widths x %.2e y %.2e px %.2e py %.2e" % (t, s[0], *wd))
