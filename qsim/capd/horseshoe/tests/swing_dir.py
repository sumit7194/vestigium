"""DIAGNOSTIC: the direction in the t = 0 section (dx, dp_x; on shell) that the swing amplifies most, relative to its
size on entry: maximise |Phi(t2, 0) D_in d| / |Phi(t1, 0) D_in d| over d in R^2 (generalised eigenproblem), and the
other eigenvector. Prints unit (in (x, p_x)) edge vectors e_thin (most amplified) and e_wide, and the ratios.
Usage: swing_dir.py t1 t2"""
import sys, numpy as np, sympy as sp, scipy.linalg as sl
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
t1, t2 = float(sys.argv[1]), float(sys.argv[2])
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, t2), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13, t_eval=[t1, t2])
M1 = sv.y[4:, 0].reshape(4, 4) @ D_in; M2 = sv.y[4:, 1].reshape(4, 4) @ D_in
lam, V = sl.eigh(M2.T @ M2, M1.T @ M1)
for k, nm in ((1, "thin"), (0, "wide")):
    d = V[:, k] / np.linalg.norm(V[:, k])
    print("e_%s = (%.15f, %.15f)   swing gain |M2 d|/|M1 d| = %.3e   |M1 d| = %.3e" % (nm, d[0], d[1], np.sqrt(lam[k]), np.linalg.norm(M1 @ d)))
# full-state direction at t1 most amplified by Phi(t2, t1) (top right singular vector, raw coordinates)
P12 = sv.y[4:, 1].reshape(4, 4) @ np.linalg.inv(sv.y[4:, 0].reshape(4, 4))
U, S, Vt = np.linalg.svd(P12)
print("v1 at t1 (x, y, px, py) = %s   singular values %s" % (" ".join("%.15e" % v for v in Vt[0]), " ".join("%.3e" % s for s in S)))
print("centre at t1:", " ".join("%.15e" % v for v in sv.y[:4, 0]))
