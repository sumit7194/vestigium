"""
Experiment 9 — Wigner's friend: is a measurement absolute, or relative to the observer?
The capstone of the measurement-problem thread (Wigner 1961; extended/reversible
version tested with photons by Proietti et al. 2019).

Three qubits: S = system, F = the Friend (sealed in an isolated lab), E = the
outside environment that a record could leak into.

  1. System starts in |+> = (|0>+|1>)/sqrt2.
  2. The Friend MEASURES S = a CNOT(S -> F).  From INSIDE, the Friend now holds a
     definite outcome.  From OUTSIDE, the sealed lab is one big superposition:
     (|0>_S|0>_F + |1>_S|1>_F)/sqrt2 -- a "measurement" that is still unitary.
  3. A leak of strength phi entangles the outcome with E (controlled rotation
     S -> E): <e0|e1> = cos(phi/2).  phi=0 sealed lab; phi=pi record fully escaped.

Two viewpoints, both computed exactly:
  FRIEND: reduced state of S is ALWAYS I/2 (diagonal, 50/50) -- from the Friend's
          side an outcome definitely happened, for every phi.
  WIGNER: treats S+F as one quantum object and runs an interference test
          <X_S X_F>.  On the sealed pure state it reads 1 (a superposition, NO
          absolute outcome yet); it falls as cos(phi/2) as the record leaks.
  REVERSIBILITY: with phi=0 Wigner can UNDO the Friend's measurement (reverse
          CNOT) -> S back to |+>, Friend's memory blanked (fidelity 1). Once the
          record has leaked (phi>0) the undo fails -> the outcome becomes absolute.

Punchline: "did a measurement happen?" has no observer-independent answer until a
record has irreversibly leaked. Measurement is relative; decoherence is what makes
it absolute -- the same reversibility boundary from experiments 2 & 6, now aimed
straight at the measurement problem.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 3-qubit machinery, amplitudes ordered |S F E> ----
I2 = np.eye(2); X = np.array([[0, 1.], [1, 0]])
def kron3(a, b, c): return np.kron(a, np.kron(b, c))
def cnot(ctrl, tgt):
    G = np.zeros((8, 8))
    for s in range(8):
        b = [(s >> 2) & 1, (s >> 1) & 1, s & 1]
        if b[ctrl]: b[tgt] ^= 1
        G[(b[0] << 2) | (b[1] << 1) | b[2], s] = 1
    return G
def crot(ctrl, tgt, phi):
    """controlled Ry(phi): rotate tgt by phi iff ctrl=1."""
    c, s = np.cos(phi/2), np.sin(phi/2)
    G = np.zeros((8, 8))
    for st in range(8):
        b = [(st >> 2) & 1, (st >> 1) & 1, st & 1]
        if not b[ctrl]:
            G[st, st] = 1
        else:
            for t in (0, 1):
                bb = b.copy(); bb[tgt] = t
                j = (bb[0] << 2) | (bb[1] << 1) | bb[2]
                G[j, st] += (c if t == b[tgt] else (s if t > b[tgt] else -s))
    return G

CNOT_SF = cnot(0, 1)
XSXF = kron3(X, X, I2)

def reduced(psi, keep):
    """reduced density matrix over the qubits in `keep` (subset of {0,1,2})."""
    T = psi.reshape(2, 2, 2)
    rest = [q for q in range(3) if q not in keep]
    A = np.transpose(T, keep + rest).reshape(2**len(keep), -1)
    return A @ A.conj().T

phis = np.linspace(0, np.pi, 61)
Vwig, Sdef, Frev = [], [], []
plus = np.array([1, 1.])/np.sqrt(2)
for phi in phis:
    psi = kron3(plus, np.array([1., 0]), np.array([1., 0]))     # |+>|0>|0>
    psi = CNOT_SF @ psi                                          # Friend measures
    psi = crot(0, 2, phi) @ psi                                  # leak into E
    Vwig.append(np.real(psi.conj() @ XSXF @ psi))               # Wigner's interference
    rhoS = reduced(psi, [0])
    Sdef.append(np.real(rhoS[0, 0] - rhoS[1, 1]))               # Friend: population bias
    psi_undo = CNOT_SF @ psi                                     # Wigner reverses
    tgt = kron3(plus, np.array([1., 0]), None) if False else None
    rhoSF = reduced(psi_undo, [0, 1])
    # fidelity of undone S+F with |+>_S|0>_F
    v = np.kron(plus, np.array([1., 0]))
    Frev.append(np.real(v.conj() @ rhoSF @ v))
Vwig, Sdef, Frev = map(np.array, (Vwig, Sdef, Frev))

print("WIGNER'S FRIEND — exact 3-qubit simulation:")
print(f"  sealed lab (phi=0):  Wigner interference <X_S X_F> = {Vwig[0]:.4f} (=1: pure superposition, no absolute outcome)")
print(f"                       Friend's S bias |0>-|1|       = {Sdef[0]:.4f} (=0: a definite 50/50 outcome for the Friend)")
print(f"                       reversal fidelity to |+>|0>   = {Frev[0]:.4f} (=1: Wigner can UNDO the measurement)")
print(f"  leaked  (phi=pi):    Wigner interference           = {Vwig[-1]:.4f} (=0: now an absolute, classical outcome)")
print(f"                       reversal fidelity             = {Frev[-1]:.4f} (=1/2: undo fails, outcome is locked in)")
print(f"  check Vwig == cos(phi/2): max dev = {np.max(np.abs(Vwig-np.cos(phis/2))):.2e}")
print(f"  check Friend always definite: max |bias| = {np.max(np.abs(Sdef)):.2e}")

# ---------------- figure ----------------
fig = plt.figure(figsize=(13, 5))
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.1])

axS = fig.add_subplot(gs[0]); axS.axis("off"); axS.set_xlim(0, 10); axS.set_ylim(0, 10)
axS.add_patch(plt.Rectangle((0.5, 1.2), 6.0, 6.6, fc="#12161f", ec="#2a6a6a", lw=1.6, ls="--"))
axS.text(3.5, 8.05, "the Friend's sealed lab", color="#5fb0b0", fontsize=10, ha="center")
def box(x, y, w, h, t, fc, tc="#e7e9f0"):
    axS.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="#3a4150", lw=1, zorder=2))
    axS.text(x+w/2, y+h/2, t, ha="center", va="center", fontsize=9.5, color=tc, zorder=3)
box(1.1, 5.4, 2.1, 1.5, "System S\n$|+\\rangle$", "#3a2f12", "#ffd27a")
box(4.0, 5.4, 2.1, 1.5, "Friend F\nmeasures", "#12263a")
box(1.1, 2.2, 5.0, 1.4, "inside: 'I got a definite outcome'", "#181b24", "#9aa0b2")
box(7.3, 4.3, 2.2, 1.9, "Wigner\n(outside)", "#241a33")
axS.annotate("", xy=(4.0, 6.15), xytext=(3.2, 6.15), arrowprops=dict(arrowstyle="->", color="#9aa0b2"))
axS.annotate("", xy=(7.3, 5.6), xytext=(6.6, 5.9), arrowprops=dict(arrowstyle="->", color="#b08be6"))
axS.text(9.6, 3.7, "outside: 'the whole lab\nis still a superposition —\nno outcome is absolute\n(until a record leaks)'",
         color="#b08be6", fontsize=8.8, ha="right", va="top")
axS.set_title("Wigner's friend: one event, two irreconcilable descriptions")

ax = fig.add_subplot(gs[1])
ax.plot(phis/np.pi, Vwig, color="tab:purple", lw=2.2, label="Wigner's interference $\\langle X_SX_F\\rangle$")
ax.plot(phis/np.pi, Frev, color="tab:green", lw=2, ls="-.", label="reversal fidelity (can Wigner undo it?)")
ax.plot(phis/np.pi, 0.5+0*phis, color="tab:orange", lw=2, ls=":",
        label="Friend's outcome: definite (flat) for all leaks")
ax.axvspan(-0.02, 0.02, color="#2a6a6a", alpha=0.25)
ax.text(0.02, 0.12, "sealed:\nreversible,\nrelative", fontsize=8.5, color="#3a8a8a")
ax.text(0.98, 0.12, "leaked:\nabsolute,\nfor everyone", fontsize=8.5, color="#a05a3a", ha="right")
ax.set_xlabel("how much the outcome has leaked into the outside world  ($\\phi/\\pi$)")
ax.set_ylabel("value")
ax.set_ylim(-0.05, 1.08)
ax.set_title("A measurement becomes 'real' exactly when its record can't be recalled")
ax.legend(fontsize=8.8, loc="upper right")

fig.suptitle("Is a measurement absolute? Only once decoherence makes it irreversible.", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("wigner_friend.png", dpi=125)
print("\nsaved -> qsim/wigner_friend.png")
