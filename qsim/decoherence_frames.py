"""
Experiment 2 — decoherence frame-by-frame (collision model, exact state vector).

A path qubit S (slit 1 / slit 2, prepared in |+>) collides sequentially with
environment qubits (each starts |0>).  A collision = controlled-Ry(theta):
IF the particle took slit 2, rotate that env qubit by theta.  Each collision
writes a PARTIAL which-path record into one more degree of freedom.

Exact analytics to verify against:
  after k collisions (fresh qubits), the two environment states' overlap is
  <E1|E2> = cos(theta/2)^k, and fringe visibility V(k) = cos(theta/2)^k,
  distinguishability D = sqrt(1-V^2), duality V^2 + D^2 = 1 throughout,
  path-qubit entropy -> 1 bit as V -> 0.

Four read-outs:
  1) V falls, D rises, entanglement entropy rises -- vs analytic.
  2) The screen: fringe curves (1 + V cos delta)/2 at three stages.
  3) Quantum Darwinism: mutual information I(S : m env qubits) vs m --
     the record is REDUNDANT (many small copies), with the classic plateau.
  4) Reversibility: recycle a tiny 2-qubit environment (hit the same qubits
     again and again) -> the coherence REVIVES periodically; a fresh 12-qubit
     environment never gives it back.  Marker (reversible) vs detector
     (effectively irreversible) in one plot.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

log2 = np.log2

def apply_2q(psi, gate, a, b, n):
    """apply 4x4 gate to qubits (a,b) of an n-qubit state vector."""
    psi = psi.reshape((2,)*n)
    psi = np.moveaxis(psi, (a, b), (0, 1)).reshape(4, -1)
    psi = gate @ psi
    psi = np.moveaxis(psi.reshape((2, 2) + (2,)*(n-2)), (0, 1), (a, b))
    return psi.reshape(-1)

def cry(theta):
    """controlled-Ry(theta): control qubit 0 (path=slit2), target qubit 1."""
    c, s = np.cos(theta/2), np.sin(theta/2)
    G = np.eye(4, dtype=complex)
    G[2:, 2:] = [[c, -s], [s, c]]
    return G

def rho_of(psi, keep, n):
    """reduced density matrix of qubit subset `keep`."""
    rest = [q for q in range(n) if q not in keep]
    M = np.moveaxis(psi.reshape((2,)*n), keep, range(len(keep)))
    M = M.reshape(2**len(keep), -1)
    return M @ M.conj().T

def entropy(rho):
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-12]
    return float(-(ev*log2(ev)).sum())

def path_metrics(psi, n):
    rho = rho_of(psi, [0], n)
    V = 2*abs(rho[0, 1])
    E1 = psi.reshape(2, -1)[0]; E2 = psi.reshape(2, -1)[1]
    n1, n2 = np.linalg.norm(E1), np.linalg.norm(E2)
    ov = abs(np.vdot(E1, E2))/(n1*n2) if n1 > 0 and n2 > 0 else 1.0
    D = np.sqrt(max(0.0, 1 - ov**2))
    return V, D, entropy(rho)

# ---------------- run 1: fresh environment, 12 collisions ----------------
Ne, theta = 12, np.pi/2
n = 1 + Ne
psi = np.zeros(2**n, complex)
psi[0] = 1.0
# path qubit -> |+>
H = np.array([[1, 1], [1, -1]])/np.sqrt(2)
psi = psi.reshape(2, -1); psi = (H @ psi).reshape(-1)

Vs, Ds, Ss = [], [], []
V, D, S = path_metrics(psi, n); Vs.append(V); Ds.append(D); Ss.append(S)
snapshots = {0: V}
for k in range(Ne):
    psi = apply_2q(psi, cry(theta), 0, 1+k, n)
    V, D, S = path_metrics(psi, n)
    Vs.append(V); Ds.append(D); Ss.append(S)
    if k+1 in (4, 12):
        snapshots[k+1] = V
Vs, Ds, Ss = map(np.array, (Vs, Ds, Ss))
ks = np.arange(Ne+1)
V_th = np.cos(theta/2)**ks
print("FRESH ENVIRONMENT (12 collisions, theta = pi/2):")
print(f"   max |V_sim - cos^k(theta/2)|  = {np.max(np.abs(Vs - V_th)):.2e}")
print(f"   max |V^2 + D^2 - 1|           = {np.max(np.abs(Vs**2 + Ds**2 - 1)):.2e}")
print(f"   final entropy of path qubit   = {Ss[-1]:.4f} bits (-> 1)")

# ---------------- run 2: quantum Darwinism at the final state ----------------
Ifrag = []
S_S = entropy(rho_of(psi, [0], n))
for m in range(Ne+1):
    frag = list(range(1, 1+m))
    S_F = entropy(rho_of(psi, frag, n)) if m else 0.0
    S_SF = entropy(rho_of(psi, [0]+frag, n))
    Ifrag.append(S_S + S_F - S_SF)
Ifrag = np.array(Ifrag)
m_star = int(np.argmax(Ifrag >= 0.95*S_S))
print(f"\nQUANTUM DARWINISM: I(S:m qubits) reaches 95% of the full record at m = {m_star}"
      f" of {Ne}; plateau ~{S_S:.2f} bit; full env: {Ifrag[-1]:.2f} bits (pure-state 2x).")

# ---------------- run 3: tiny recycled environment -> revival ----------------
Ne2, theta2, hits = 2, np.pi/4, 32
n2 = 1 + Ne2
psi2 = np.zeros(2**n2, complex); psi2[0] = 1.0
psi2 = psi2.reshape(2, -1); psi2 = (H @ psi2).reshape(-1)
Vr = [path_metrics(psi2, n2)[0]]
for k in range(hits):
    psi2 = apply_2q(psi2, cry(theta2), 0, 1 + (k % Ne2), n2)
    Vr.append(path_metrics(psi2, n2)[0])
Vr = np.array(Vr)
k_rev = int(np.argmax(Vr[1:] > 0.999)) + 1
print(f"\nREVIVAL (2 recycled qubits, theta = pi/4): V collapses and returns to "
      f"{Vr[k_rev]:.4f} at collision {k_rev} (predicted 16).")

# ---------------- figure ----------------
fig, ax = plt.subplots(2, 2, figsize=(13, 8.4))

ax[0, 0].plot(ks, Vs, "o-", color="tab:orange", label="visibility V")
ax[0, 0].plot(ks, V_th, "k--", lw=1, label=r"analytic $\cos^k(\theta/2)$")
ax[0, 0].plot(ks, Ds, "s-", color="tab:blue", label="which-path record D")
ax[0, 0].plot(ks, Ss, "^-", color="tab:purple", label="entanglement S (bits)")
ax[0, 0].set_xlabel("collisions with the environment")
ax[0, 0].set_title("Decoherence = the record accumulating, one collision at a time\n"
                   r"($V^2+D^2=1$ holds throughout)")
ax[0, 0].legend(fontsize=9)

delta = np.linspace(-3*np.pi, 3*np.pi, 400)
for i, (kk, vv) in enumerate(snapshots.items()):
    ax[0, 1].plot(delta/np.pi, (1 + vv*np.cos(delta))/2 + i*1.1,
                  color=plt.cm.plasma(i/2.5), lw=2,
                  label=f"after {kk} collisions (V={vv:.2f})")
ax[0, 1].set_xlabel(r"screen phase $\delta/\pi$"); ax[0, 1].set_yticks([])
ax[0, 1].set_title("What the screen shows at each stage")
ax[0, 1].legend(fontsize=9)

ax[1, 0].plot(range(Ne+1), Ifrag, "o-", color="tab:green")
ax[1, 0].axhline(S_S, ls=":", color="gray")
ax[1, 0].text(6.2, S_S+0.05, "classical record (1 bit) -- redundant plateau", fontsize=8.5)
ax[1, 0].set_xlabel("environment qubits read (m)")
ax[1, 0].set_ylabel("mutual information I(S : m) [bits]")
ax[1, 0].set_title("Quantum Darwinism: a few qubits already hold the whole\n"
                   "which-path story -- the record is COPIED, not moved")

ax[1, 1].plot(range(hits+1), Vr, "o-", color="tab:red", ms=4,
              label="2-qubit environment, recycled")
ax[1, 1].plot(ks, Vs, "s--", color="tab:gray", ms=4,
              label="12 fresh qubits (never returns)")
ax[1, 1].set_xlabel("collisions"); ax[1, 1].set_ylabel("visibility V")
ax[1, 1].set_title("The difference between a marker and a detector:\n"
                   "a SMALL environment gives the coherence back (revival)")
ax[1, 1].legend(fontsize=9)

fig.suptitle("Decoherence frame-by-frame: coherence doesn't vanish -- it moves into records "
             "(and comes back if you hold them)", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("decoherence_frames.png", dpi=125)
print("\nsaved -> qsim/decoherence_frames.png")
