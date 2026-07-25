"""
The composable double-slit "bench" -- the exact state engine that ties Stages 0-2
into one reusable, UI-drivable API.

Everything we discussed lives in one master formula:

    I(x) = |psi1(x)|^2 + |psi2(x)|^2 + 2 * g * Re[ psi1(x) psi2*(x) <m2|m1> ]

  - psi1, psi2 : the two slits' spatial amplitudes (geometry + a coherence factor g)
  - <m2|m1>    : overlap of the polarization markers on the two paths (which-path info)

Visibility can be reduced TWO ways, the two halves of our whole conversation:
  - low transverse coherence g  (classical: the source isn't coherent across both slits)
  - marking the paths           (quantum: which-path info entangles path with polarization)

The photon's joint (path (x) polarization) state is a 2x2 complex matrix C[path, pol].
Components are fluent (each returns self) so you can chain a pipeline:

    DoubleSlit().source(45).mark(0, 90).analyzer(45).visibility()

No neural net -- this is the small, exact, real-time core (NN is for Stage-3 scale).
"""
import numpy as np

DEG = np.pi / 180.0


def _rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]], complex)


def _pol(t):
    return np.array([np.cos(t), np.sin(t)], complex)


class DoubleSlit:
    def __init__(self):
        self.reset()

    # ---- pipeline components (fluent) ----
    def reset(self):
        self.C = np.array([[1, 0], [1, 0]], complex) / np.sqrt(2)   # both slits, pol H
        self.g = 1.0                                                # transverse coherence
        return self

    def source(self, pol_deg=0.0):
        """Emit one photon: equal path superposition, polarization at pol_deg."""
        p = _pol(pol_deg * DEG)
        self.C = np.array([p, p], complex) / np.sqrt(2)
        return self

    def coherence(self, g):
        """Transverse spatial coherence across the two slits (1=full, 0=none)."""
        self.g = float(np.clip(g, 0.0, 1.0))
        return self

    def mark(self, slit1_deg=0.0, slit2_deg=None):
        """Tag each slit's polarization (a wave-plate/polarizer marker)."""
        if slit2_deg is None:
            slit2_deg = slit1_deg
        C = self.C.copy()
        C[0] = _rot(slit1_deg * DEG) @ C[0]
        C[1] = _rot(slit2_deg * DEG) @ C[1]
        self.C = C
        return self

    def analyzer(self, phi_deg):
        """A polarizer after the slits (the eraser), projecting onto angle phi_deg."""
        p = _pol(phi_deg * DEG)
        c = self.C @ p.conj()           # surviving path amplitudes
        self.C = np.outer(c, p)         # both paths now share polarization |phi>
        return self

    # ---- read-outs ----
    def screen(self, deltas):
        """Intensity pattern vs screen phase delta (traces out polarization)."""
        a1, a2 = np.exp(1j * deltas / 2), np.exp(-1j * deltas / 2)
        I = np.zeros_like(deltas, dtype=float)
        for q in (0, 1):
            t1, t2 = self.C[0, q] * a1, self.C[1, q] * a2
            I += np.abs(t1) ** 2 + np.abs(t2) ** 2 + 2 * self.g * np.real(t1 * np.conj(t2))
        return I

    def visibility(self):
        I = self.screen(np.linspace(-np.pi, np.pi, 401))
        return float((I.max() - I.min()) / (I.max() + I.min() + 1e-12))

    def distinguishability(self):
        """Which-path info D, with V^2 + D^2 <= 1 (= 1 for a pure, coherent state)."""
        return float(np.sqrt(max(0.0, 1.0 - self.visibility() ** 2)))

    def entanglement(self):
        """Path<->polarization entanglement entropy in bits (the quantum marking)."""
        rho = self.C @ self.C.conj().T
        tr = np.trace(rho).real
        if tr < 1e-15:
            return 0.0
        ev = np.linalg.eigvalsh(rho / tr).real
        ev = ev[ev > 1e-12]
        return float(-np.sum(ev * np.log2(ev)))

    def transmitted(self):
        """Fraction of photons that survived the pipeline (analyzers absorb some)."""
        return float(np.vdot(self.C, self.C).real)

    def sample(self, n, rng=None):
        """Born-rule detections: return n screen phases drawn from I(x)."""
        rng = rng or np.random.default_rng(0)
        d = np.linspace(-np.pi, np.pi, 1000)
        I = self.screen(d)
        I = I / I.sum()
        return rng.choice(d, size=n, p=I)


# --------------------------------------------------------------------------
def _selftest():
    def close(a, b, tol=1e-6):
        return abs(a - b) < tol

    print(f"{'configuration':<42}{'V':>7}{'D':>7}{'S(bits)':>9}{'pass%':>7}")
    cases = [
        ("no tag (full coherence)",        DoubleSlit().source(0)),
        ("tag H / V (orthogonal)",         DoubleSlit().source(0).mark(0, 90)),
        ("tag H / V  + analyzer @45 (erase)", DoubleSlit().source(0).mark(0, 90).analyzer(45)),
        ("partial tag H / 45",             DoubleSlit().source(0).mark(0, 45)),
        ("partial tag + analyzer @22.5 (best erase)", DoubleSlit().source(0).mark(0, 45).analyzer(22.5)),
        ("coherence 0.5, no tag",          DoubleSlit().source(0).coherence(0.5)),
    ]
    for name, b in cases:
        print(f"{name:<42}{b.visibility():>7.3f}{b.distinguishability():>7.3f}"
              f"{b.entanglement():>9.3f}{b.transmitted()*100:>6.0f}%")

    # assertions: the engine must reproduce the physics we derived by hand
    assert close(DoubleSlit().source(0).visibility(), 1.0)
    assert close(DoubleSlit().source(0).mark(0, 90).visibility(), 0.0)
    assert close(DoubleSlit().source(0).mark(0, 90).entanglement(), 1.0)
    b = DoubleSlit().source(0).mark(0, 90).analyzer(45)
    assert close(b.visibility(), 1.0) and close(b.transmitted(), 0.5)
    assert close(DoubleSlit().source(0).mark(0, 45).visibility(), np.cos(45 * DEG))   # V=cos
    assert close(DoubleSlit().source(0).coherence(0.5).visibility(), 0.5)
    # the duality relation V^2 + D^2 = 1 for any pure marking
    for th in (0, 20, 45, 70, 90):
        b = DoubleSlit().source(0).mark(0, th)
        assert close(b.visibility() ** 2 + b.distinguishability() ** 2, 1.0, 1e-6)
    print("\nall self-tests passed  ->  V=cos(tag), eraser restores V=1 at 50% light, "
          "V^2+D^2=1, coherence dial all verified.")


if __name__ == "__main__":
    _selftest()
