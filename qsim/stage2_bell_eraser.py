"""
Stage 2: TWO photons, genuine non-local entanglement, and the delayed-choice eraser.

Walborn's structure: a source makes an entangled pair.  Photon s goes to the double
slit; the which-path information is carried by the polarization of the *partner*
photon p (which can be far away, measured later).  We model the net correlation

    |Psi> = (1/sqrt2) ( |slit1>_s |H>_p  +  |slit2>_s |V>_p )           # 2x2 = 4-dim

as a matrix M[path_s, pol_p].  The which-path info lives entirely in p's polarization
(orthogonal H/V), so:

  - screen at s ALONE (trace out p): NO fringes, ever -- and it can't carry a signal.
  - measure p in the DIAGONAL basis: coincidence pattern shows fringes (project |D>)
    or anti-fringes (project |A>) -- the eraser, recovered only by sorting on p.
  - the partner's analyzer angle continuously dials the near fringe contrast.

Still exact (4-dim) -- two photons, but tiny.  The NN waits for Stage 3 (scale).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def pol(phi):
    return np.array([np.cos(phi), np.sin(phi)], complex)

H, V = pol(0), pol(np.pi/2)
Dg, Ag = pol(np.pi/4), pol(-np.pi/4)          # diagonal / anti-diagonal


def bell():
    M = np.zeros((2, 2), complex)
    M[0, 0] = 1/np.sqrt(2)                     # slit 1  <-> p is |H>
    M[1, 1] = 1/np.sqrt(2)                     # slit 2  <-> p is |V>
    return M


def entanglement_entropy(M):
    rho = M @ M.conj().T
    rho = rho / np.trace(rho).real
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 1e-12]
    return float(-np.sum(ev * np.log2(ev)))


def pattern(M, deltas, m=None):
    """Detection at screen phase delta. m=None -> singles at s; else coincidence
    with partner p projected onto polarization state m."""
    a1, a2 = np.exp(1j*deltas/2), np.exp(-1j*deltas/2)
    psi0 = M[0, 0]*a1 + M[1, 0]*a2             # p's H-amplitude, conditioned on s@delta
    psi1 = M[0, 1]*a1 + M[1, 1]*a2             # p's V-amplitude
    if m is None:
        return np.abs(psi0)**2 + np.abs(psi1)**2
    amp = np.conj(m[0])*psi0 + np.conj(m[1])*psi1
    return np.abs(amp)**2


def visibility(I):
    return (I.max() - I.min()) / (I.max() + I.min() + 1e-12)


def main():
    M = bell()
    d = np.linspace(-3*np.pi, 3*np.pi, 600)
    print(f"two-photon Bell state |1>|H> + |2>|V>:  entanglement S = "
          f"{entanglement_entropy(M):.3f} bits (maximal)\n")

    singles = pattern(M, d)
    coincD  = pattern(M, d, Dg)
    coincA  = pattern(M, d, Ag)
    coincH  = pattern(M, d, H)
    print(f"  screen at s ALONE (singles):              V = {visibility(singles):.3f}"
          f"   -> always a blob; the far choice sends NO signal")
    print(f"  coincidence, partner measured D (+45):    V = {visibility(coincD):.3f}"
          f"   -> fringes")
    print(f"  coincidence, partner measured A (-45):    V = {visibility(coincA):.3f}"
          f"   -> ANTI-fringes (shifted by pi)")
    print(f"  coincidence, partner measured H (path):   V = {visibility(coincH):.3f}"
          f"   -> no fringes (which-path known)")
    print(f"  D-coincidence + A-coincidence = singles?  "
          f"max diff {np.max(np.abs(coincD+coincA-singles)):.1e}"
          f"   -> yes: erasure only sorts, never signals")
    print("\n  delayed choice: projecting p and detecting s act on different tensor")
    print("  factors, so the order is irrelevant -- choose p's basis AFTER s lands.")

    # partner analyzer angle continuously dials the near fringe contrast: V = |sin 2phi|
    phis = np.linspace(0, np.pi/2, 46)
    Vc = [visibility(pattern(M, d, pol(p))) for p in phis]

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].plot(d/np.pi, singles, "k--", lw=2, label="s alone (no fringes)")
    ax[0].plot(d/np.pi, coincD, color="tab:blue", label="coincidence: partner = D  (fringes)")
    ax[0].plot(d/np.pi, coincA, color="tab:orange", label="coincidence: partner = A  (anti-fringes)")
    ax[0].plot(d/np.pi, coincD + coincA, ":", color="gray", lw=2, label="D + A  =  s alone (no signal)")
    ax[0].set_xlabel(r"screen phase  $\delta/\pi$"); ax[0].set_ylabel("intensity")
    ax[0].set_title("Fringes hide on the screen, live in the correlations")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    ax[1].plot(np.degrees(phis), Vc, "-o", color="tab:purple", ms=4)
    ax[1].plot(np.degrees(phis), np.abs(np.sin(2*phis)), "k:", lw=1, label=r"$|\sin 2\phi|$")
    ax[1].axvline(0, ls="--", color="gray"); ax[1].axvline(45, ls="--", color="gray")
    ax[1].text(2, 0.5, "partner in H/V\n= which-path\n(V=0)", fontsize=8)
    ax[1].text(33, 0.2, "partner in D/A\n= erase\n(V=1)", fontsize=8)
    ax[1].set_xlabel(r"partner photon's analyzer angle  $\phi$ (deg)")
    ax[1].set_ylabel("near-screen coincidence visibility")
    ax[1].set_title("The FAR photon's dial controls the NEAR fringes")
    ax[1].legend(); ax[1].grid(alpha=0.3)
    fig.suptitle("Stage 2 - two-photon entanglement & the non-local, delayed-choice eraser")
    fig.tight_layout()
    fig.savefig("stage2_bell_eraser.png", dpi=130)
    print("\nsaved plot -> qsim/stage2_bell_eraser.png")


if __name__ == "__main__":
    main()
