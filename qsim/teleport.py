"""
Experiment 8 — quantum teleportation, exact (Bennett et al. 1993; first photons:
Bouwmeester 1997; satellite, 1400 km: Ren et al. / Micius 2017).

Three qubits: Q0 = Alice's UNKNOWN state chi (random on the Bloch sphere),
Q1,Q2 = a shared Bell pair (Q1 Alice's half, Q2 Bob's).  Protocol:
  1. Alice: CNOT(Q0 -> Q1), then H on Q0.
  2. Alice measures Q0,Q1 -> two CLASSICAL bits (m1, m2); her copy is destroyed.
  3. Bob applies the correction Z^m1 X^m2 to his qubit.
Result: Bob's qubit IS chi, fidelity 1, though chi never traveled.

Three verdicts, over 2000 Haar-random input states:
  A. full protocol         -> fidelity = 1 (machine precision), each outcome p = 1/4.
  B. bits withheld         -> Bob's average state = I/2 EXACTLY (trace distance
                              ~1e-16): Alice's collapse alone tells Bob NOTHING.
                              No-signaling, shown constructively.  F = 1/2.
  C. no entanglement       -> best measure-and-resend: average fidelity 2/3
                              (the classical ceiling teleportation beats).

Ties the threads: collapse (Alice's measurement) + a mundane classical channel
(2 bits, light-speed limited) = perfect state transfer; entanglement alone = nothing;
and no-cloning is respected -- the original is necessarily destroyed.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
M = 2000

# ---------- gates on 3 qubits (Q0,Q1,Q2), amplitudes ordered |q0 q1 q2> ----------
I2 = np.eye(2); X = np.array([[0, 1], [1, 0]]); Z = np.diag([1.0, -1.0])
H = np.array([[1, 1], [1, -1]])/np.sqrt(2)
def kron3(a, b, c): return np.kron(a, np.kron(b, c))
CNOT01 = np.zeros((8, 8))
for q0 in (0, 1):
    for q1 in (0, 1):
        for q2 in (0, 1):
            CNOT01[(q0 << 2) | ((q1 ^ q0) << 1) | q2, (q0 << 2) | (q1 << 1) | q2] = 1
H0 = kron3(H, I2, I2)

# ---------- random unknown states + initial 3-qubit state ----------
chi = rng.normal(size=(M, 2)) + 1j*rng.normal(size=(M, 2))
chi /= np.linalg.norm(chi, axis=1, keepdims=True)
bell = np.zeros(4); bell[0] = bell[3] = 1/np.sqrt(2)          # (|00>+|11>)/sqrt2
psi = np.einsum('mi,j->mij', chi, bell).reshape(M, 8)         # chi (x) bell

# ---------- Alice's operations ----------
psi = psi @ CNOT01.T
psi = psi @ H0.T

# ---------- the four measurement outcomes ----------
corr = {(0, 0): I2, (0, 1): X, (1, 0): Z, (1, 1): Z @ X}
F_tele = np.zeros((M, 4)); probs = np.zeros((M, 4))
rho_nobits = np.zeros((M, 2, 2), complex)
for idx, (m1, m2) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
    block = psi.reshape(M, 2, 2, 2)[:, m1, m2, :]             # Bob's unnormalized state
    p = np.sum(np.abs(block)**2, axis=1)
    probs[:, idx] = p
    phi = block / np.sqrt(p)[:, None]
    rho_nobits += p[:, None, None] * np.einsum('mi,mj->mij', phi, phi.conj())
    phi_corr = phi @ corr[(m1, m2)].T
    F_tele[:, idx] = np.abs(np.einsum('mi,mi->m', chi.conj(), phi_corr))**2

print("A. FULL PROTOCOL (entanglement + 2 classical bits), 2000 random states:")
print(f"   min fidelity over all states & outcomes = {F_tele.min():.12f}   (exact: 1)")
print(f"   outcome probabilities: max |p - 1/4| = {np.max(np.abs(probs-0.25)):.2e}")

td = np.max(np.abs(rho_nobits - I2[None]/2))
F_nobits = np.real(np.einsum('mi,mij,mj->m', chi.conj(), rho_nobits, chi))
print("\nB. BITS WITHHELD (Bob acts before Alice's phone call):")
print(f"   max |rho_Bob - I/2| = {td:.2e}  ->  Bob's qubit is EXACTLY maximally mixed")
print(f"   fidelity = {F_nobits.mean():.4f} for every state  (no-signaling, constructively)")

# C. classical benchmark: measure chi in z, resend the eigenstate
p0 = np.abs(chi[:, 0])**2
F_class = p0**2 + (1-p0)**2
print("\nC. NO ENTANGLEMENT (best measure-and-resend):")
print(f"   average fidelity = {F_class.mean():.4f}   (theory: 2/3 = 0.6667)")

# ---------- figure ----------
fig = plt.figure(figsize=(13, 4.8))
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1])

# schematic
axS = fig.add_subplot(gs[0])
axS.axis("off"); axS.set_xlim(0, 10); axS.set_ylim(0, 10)
def box(x, y, w, h, txt, fc, tc="#e7e9f0"):
    axS.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="#3a4150", lw=1, zorder=2))
    axS.text(x+w/2, y+h/2, txt, ha="center", va="center", fontsize=9.5, color=tc, zorder=3)
box(0.4, 7.6, 3.0, 1.6, "Alice's unknown\nqubit  |χ⟩", "#3a2f12", "#ffd27a")
box(0.4, 4.6, 3.0, 1.6, "Bell pair source\n(one half each)", "#1c1f29")
box(4.4, 6.4, 2.6, 1.9, "Alice:\nCNOT, H,\nmeasure", "#12263a")
box(8.0, 4.9, 1.7, 1.6, "Bob:\n$Z^{m_1}X^{m_2}$", "#241a33")
axS.annotate("", xy=(4.4, 7.9), xytext=(3.4, 8.3), arrowprops=dict(arrowstyle="->", color="#ffd27a"))
axS.annotate("", xy=(4.4, 6.9), xytext=(3.4, 5.6), arrowprops=dict(arrowstyle="->", color="#9aa0b2"))
axS.annotate("", xy=(8.2, 4.9), xytext=(3.4, 5.1), arrowprops=dict(arrowstyle="->", color="#9aa0b2"))
axS.annotate("", xy=(8.4, 6.6), xytext=(7.0, 7.3),
             arrowprops=dict(arrowstyle="->", color="#67c98a", lw=2,
                             connectionstyle="arc3,rad=-0.25"))
axS.text(7.4, 8.6, "two CLASSICAL bits $m_1m_2$\n(any phone line; light-limited)",
         fontsize=8.5, color="#67c98a", ha="left")
axS.text(8.85, 4.0, "Bob's qubit = |χ⟩\nfidelity 1.0000", fontsize=9.5,
         color="#ffd27a", ha="center", va="top")
axS.text(0.4, 3.2, "collapse + 2 mundane bits = perfect transfer\n"
                   "entanglement alone = exactly nothing (ρ = I/2)\n"
                   "original necessarily destroyed (no-cloning)",
         fontsize=9.5, color="#9aa0b2", va="top")
axS.set_title("The protocol (Bennett 1993; done over 1400 km via satellite, 2017)")

# fidelity bands
axF = fig.add_subplot(gs[1])
xs = rng.uniform(-0.28, 0.28, M)
axF.scatter(0+xs, F_tele.mean(1), s=3, color="tab:green", alpha=0.4)
axF.scatter(1+xs, F_class, s=3, color="tab:orange", alpha=0.4)
axF.scatter(2+xs, F_nobits, s=3, color="tab:red", alpha=0.4)
for x, y, lab in [(0, 1.0, "1.000"), (1, 2/3, "2/3"), (2, 0.5, "1/2")]:
    axF.hlines(y, x-0.35, x+0.35, color="k", lw=1.4)
    axF.text(x+0.38, y, lab, fontsize=10, va="center")
axF.set_xticks([0, 1, 2])
axF.set_xticklabels(["teleportation\n(entangled + 2 bits)",
                     "best classical\n(measure & resend)",
                     "bits withheld\n(entanglement alone)"], fontsize=9)
axF.set_ylabel("fidelity with the unknown state")
axF.set_ylim(0.25, 1.06)
axF.set_title("2000 random states: three strategies")
fig.suptitle("Teleportation: collapse + a classical channel moves a quantum state — "
             "and neither ingredient works alone", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("teleport.png", dpi=125)
print("\nsaved -> qsim/teleport.png")
