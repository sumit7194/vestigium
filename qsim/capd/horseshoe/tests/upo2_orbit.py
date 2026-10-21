import sys, time, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
from scipy.integrate import solve_ivp
t0=time.time()
f = MNN.MNFlow(89, 80, sp.Rational(13394411,1186380), sp.Rational(19,20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808
py0 = f.py_of(x0, px0); print("py0", py0, "setup", time.time()-t0, flush=True)
ev = lambda t, s: s[1]; ev.direction = 1.0
sol = solve_ivp(f.rhs, (0, 5000), [x0, 0, px0, py0], method="DOP853", rtol=1e-12, atol=1e-12, events=ev, dense_output=True, first_step=1e-6)
ts = [t for t in sol.t_events[0] if t > 1e-6]; T = ts[0]; print("return T", T, "nevents", len(ts))
k = list(sol.t_events[0]).index(T); print("return (x,px)", sol.y_events[0][k][[0,2]])
tt = np.linspace(0, T, 20001); Y = sol.sol(tt)
x, y, px, py = Y; R2 = x*x+y*y-1
print("x range", x.min(), x.max(), " y range", y.min(), y.max(), " min x-1", (x-1).min(), " min R2", R2.min(), " min 1-y^2", (1-y*y).min())
print("|px| max", abs(px).max(), "|py| max", abs(py).max())
for i in range(0, 20001, 1000): print("t=%9.3f x=%9.4f y=%8.4f px=%10.3f py=%10.3f" % (tt[i], x[i], y[i], px[i], py[i]))
r = f.P((x0, px0), jac=True, tmax=5000)
DP = r[2]; print("DP", DP); ev_ = np.linalg.eigvals(DP); print("eigs", ev_, "det", np.linalg.det(DP), "norm", np.linalg.norm(DP, 2))
# growth of a 1e-6 box along the orbit: full 4x4 variational norm sampled
s = np.array([x0, 0, px0, py0] + list(np.eye(4).ravel()))
sol2 = solve_ivp(f.rhs, (0, T), s, method="DOP853", rtol=1e-11, atol=1e-11, dense_output=True)
for tq in np.linspace(0, T, 21):
    Phi = sol2.sol(tq)[4:].reshape(4, 4); print("t=%8.2f  |Phi|=%.3e" % (tq, np.linalg.norm(Phi, 2)))
