"""
Stage 1: TWO properties, and the birth of entanglement.

We tensor two Stage-0 latents into one joint state:
    path  (which slit: |1>, |2>)   (x)   polarization (the marker)
represented as a 2x2 complex matrix C[path, pol], meaning
    |Psi> = sum_{p,q} C[p,q] |path=p> |pol=q>.

Operations:
  - marker(theta): a CONTROLLED rotation -- rotate path-2's polarization by theta
    relative to path-1.  This is the entangling gate.
  - erase(phi):     a polarizer at angle phi on the polarization -- projects both
    paths onto a common polarization, DIS-entangling them (the quantum eraser).

Read-outs:
  - entanglement entropy S  = von Neumann entropy of the reduced path state (bits).
    S=0 means separable (product); S=1 bit means maximally entangled.
  - fringe visibility V     = contrast of the screen pattern after tracing out pol.

The punchline: S and V are two views of ONE quantity (the overlap of the two path
markers). Marking raises S and lowers V; erasing drops S back to 0 and restores V.
Exact, no neural net -- a 4-dim state is tiny.  (NN earns its keep at Stage 3: scale.)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]], complex)


def initial_state():
    # equal path superposition, polarization = H  ->  a PRODUCT state
    C = np.zeros((2, 2), complex)
    C[0] = np.array([1, 0]) / np.sqrt(2)   # path 1, pol H
    C[1] = np.array([1, 0]) / np.sqrt(2)   # path 2, pol H
    return C


def marker(C, theta):
    out = C.copy()
    out[1] = rot(theta) @ C[1]             # stamp path 2 with polarization angle theta
    return out


def erase(C, phi):
    p = np.array([np.cos(phi), np.sin(phi)], complex)   # polarizer axis
    c = C @ p.conj()                                    # surviving path amplitudes
    out = np.outer(c, p)                                # all paths now share pol |phi>
    return out, float(np.vdot(c, c).real)               # (post-state, pass probability)


def entanglement_entropy(C):
    rho = C @ C.conj().T                                # reduced path density matrix
    rho = rho / np.trace(rho).real
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 1e-12]
    return float(-np.sum(ev * np.log2(ev)))


def fringe(C, deltas):
    a1, a2 = np.exp(1j * deltas / 2), np.exp(-1j * deltas / 2)
    I = np.zeros_like(deltas)
    for q in (0, 1):                                    # sum over (traced-out) polarization
        amp = C[0, q] * a1 + C[1, q] * a2
        I = I + np.abs(amp) ** 2
    return I


def visibility(C):
    d = np.linspace(-np.pi, np.pi, 401)
    I = fringe(C, d)
    return (I.max() - I.min()) / (I.max() + I.min() + 1e-12)


def main():
    print("=== marking entangles path with polarization ===")
    for label, th in [("0  (both H)", 0.0), ("45", np.pi/4), ("90 (H vs V)", np.pi/2)]:
        C = marker(initial_state(), th)
        print(f"  tag angle {label:>11}:  S = {entanglement_entropy(C):.3f} bits   "
              f"V = {visibility(C):.3f}")

    print("\n=== the eraser: a 45-deg polarizer dis-entangles the maximally-marked state ===")
    C90 = marker(initial_state(), np.pi/2)               # H/V: S=1, V=0
    Cer, passp = erase(C90, np.pi/4)                      # project onto diagonal
    print(f"  before erase: S = {entanglement_entropy(C90):.3f} bits   V = {visibility(C90):.3f}")
    print(f"  after  erase: S = {entanglement_entropy(Cer):.3f} bits   V = {visibility(Cer):.3f}"
          f"   (and {passp*100:.0f}% of light passed the polarizer)")

    # ---- sweep tag angle: S and V are complementary readouts of one overlap ----
    ths = np.linspace(0, np.pi/2, 46)
    S = [entanglement_entropy(marker(initial_state(), t)) for t in ths]
    Vv = [visibility(marker(initial_state(), t)) for t in ths]

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    deg = np.degrees(ths)
    ax[0].plot(deg, Vv, "-o", color="tab:blue", ms=4, label=r"fringe visibility  $V=\cos\theta$")
    ax[0].plot(deg, S, "-s", color="tab:red", ms=4, label="entanglement  $S$ (bits)")
    ax[0].axvline(45, ls="--", color="gray")
    ax[0].set_xlabel(r"tag angle between the two slits' markers  $\theta$ (deg)")
    ax[0].set_ylabel("value")
    ax[0].set_title("Mark more  ->  entanglement up, fringes down")
    ax[0].legend(); ax[0].grid(alpha=0.3)

    d = np.linspace(-3*np.pi, 3*np.pi, 600)
    ax[1].plot(d/np.pi, fringe(marker(initial_state(), 0.0), d), color="tab:green",
               label="no tag (S=0): full fringes")
    ax[1].plot(d/np.pi, fringe(marker(initial_state(), np.pi/4), d), color="tab:orange",
               label="45 tag (S=0.6): washed out")
    ax[1].plot(d/np.pi, fringe(marker(initial_state(), np.pi/2), d), color="tab:red",
               label="H/V tag (S=1): flat, no fringes")
    ax[1].plot(d/np.pi, fringe(Cer, d), "--", color="tab:blue",
               label="erased (S=0): fringes back, half light")
    ax[1].set_xlabel(r"screen phase  $\delta / \pi$"); ax[1].set_ylabel("intensity")
    ax[1].set_title("The same story on the screen")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("Stage 1 - entanglement made an explicit number (and erased)")
    fig.tight_layout()
    fig.savefig("stage1_entanglement.png", dpi=130)
    print("\nsaved plot -> qsim/stage1_entanglement.png")


if __name__ == "__main__":
    main()
