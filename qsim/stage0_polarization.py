"""
Stage 0 of the quantum-properties simulator: ONE property as a structured latent.

Polarization is a qubit.  Its "latent" is a 2-component complex state vector
|psi> = a|H> + b|V>, which lives geometrically on the Poincare (Bloch) sphere.

We implement, exactly (no neural net -- one property doesn't need one):
  - states  (Jones vectors): H, V, D, A, R, L
  - operations: linear rotation, polarizer (projection), quarter-wave plate
  - the Bloch/Poincare vector = the geometric coordinates of the latent
  - Born-rule measurement by sampling, verified against Malus's law cos^2(theta)

This is the substrate the later stages build on:
  Stage 1 tensor-products TWO of these (path (x) polarization) -> first entanglement
  Stage 3 hands the (then-exponential) joint state to a neural network.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)
s2 = np.sqrt(2)

# Pauli matrices (the measuring sticks for the Bloch vector)
SX = np.array([[0, 1], [1, 0]], complex)
SY = np.array([[0, -1j], [1j, 0]], complex)
SZ = np.array([[1, 0], [0, -1]], complex)

# --- states (Jones vectors) ---
H = np.array([1, 0], complex)
V = np.array([0, 1], complex)
D = (H + V) / s2          # diagonal  +45
A = (H - V) / s2          # anti-diag -45
R = (H - 1j * V) / s2     # right circular
L = (H + 1j * V) / s2     # left circular
NAMED = {"H": H, "V": V, "D": D, "A": A, "R": R, "L": L}

# --- operations (2x2 matrices acting on the latent) ---
def rot(t):                                   # rotate linear polarization by t
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]], complex)

def polarizer(t):                             # project onto axis at angle t
    p = np.array([np.cos(t), np.sin(t)], complex)
    return np.outer(p, p.conj())

def qwp(t):                                   # quarter-wave plate, fast axis at t
    base = np.array([[1, 0], [0, 1j]], complex)
    return rot(t) @ base @ rot(-t)

# --- geometry: the Bloch/Poincare vector = where the latent sits on the sphere ---
def bloch(psi):
    psi = psi / np.linalg.norm(psi)
    return np.array([np.vdot(psi, M @ psi).real for M in (SX, SY, SZ)])

# --- measurement: Born rule by sampling ---
def born_sample(psi, outcome_state, n):
    prob = abs(np.vdot(outcome_state, psi)) ** 2      # |<outcome|psi>|^2
    return int(np.sum(rng.random(n) < prob)), prob


def main():
    print("=== 1) the latent's geometry: named states on the Poincare sphere ===")
    for name, st in NAMED.items():
        bx, by, bz = bloch(st)
        print(f"  |{name}>  Bloch=({bx:+.2f}, {by:+.2f}, {bz:+.2f})")

    print("\n=== 2) an OPERATION moves the point: quarter-wave plate at 45 on |H> ===")
    out = qwp(np.pi / 4) @ H
    bx, by, bz = bloch(out)
    print(f"  |H> (north pole, z=+1)  --QWP@45-->  Bloch=({bx:+.2f}, {by:+.2f}, {bz:+.2f})"
          f"  (now on the equator => circular)")

    print("\n=== 3) Born-rule measurement is basis-dependent (superposition is relative) ===")
    N = 20000
    kH, pH = born_sample(D, H, N)        # prepare |D>, ask 'is it H?'
    kD, pD = born_sample(D, D, N)        # prepare |D>, ask 'is it D?'
    print(f"  prepared |D>, measured in H/V basis: H-fraction {kH/N:.3f}  (exact {pH:.3f})")
    print(f"  prepared |D>, measured in D/A basis: D-fraction {kD/N:.3f}  (exact {pD:.3f})")
    print("  => the SAME state is a coin-flip in one basis and certain in another.")

    print("\n=== 4) verify against Malus's law: |H> through a polarizer at theta ===")
    thetas = np.linspace(0, np.pi, 19)
    sampled, theory = [], []
    for t in thetas:
        k, p = born_sample(H, np.array([np.cos(t), np.sin(t)], complex), N)
        sampled.append(k / N); theory.append(np.cos(t) ** 2)
    sampled, theory = np.array(sampled), np.array(theory)
    print(f"  max |sampled - cos^2(theta)| over the sweep = {np.max(np.abs(sampled-theory)):.4f}")
    k45, _ = born_sample(H, np.array([np.cos(np.pi/4), np.sin(np.pi/4)], complex), N)
    print(f"  at theta=45deg exactly: transmitted {k45/N:.3f} "
          f"(theory 0.500 -- the number from our eraser talk)")

    # ---- figure: the latent (sphere) + the verification (Malus) ----
    fig = plt.figure(figsize=(11, 4.6))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, v = np.linspace(0, 2*np.pi, 40), np.linspace(0, np.pi, 25)
    xs = np.outer(np.cos(u), np.sin(v)); ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color="lightgray", alpha=0.35, linewidth=0.4)
    for nm, st in NAMED.items():
        bx, by, bz = bloch(st)
        ax.scatter([bx], [by], [bz], s=45, color="tab:blue")
        ax.text(bx*1.15, by*1.15, bz*1.15, nm, fontsize=11)
    for vec, lab in [((1.4,0,0), "x"), ((0,1.4,0), "y"), ((0,0,1.4), "z")]:
        ax.plot([0, vec[0]], [0, vec[1]], [0, vec[2]], color="gray", lw=0.8)
    ax.set_title("The polarization latent = Poincare sphere")
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()

    ax2 = fig.add_subplot(1, 2, 2)
    deg = np.degrees(thetas)
    ax2.plot(deg, theory, "k-", lw=2, label=r"Malus  $\cos^2\theta$")
    ax2.plot(deg, sampled, "o", color="tab:red", ms=6, label=f"sampled ({N} photons/pt)")
    ax2.axvline(45, ls="--", color="gray"); ax2.axhline(0.5, ls=":", color="gray")
    ax2.set_xlabel(r"polarizer angle $\theta$ (deg)"); ax2.set_ylabel("transmitted fraction")
    ax2.set_title("Born-rule measurement reproduces Malus's law")
    ax2.legend(); ax2.grid(alpha=0.3)
    fig.suptitle("Stage 0 - one quantum property (polarization) as a structured, measurable latent")
    fig.tight_layout()
    fig.savefig("stage0_polarization.png", dpi=130)
    print("\nsaved plot -> qsim/stage0_polarization.png")


if __name__ == "__main__":
    main()
