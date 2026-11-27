"""Tier 2a comparison points (registered in TIER2A_PREREG.md). Float only; points are LOCATIONS, so any field may place
them. ~100 phase-space points (x, y, p_x, p_y): the S2 MN nodes, the fixed point and the symmetric point p (lifted to
the beta = 3/100 shell), points sampled along each S2 return including every periapsis (min x) and y-extremum, and
off-orbit perturbations. Written to points.txt as exact decimals (20 significant digits). Claude Opus 5.5 (Quantum)."""
import os, sys, random, numpy as np
from scipy.integrate import solve_ivp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import s1
def spec(fn):
    kv = {}
    for ln in open(fn):
        p = ln.split()
        if p and not ln.startswith("#"): kv[p[0]] = p[1:]
    return kv
B = os.path.join(os.path.dirname(HERE), "s2", "mn")
sp_ = spec(os.path.join(B, "bvp.spec")); m = int(sp_["m"][0])
f = s1.flow(0.03)
sec = [np.array([float(sp_["c"][0]), float(sp_["c"][1])])]
z = [float(v) for v in sp_["z"]]; sec += [np.array(z[2 * i:2 * i + 2]) for i in range(m - 1)]
sec.append(np.array([10.58222772208633, 0.0]))                       # S2's certified symmetric point p (mid)
pts = []
for w in sec:
    py = f.py_of(w[0], w[1]); pts.append(("node", [w[0], 0.0, w[1], py]))
rhs = lambda t, s: f._f(*s)
for i, w in enumerate(sec[1:-1]):                                     # one return from each node, dense samples
    s0 = [w[0], 0.0, w[1], f.py_of(w[0], w[1])]
    ev = lambda t, s: s[1]; ev.direction = 1.0; ev.terminal = True
    o1 = solve_ivp(rhs, (0, 10.0), s0, method="DOP853", rtol=1e-12, atol=1e-12)
    sol = solve_ivp(rhs, (10.0, 2000.0), o1.y[:, -1], method="DOP853", rtol=1e-12, atol=1e-12, events=ev, dense_output=True)
    T = sol.t[-1]; ts = np.linspace(10.0, T, 400); Y = sol.sol(ts)
    picks = set(np.linspace(0, 399, 9).astype(int)[1:-1])
    picks.add(int(np.argmin(Y[0]))); picks.add(int(np.argmax(Y[1]))); picks.add(int(np.argmin(Y[1])))
    for j in sorted(picks): pts.append(("orbit%d" % i, list(Y[:, j])))
rnd = random.Random(20261127)
base = [p for _, p in pts]
for j in range(12):                                                   # off-orbit: perturb by up to 10%
    b = base[rnd.randrange(len(base))]
    pts.append(("off", [b[0] * (1 + 0.1 * (rnd.random() - 0.5)), max(-0.6, min(0.6, b[1] + 0.1 * (rnd.random() - 0.5))),
                       b[2] * (1 + 0.2 * (rnd.random() - 0.5)) + 0.05 * (rnd.random() - 0.5), b[3] * (1 + 0.2 * (rnd.random() - 0.5)) + 0.05 * (rnd.random() - 0.5)]))
with open(os.path.join(HERE, "points.txt"), "w") as fo:
    for tag, p in pts: fo.write(tag + " " + " ".join("%.19e" % v for v in p) + "\n")
print(len(pts), "points; x range %.3f..%.3f, |y| max %.3f" % (min(p[0] for _, p in pts), max(p[0] for _, p in pts), max(abs(p[1]) for _, p in pts)))
