"""DIAGNOSTIC (the Bridge's B): true on-shell image of the smoke box at time t1 is a parallelogram M1 [-h,h]^2,
M1 = Phi(t1, 0) D_in (4x2). Its axes (SVD of M1: s1 >= s2, left vectors u1, u2), the symplectic area check
omega(M1 e1, M1 e2) = omega(e1, e2), and the swing gains |Phi(t2, t1) u_i|. Prints u1, u2 for the set probe.
Usage: needle.py h t1 t2"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
h, t1, t2 = (float(v) for v in sys.argv[1:4])
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, t2), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13, t_eval=[t1, t2])
P1 = sv.y[4:, 0].reshape(4, 4); P2 = sv.y[4:, 1].reshape(4, 4); P21 = P2 @ np.linalg.inv(P1)
M1 = P1 @ D_in
U, S, Vt = np.linalg.svd(M1, full_matrices=False)
om = lambda a, b: a[0] * b[2] - a[2] * b[0] + a[1] * b[3] - a[3] * b[1]
print("needle at t=%g (box half-width %g): long axis %.3e, short axis %.3e (full widths 2 s_i h)" % (t1, h, 2 * S[0] * h, 2 * S[1] * h))
print("symplectic area check: omega(M1 e1, M1 e2) = %.12f (t = 0: %.12f)" % (om(M1[:, 0], M1[:, 1]), om(D_in[:, 0], D_in[:, 1])))
for i in range(2):
    print("u%d = %s   swing gain |Phi(%g,%g) u| = %.3e" % (i + 1, " ".join("%.15e" % v for v in U[:, i]), t2, t1, np.linalg.norm(P21 @ U[:, i])))
xc = sv.y[:4, 0]; fc = np.array(f._f(*xc), float)
print("flow direction at t1 (unit):", " ".join("%.6e" % v for v in fc / np.linalg.norm(fc)), " gain %.3e" % np.linalg.norm(P21 @ (fc / np.linalg.norm(fc))))
# directions for the set probe (8 numbers each: x y px py a b E2 eG); aux entries 0 here (projection on the 4-D part),
# energy normal from the 4-D field (H_x, H_y, H_px, H_py) = (-pxdot, -pydot, xdot, ydot)
gH = np.array([-fc[2], -fc[3], fc[0], fc[1]]); gH /= np.linalg.norm(gH)
print("gradH unit:", " ".join("%.6e" % v for v in gH), " gain %.3e" % np.linalg.norm(P21 @ gH))
with open(sys.argv[4] if len(sys.argv) > 4 else "/dev/null", "w") as fh:
    for v in (U[:, 0], U[:, 1], gH):
        fh.write(" ".join("%.17e" % c for c in list(v) + [0, 0, 0, 0]) + "\n")
