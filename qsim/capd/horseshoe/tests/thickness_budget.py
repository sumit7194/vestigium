"""DIAGNOSTIC: contributions of each initial set component to the set's width along u2 (needle short axis) and grad H at
time t1: the correlated (dx, dpx) part (true needle), and the INDEPENDENT radii (p_y own radius r_py; y has zero width).
Usage: thickness_budget.py h r_py_width t1"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
h, wpy, t1 = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, t1), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13)
P = sv.y[4:, -1].reshape(4, 4); M1 = P @ D_in; U, S, Vt = np.linalg.svd(M1, full_matrices=False); u2 = U[:, 1]
xc = sv.y[:4, -1]; fc = np.array(f._f(*xc), float); gH = np.array([-fc[2], -fc[3], fc[0], fc[1]]); gH /= np.linalg.norm(gH)
for nm, n in (("u2", u2), ("gradH", gH)):
    true = np.abs(n @ M1).sum() * 2 * h
    own = abs(n @ P[:, 3]) * wpy
    print("t=%g along %-5s: true (correlated dx,dpx) %.3e ;  from p_y own radius (width %.1e): %.3e  (|n.Phi e_py| = %.3e)" % (t1, nm, true, wpy, own, abs(n @ P[:, 3])))
