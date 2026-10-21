import sys, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
f = MNN.MNFlow(89, 80, sp.Rational(13394411,1186380), sp.Rational(19,20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
sol = solve_ivp(f.rhs, (0, 300), [x0, 0, px0, py0], method="DOP853", rtol=1e-12, atol=1e-12, dense_output=True)
for t in [0, 100, 200, 250, 280, 285, 288, 289, 290, 290.5, 291, 291.5, 292, 295]:
    z = sol.sol(t); J = np.array(f._J(*z), float); fz = np.array(f._f(*z), float)
    ev = np.linalg.eigvals(J); mu = np.linalg.eigvalsh((J + J.T) / 2).max()
    print("t=%6.1f x=%.4f px=%8.2f |J|=%.2e  max Re eig=%.2e  lognorm=%.2e |f|=%.2e" % (t, z[0], z[2], np.linalg.norm(J, 2), ev.real.max(), mu, np.linalg.norm(fz)))
print("--- constant rescale p -> c p : max over orbit of the log norm (2-norm and inf-norm)")
sol = solve_ivp(f.rhs, (0, 1018.7), [x0, 0, px0, py0], method="DOP853", rtol=1e-12, atol=1e-12, dense_output=True)
ts = np.linspace(0, 1018.7, 4001); Js = [np.array(f._J(*sol.sol(t)), float) for t in ts]
def ln2(A): return np.linalg.eigvalsh((A + A.T) / 2).max()
def lninf(A): return max(A[i, i] + sum(abs(A[i, j]) for j in range(4) if j != i) for i in range(4))
for c in [1, 3e-1, 1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4]:
    D = np.diag([1, 1, c, c]); Di = np.diag([1, 1, 1 / c, 1 / c])
    a = [ln2(D @ J @ Di) for J in Js]; b = [lninf(D @ J @ Di) for J in Js]
    print("c=%.0e  max lognorm2 %.2e  max lognorm_inf %.2e  (at t=%.1f)" % (c, max(a), max(b), ts[int(np.argmax(b))]))
