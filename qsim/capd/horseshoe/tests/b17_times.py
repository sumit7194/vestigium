"""B17 checkpoint times from the centre orbit (F5-R UPO 2), computed and logged BEFORE any fix run is read:
t_p1, t_p2 (periapsis = local minima of x along the return), t*_1, t*_2 (argmax over the swing window of
||Phi(t, t_p - 7) M||_2, M = Phi(t_p - 7, 0) D_in the set's true span), the first y = 0 crossing with ydot < 0, and the
return to Sigma = {y = 0, ydot > 0}. DOP853, rtol = atol = 1e-13."""
import sys, json, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
evd = lambda t, s: s[1]; evd.direction = -1.0
evu = lambda t, s: s[1]; evu.direction = 1.0
sol = solve_ivp(f.rhs, (0, 1100), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853",
                rtol=1e-13, atol=1e-13, dense_output=True, events=[evd, evu])
t_down = float(sol.t_events[0][0]); t_ret = float([t for t in sol.t_events[1] if t > 1][0])
ts = np.linspace(0, t_ret, 200001); xs = sol.sol(ts)[0]
mins = [i for i in range(1, len(ts) - 1) if xs[i] < xs[i - 1] and xs[i] < xs[i + 1]]
tps = []
for i in mins:
    r = minimize_scalar(lambda t: sol.sol(t)[0], bracket=(ts[i - 1], ts[i], ts[i + 1]), tol=1e-12); tps.append(float(r.x))
out = dict(t_periapsis=tps, x_at_periapsis=[float(sol.sol(t)[0]) for t in tps], t_y0_down=t_down, t_return=t_ret)
stars = []
for tp in tps:
    t0 = tp - 7; P0 = sol.sol(t0)[4:].reshape(4, 4); M = P0 @ D_in; Pinv0 = np.linalg.inv(P0)
    grid = np.linspace(tp - 7, tp + 5, 24001)
    g = [np.linalg.norm(sol.sol(t)[4:].reshape(4, 4) @ Pinv0 @ M, 2) for t in grid]
    k = int(np.argmax(g)); stars.append(dict(t_star=float(grid[k]), peak_gain=float(g[k] / np.linalg.norm(M, 2))))
out["swings"] = stars
print(json.dumps(out, indent=1))
