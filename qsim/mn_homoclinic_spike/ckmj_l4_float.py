"""Control (iv) float pre-run: is CKMJ Thm 3's p-bar (arXiv:2205.03922v2, Table 4 x1) on an L4 homoclinic of the PCRTBP,
mu = 1/2, c = 3? CKMJ eq. (26)-(27): x'' = 2y' + Omega_x, y'' = -2x' + Omega_y, state (x, p, y, q), m1 = (mu, 0), m2 = (mu-1, 0).
Energy E = -(p^2 + q^2) + 2 Omega (CKMJ's Jacobi constant). Float only. Written by Claude Opus 5.5 (Quantum)."""
import json, numpy as np
from scipy.integrate import solve_ivp
mu = 0.5
def Om(x, y):
    r1 = np.hypot(x - mu, y); r2 = np.hypot(x + 1 - mu, y)
    return (1 - mu) * (r1 ** 2 / 2 + 1 / r1) + mu * (r2 ** 2 / 2 + 1 / r2)
def f(t, s):
    x, p, y, q = s; r1 = ((x - mu) ** 2 + y ** 2) ** 1.5; r2 = ((x + 1 - mu) ** 2 + y ** 2) ** 1.5
    return [p, 2 * q + x - (1 - mu) * (x - mu) / r1 - mu * (x + 1 - mu) / r2, q, -2 * p + y - (1 - mu) * y / r1 - mu * y / r2]
E = lambda s: -(s[1] ** 2 + s[3] ** 2) + 2 * Om(s[0], s[2])
L4 = np.array([mu - 0.5, 0.0, np.sqrt(3) / 2, 0.0])
pbar = np.array([-0.037058535628028, -0.007623220519232, 0.873641524369283, 0.033084516464648])
out = dict(E_pbar=E(pbar), E_L4=E(L4), f_L4=list(np.abs(f(0, L4))), dist_pbar_L4=float(np.linalg.norm(pbar - L4)))
for sgn, T in ((+1, 40.0), (-1, 40.0)):
    sol = solve_ivp(lambda t, s: [sgn * v for v in f(t, s)], (0, T), pbar, method="DOP853", rtol=1e-13, atol=1e-13, dense_output=True)
    ts = np.linspace(0, sol.t[-1], 4001); Y = sol.sol(ts); d = np.linalg.norm(Y.T - L4, axis=1)
    r2min = float(np.min(np.hypot(Y[0] + 1 - mu, Y[2])))
    k = int(np.argmin(d[400:])) + 400
    out["fwd" if sgn > 0 else "bwd"] = dict(t_end=float(sol.t[-1]), status=int(sol.status), min_dist_m2=r2min,
        dist_L4_at=[(float(ts[j]), float(d[j])) for j in (0, 500, 1000, 1500, 2000, 3000, 4000)], min_dist_L4_after_t4=float(d[k]), t_min=float(ts[k]),
        E_drift=float(abs(E(Y[:, -1]) - E(pbar))))
print(json.dumps(out, indent=1)); json.dump(out, open("ckmj_l4_float.json", "w"), indent=1)
