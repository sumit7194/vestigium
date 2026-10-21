import sys, subprocess, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN; BETA = sp.Rational(sys.argv[1]) if len(sys.argv) > 1 else sp.Rational(13394411,1186380)
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411,1186380), sp.Rational(19,20), sp.Integer(267)); fJ = MNN.MNFlow(89, 80, BETA, sp.Rational(19,20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
sol = solve_ivp(f.rhs, (0, 300), [x0, 0, px0, py0], method="DOP853", rtol=1e-12, atol=1e-12, dense_output=True)
ts = [0, 100, 200, 250, 280, 285, 288, 289, 290, 290.5, 291, 291.5, 292, 295]
pts = [(t, *sol.sol(t)) for t in ts]
inp = "".join("%.17g %.17g %.17g %.17g %.17g\n" % p for p in pts)
for h in ["1/1000000"]:
    hh = eval(h.replace("/", "./"))
    out = subprocess.run(["/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests/mn_fieldwidth", "128", h] + sys.argv[2:3], input=inp, capture_output=True, text=True).stdout.split("\n")
    print("--- h =", h, " ratio = interval width / linear true range (sum_j |J_ij| 2h)")
    for p, line in zip(pts, out):
        J = np.array(fJ._J(*p[1:]), float); lin = np.abs(J).sum(axis=1) * 2 * hh
        wv = [float(v) for v in line.split()[1:]]
        print("t=%6.1f x=%.3f  widths %s  ratio %s" % (p[0], p[1], " ".join("%.1e" % v for v in wv), " ".join("%.1e" % (a / b) for a, b in zip(wv, lin))))
