"""Double-precision MN/Kerr reduced flow for the B14 constructor (non-rigorous; proposals only).
H = 1/2 (g^xx p_x^2 + g^yy p_y^2) + V(x, y) = -1/2, with my B10-regularised V, g^xx, g^yy (mn_s5_gate.mine, gated
against the bridge's field). Section Sigma = {y = 0, p_y > 0}, coordinates (x, p_x), p_y lifted on the positive branch.
Hamilton's equations and their Jacobian are generated symbolically, then lambdified to numpy."""
import numpy as np, sympy as sp
from scipy.integrate import solve_ivp
import mn_s5_gate as G


class MNFlow:
    def __init__(self, M, a, beta, E, L):
        X, Y, gxx, gyy, V = G.mine(M, a, beta, E, L)
        PX, PY = sp.symbols("p_x p_y")
        H = (gxx * PX**2 + gyy * PY**2) / 2 + V
        z = [X, Y, PX, PY]
        f = [sp.diff(H, PX), sp.diff(H, PY), -sp.diff(H, X), -sp.diff(H, Y)]
        J = sp.Matrix(f).jacobian(z)
        self._f = sp.lambdify(z, f, "numpy", cse=True)
        self._J = sp.lambdify(z, J, "numpy", cse=True)
        self._H = sp.lambdify(z, H, "numpy")
        self._g = sp.lambdify((X, Y), [gxx, gyy, V], "numpy")
        self.params = dict(M=M, a=a, beta=beta, E=E, L=L)

    def py_of(self, x, px, y=0.0):
        gxx, gyy, V = self._g(x, y)
        r = (-1.0 - gxx * px * px - 2 * V) / gyy                    # from H = -1/2
        return np.sqrt(r) if r > 0 else np.nan

    def rhs(self, t, s):
        f = np.array(self._f(*s[:4]), float)
        if len(s) == 4:
            return f
        Phi = s[4:].reshape(4, 4)
        return np.concatenate([f, (np.array(self._J(*s[:4]), float) @ Phi).ravel()])

    def P(self, w, n=1, jac=False, tmax=2000.0, rtol=1e-12, atol=1e-12):
        x, px = w
        py = self.py_of(x, px)
        if not np.isfinite(py):
            return None
        s = np.array([x, 0.0, px, py] + (list(np.eye(4).ravel()) if jac else []))
        ev = lambda t, s: s[1]; ev.direction = 1.0
        T = 0.0
        for _ in range(n):
            sol = solve_ivp(self.rhs, (0, tmax), s, method="DOP853", rtol=rtol, atol=atol, events=ev, first_step=1e-6)
            ts = [t for t in sol.t_events[0] if t > 1e-6]
            if not ts:
                return None
            k = list(sol.t_events[0]).index(ts[0]); s = sol.y_events[0][k].copy(); s[1] = 0.0; T += ts[0]
        w2 = np.array([s[0], s[2]])
        if not jac:
            return w2, T
        Phi = s[4:].reshape(4, 4)
        x0, px0 = w; py0 = self.py_of(x0, px0)
        # dpy from the constraint: dH = 0 with dy = 0 =>  dpy = -(H_x dx + H_px dpx) / H_py
        f0 = np.array(self._f(x0, 0.0, px0, py0), float)
        Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
        D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
        V = Phi @ D_in
        f = np.array(self._f(*s[:4]), float)
        V = V - np.outer(f, V[1] / f[1])                             # slide along the flow back to y = 0
        return w2, T, np.array([V[0], V[2]])

    def Pinv(self, w, tmax=2000.0, rtol=1e-12, atol=1e-12):
        """previous crossing of Sigma (y = 0 with ydot > 0 in forward time), by integrating the reversed flow"""
        x, px = w
        py = self.py_of(x, px)
        if not np.isfinite(py):
            return None
        back = lambda t, s: -np.asarray(self.rhs(t, s))
        ev = lambda t, s: s[1]; ev.direction = -1.0                  # reversed time: y decreases through 0
        sol = solve_ivp(back, (0, tmax), [x, 0.0, px, py], method="DOP853", rtol=rtol, atol=atol, events=ev, first_step=1e-6)
        ts = [i for i, t in enumerate(sol.t_events[0]) if t > 1e-6]
        if not ts:
            return None
        s = sol.y_events[0][ts[0]]
        return np.array([s[0], s[2]])


def plug_into_constructor(flow):
    """Point the FROZEN B14 constructor (hs_construct, unchanged) at this system's maps. The constructor's functions
    look up P, Pinv and px_of in their module at call time, so this swaps the system without editing the constructor."""
    import hs_construct as H
    H.P = flow.P
    H.Pinv = flow.Pinv
    H.px_of = lambda x, px: flow.py_of(x, px)
    return H
