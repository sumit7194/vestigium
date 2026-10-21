"""DIAGNOSTIC (the Bridge's kappa test, 2026-10-21): along the point orbit, step transition matrices M_n = Phi(t_{n+1}, t_n)
on CAPD's own step sequence (read from a diag8 DECOMP log), and the ratio of the absolute-value product |M_n|...|M_k|
to the true product M_n...M_k (inf-norms), from t_start. If interval radii are propagated by absolute products,
this ratio is the amplifier of any per-step seed.
Usage: abs_product.py decomp_log t_start"""
import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
log, t0 = sys.argv[1], float(sys.argv[2])
ts = [float(l.split()[2]) for l in open(log) if l.startswith("DECOMP")]
ts = [t for t in ts if t >= t0]
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
s = solve_ivp(f.rhs, (0, ts[0]), [x0, 0, px0, py0], method="DOP853", rtol=1e-13, atol=1e-13).y[:, -1]
Pt = np.eye(4); Pa = np.eye(4); out = []
for a, b in zip(ts[:-1], ts[1:]):
    sol = solve_ivp(f.rhs, (a, b), np.concatenate([s, np.eye(4).ravel()]), method="DOP853", rtol=1e-13, atol=1e-13)
    s = sol.y[:4, -1]; M = sol.y[4:, -1].reshape(4, 4)
    Pt = M @ Pt; Pa = np.abs(M) @ Pa
    out.append((b, np.abs(Pt).sum(axis=1).max(), Pa.sum(axis=1).max()))
for t, nt, na in out[::max(1, len(out) // 40)] + [out[-1]]:
    print("t=%9.4f  steps<=  |true prod|=%.3e  |abs prod|=%.3e  kappa=%.3e" % (t, nt, na, na / nt))
