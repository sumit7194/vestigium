"""DIAGNOSTIC: TRUE NONLINEAR hull of the smoke box's image (the Bridge's check, 2026-10-21): integrate n boundary
points of the box (x, p_x in c +- h, y = 0, p_y on shell) and compare the hull of their images in (x, p_x) with the
linearised width (variational equation) at times t. DOP853, rtol = atol = 1e-13.
Usage: nonlin_hull.py h n_per_edge t1 t2 dt"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
h = float(sys.argv[1]); n = int(sys.argv[2]); t1, t2, dt = (float(v) for v in sys.argv[3:6])
x0, px0 = 3.6419361737, 6.0360992808
ts = np.arange(t1, t2 + 1e-9, dt)
pts = []
for i in range(n):
    s_ = -1 + 2 * i / n
    pts += [(-1, s_), (s_, 1), (1, -s_), (-s_, -1)]           # around the boundary
traj = []
for u, s in pts:
    x, px = x0 + u * h, px0 + s * h; py = f.py_of(x, px)
    sol = solve_ivp(f.rhs, (0, t2), [x, 0, px, py], method="DOP853", rtol=1e-13, atol=1e-13, t_eval=ts)
    traj.append(sol.y)
traj = np.array(traj)                                         # (npts, 4, nt)
py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, t2), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13, t_eval=ts)
print("h = %g, %d boundary points" % (h, len(pts)))
print("   t      hull_x   lin_x  ratio |  hull_px  lin_px  ratio")
for j, t in enumerate(ts):
    M = sv.y[4:, j].reshape(4, 4) @ D_in; lin = np.abs(M).sum(axis=1) * 2 * h
    hx = np.ptp(traj[:, 0, j]); hp = np.ptp(traj[:, 2, j])
    print("%7.2f  %.2e %.2e %5.2f | %.2e %.2e %5.2f" % (t, hx, lin[0], hx / lin[0], hp, lin[2], hp / lin[2]))
