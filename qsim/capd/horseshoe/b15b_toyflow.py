"""TEST-ONLY toy map for the G6 end-to-end test (test_b15b_g6_run.py); never used by a counted run.
The standard map on the cylinder, y' = y + K sin x, x' = x + y' (x wrapped to [-pi, pi)), K = 8: a saddle at the origin
(eigenvalues ~9.90 and ~0.101) with a homoclinic tangle, so W^u and W^s of the origin cross. A "hole" |y| > HOLE, and a band BAND[0] < |y| < BAND[1] inside the arcs,
return None (no return), to exercise the drop / chord bookkeeping. MNFlow's interface: py_of, P(w, n, jac, tmax, rtol, atol)
-> (w2, T[, DP]) or None, Pinv(w, tmax, rtol, atol) -> w0 or None, plunges. The tolerance enters as a deterministic
perturbation of size ~ rtol * 1e-2, so 1e-13 and 1e-14 differ measurably (the self-convergence error of the recompute)."""
import numpy as np
K = 8.0; HOLE = 3.0; BAND = (0.50, 0.52)      # BAND: an interior hole, so drops occur inside an arc (chords)
wrap = lambda x: (x + np.pi) % (2 * np.pi) - np.pi


class ToyFlow:
    def __init__(self): self.plunges = []; self.delta_floor = 1e-6

    def py_of(self, x, px): return 1.0

    def P(self, w, n=1, jac=False, tmax=2000.0, rtol=1e-12, atol=1e-12):
        x, y = np.asarray(w, float); D = np.eye(2)
        for _ in range(int(n)):
            if abs(y) > HOLE or BAND[0] < abs(y) < BAND[1]: return None
            c = K * np.cos(x); D = np.array([[1 + c, 1.0], [c, 1.0]]) @ D
            y = y + K * np.sin(x) + rtol * 1e-2 * np.sin(3 * x); x = wrap(x + y)
        w2 = np.array([x, y]); return (w2, 1.0 * n) if not jac else (w2, 1.0 * n, D)

    def Pinv(self, w, tmax=2000.0, rtol=1e-12, atol=1e-12):
        X, Y = np.asarray(w, float); x = wrap(X - Y); y = Y - K * np.sin(x) - rtol * 1e-2 * np.sin(3 * x)
        if abs(y) > HOLE or BAND[0] < abs(y) < BAND[1]: return None
        return np.array([x, y])
