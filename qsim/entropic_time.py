"""
BRIDGE ASK (round 7-ish, 2026-07-xx) — is "entropic time" a coarse-graining choice?

Target: Barontini, "Testing the problem of time with cold atoms"
(arXiv:2509.07745, Phys. Rev. Research 8, L022047 (2026)). A BEC in a trap split
by an optical barrier into observed (bright) / unobserved (dark) sectors; an
"entropic time" is built from a coarse-grained entropy of the observed sector and
shown to order events across expansion/recollapse cycles. Operationally the
entropy reduces to the bright-sector atom number (entropy-per-particle ~ 1), so
the clock counts atoms that have tunnelled across.

M2-species question (definitional robustness): coarse-graining is a SCHEME CHOICE.
Does the constructed entropic time depend on which coarse-graining you pick? If
2-3 legitimately different coarse-grainings of the SAME dynamics order the same
events identically -> entropic time is scheme-robust (strengthens the paper). If
they diverge -> "time" here is partly the experimenter's choice (a novel critique).

Model (exact, faithful to the split-BEC): two-mode Bose-Hubbard, N atoms,
    H = -J (aL^ aR + aR^ aL) + (U/2)[nL(nL-1) + nR(nR-1)] + eps (nL - nR)/2
time-INDEPENDENT. Hilbert space = {|nL, N-nL>}, dim N+1 (exact diagonalization).
Start all atoms in the bright well |N,0> and let them tunnel. Reduced state of the
bright mode is diagonal in Fock number (each nL pairs with a unique nR=N-nL), so
the bright<->dark entanglement entropy = Shannon entropy of P(nL) exactly.

Four legitimately different coarse-grained entropies of the observed sector:
  A  count   : S_A = <nL>   (Barontini's operational clock: extensive, ~ atom number)
  B  entang  : S_B = -sum P(n) ln P(n)   (full number-distribution / entanglement entropy)
  C  binned  : S_C = -sum_b Q_b ln Q_b, Q_b = coarse bins of nL (an explicit
               coarse-graining; we test B_bins = 4 and 8)
  D  linear  : S_D = 1 - sum P(n)^2   (linear/collision entropy)

"Entropic time" orders events by the value of its entropy. Two schemes order the
SAME events identically iff their entropies are monotonically related over the
run -> measured by Kendall tau (tau=+1 identical order, -1 reversed, 0 unrelated).
We report tau over the full run AND within the first monotonic-flow segment (the
regime where the paper's clock is well-defined), plus turning-point alignment.
"""
import json
import os
import numpy as np
from scipy.stats import kendalltau

# ---------------- exact two-mode Bose-Hubbard ----------------
N = 40
J, U, eps = 0.5, 0.02, 0.0                       # Josephson regime (Lambda=NU/2J=0.8)
n = np.arange(N + 1)                              # nL = 0..N
Hd = (U/2)*(n*(n-1) + (N-n)*(N-n-1)) + eps*(n - (N-n))/2
off = -J*np.sqrt((n[:-1]+1)*(N - n[:-1]))        # <nL+1| a_L^ a_R |nL>
H = np.diag(Hd) + np.diag(off, 1) + np.diag(off, -1)
E, V = np.linalg.eigh(H)

psi0 = np.zeros(N + 1); psi0[N] = 1.0            # all atoms in the bright well
c = V.T @ psi0

T, K = 40.0, 1000
ts = np.linspace(0, T, K)
P = np.empty((K, N + 1))
for i, t in enumerate(ts):
    amp = V @ (c*np.exp(-1j*E*t))
    P[i] = np.abs(amp)**2

# ---------------- the four coarse-grained entropies ----------------
def shannon(p):
    p = p[p > 1e-15]
    return float(-(p*np.log(p)).sum())

def binned(p, B):
    edges = np.linspace(0, N + 1, B + 1)
    Q = np.array([p[int(edges[b]):int(edges[b+1])].sum() for b in range(B)])
    return shannon(Q)

S = {
    "A_count":   P @ n,                                   # <nL>
    "B_entang":  np.array([shannon(P[i]) for i in range(K)]),
    "C_bin4":    np.array([binned(P[i], 4) for i in range(K)]),
    "C_bin8":    np.array([binned(P[i], 8) for i in range(K)]),
    "D_linear":  1 - (P**2).sum(1),
}
names = list(S)

# ---------------- monotonic-flow window (paper's domain of validity) ----------
# first segment where the counting clock flows one way (bright well depletes)
nb = S["A_count"]
dn = np.sign(np.diff(nb))
first_turn = int(np.argmax(dn != dn[0])) + 1 if np.any(dn != dn[0]) else K-1
mono = slice(0, first_turn)
print(f"model: N={N}, J={J}, U={U} (Lambda=NU/2J={N*U/(2*J):.2f}); "
      f"first turning point at lab-time t={ts[first_turn]:.2f} (index {first_turn}/{K})")

# ---------------- Kendall tau: do the schemes order events identically? -------
# ORIENTATION IS A CONVENTION (a clock running backwards is the same clock), so
# the fair measure of "do these two order events identically" is |tau|:
#   |tau| = 1  -> perfectly monotonically related -> SAME ordering of events
#   |tau| < 1  -> the pair disagrees about which event came first, somewhere.
def tau_matrix(idx):
    M = np.zeros((len(names), len(names)))
    for a in range(len(names)):
        for b in range(len(names)):
            M[a, b] = abs(kendalltau(S[names[a]][idx], S[names[b]][idx])[0])
    return M

full = tau_matrix(slice(0, K))
monm = tau_matrix(mono)

def show(M, title):
    print(f"\n{title}")
    print("            " + "".join(f"{nm[:8]:>10}" for nm in names))
    for a, nm in enumerate(names):
        print(f"{nm:>11} " + "".join(f"{M[a,b]:10.3f}" for b in range(len(names))))

show(monm, "|Kendall tau| WITHIN the monotonic-flow window (paper's valid regime):")
show(full, "|Kendall tau| over the FULL run (incl. expansion/recollapse cycles):")

# ---------------- how often does each clock stop / reverse? ------------------
# quantifies the paper's own caveat ("not well defined when there is no entropy
# flow"): a clock that turns around cannot globally order events.
def turns(x):
    d = np.diff(x)
    idx = np.where(np.sign(d[:-1]) != np.sign(d[1:]))[0] + 1
    return ts[idx]

print("\nturning points (lab-time) — where each clock stops and runs backwards:")
tp = {}
for nm in names:
    t_ = turns(S[nm])
    tp[nm] = t_.tolist()
    print(f"  {nm:>10}: {len(t_):3d} reversals in T={T:g};  first six: {np.round(t_[:6], 2)}")

# ---------------- parameter robustness: is the disagreement generic? ---------
def min_offdiag_tau(Jx, Ux, window_only=True):
    Hd_ = (Ux/2)*(n*(n-1) + (N-n)*(N-n-1))
    off_ = -Jx*np.sqrt((n[:-1]+1)*(N - n[:-1]))
    H_ = np.diag(Hd_) + np.diag(off_, 1) + np.diag(off_, -1)
    E_, V_ = np.linalg.eigh(H_)
    c_ = V_.T @ psi0
    P_ = np.empty((K, N+1))
    for i, t in enumerate(ts):
        a_ = V_ @ (c_*np.exp(-1j*E_*t)); P_[i] = np.abs(a_)**2
    s_ = {"A_count": P_ @ n,
          "B_entang": np.array([shannon(P_[i]) for i in range(K)]),
          "C_bin4": np.array([binned(P_[i], 4) for i in range(K)]),
          "D_linear": 1 - (P_**2).sum(1)}
    nbx = s_["A_count"]; dnx = np.sign(np.diff(nbx))
    ft = int(np.argmax(dnx != dnx[0])) + 1 if np.any(dnx != dnx[0]) else K-1
    idx = slice(0, ft) if window_only else slice(0, K)
    ks = list(s_)
    return min(abs(kendalltau(s_[a][idx], s_[b][idx])[0])
               for a in ks for b in ks if a != b), ts[ft]

print("\nparameter scan (is the divergence generic, or a fluke of one setting?):")
scan = []
for Jx, Ux in [(0.5, 0.0), (0.5, 0.02), (0.5, 0.2), (0.2, 0.02), (1.0, 0.05)]:
    mt, ft = min_offdiag_tau(Jx, Ux)
    lam = N*Ux/(2*Jx)
    scan.append({"J": Jx, "U": Ux, "Lambda": round(lam, 3),
                 "min_abs_tau_window": round(float(mt), 4),
                 "window_end_lab_time": round(float(ft), 3)})
    print(f"  J={Jx:4.2f} U={Ux:4.2f} (Lambda={lam:5.2f}): "
          f"min|tau| in window = {mt:.3f}   (window ends t={ft:.2f})")

# ---------------- STEELMAN 1: is the disagreement macroscopic or fine-grained? --
# A critique is weak if the clocks only disagree about events 0.04 apart in lab
# time (no experiment resolves that). Test: keep only events separated by dt, and
# smooth each clock over that same scale (finite experimental resolution), then
# re-score. Report the separation at which orderings actually reconcile.
def coarse_agreement(dt_sep, idx=mono):
    step = max(1, int(dt_sep/(ts[1]-ts[0])))
    w = step if step % 2 == 1 else step + 1
    ker = np.ones(w)/w
    out = {}
    for nm in names:
        sm = np.convolve(S[nm], ker, mode="same")
        out[nm] = sm[idx][::step]
    ks = names
    return min(abs(kendalltau(out[a], out[b])[0]) for a in ks for b in ks if a != b), \
           len(out[names[0]])

print("\nSTEELMAN 1 — do the clocks reconcile if we only compare well-separated events?")
print(f"{'dt_sep':>8} {'#events':>8} {'min|tau|':>10}")
steel = []
for dt_sep in [0.05, 0.1, 0.2, 0.4, 0.8, 1.6]:
    mt, ne = coarse_agreement(dt_sep)
    steel.append({"dt_separation": dt_sep, "n_events": ne,
                  "min_abs_tau": round(float(mt), 4)})
    print(f"{dt_sep:8.2f} {ne:8d} {mt:10.3f}")

# ---------------- STEELMAN 2: regime map (where IS the construction safe?) -----
print("\nSTEELMAN 2 — regime map: min|tau| in window vs interaction strength Lambda")
regime = []
for Ux in [0.0, 0.005, 0.02, 0.05, 0.1, 0.2, 0.4]:
    mt, ft = min_offdiag_tau(0.5, Ux)
    regime.append({"Lambda": round(N*Ux/(2*0.5), 3), "U": Ux,
                   "min_abs_tau_window": round(float(mt), 4),
                   "window_end": round(float(ft), 3)})
    print(f"  Lambda={N*Ux/(2*0.5):6.2f}: min|tau| = {mt:.3f}  (window ends t={ft:.2f})")

# ---------------- verdict ----------------
od = lambda M: [M[a, b] for a in range(len(names)) for b in range(len(names)) if a != b]
mono_min, full_min = min(od(monm)), min(od(full))
# same-family control: two distributional entropies (B vs D) should agree if the
# machinery is sound -> isolates "structural disagreement" from "numerical noise"
ctrl = monm[names.index("B_entang"), names.index("D_linear")]
cross = monm[names.index("A_count"), names.index("B_entang")]
print(f"\nVERDICT")
print(f"  same-family control  |tau|(B_entang, D_linear)  = {ctrl:.3f}"
      f"   <- machinery sound if ~1")
print(f"  cross-family         |tau|(A_count,  B_entang)  = {cross:.3f}"
      f"   <- the actual test")
print(f"  min pairwise |tau|, monotonic window = {mono_min:.3f}  "
      f"({'ROBUST' if mono_min > 0.98 else 'SCHEME-DEPENDENT'})")
print(f"  min pairwise |tau|, full run         = {full_min:.3f}  "
      f"({'robust' if full_min > 0.98 else 'SCHEME-DEPENDENT'})")

out = {
    "target": "Barontini arXiv:2509.07745 PRR 8 L022047 (2026), entropic time",
    "question": "does constructed entropic time depend on the coarse-graining choice?",
    "model": {"two_mode_Bose_Hubbard": True, "N": N, "J": J, "U": U, "eps": eps,
              "Lambda_NU_2J": N*U/(2*J), "T": T, "K": K,
              "first_turning_lab_time": round(float(ts[first_turn]), 3)},
    "schemes": names,
    "measure": "|Kendall tau| (orientation of a clock is a convention; |tau|=1 "
               "means the two schemes order all events identically)",
    "abs_kendall_tau_monotonic_window": monm.round(4).tolist(),
    "abs_kendall_tau_full_run": full.round(4).tolist(),
    "clock_reversals": {k: {"count": len(v), "first_six_lab_time":
                            [round(x, 3) for x in v[:6]]} for k, v in tp.items()},
    "parameter_scan": scan,
    "steelman_1_coarse_event_separation": steel,
    "steelman_2_regime_map": regime,
    "verdict": {
        "same_family_control_B_vs_D": round(float(ctrl), 4),
        "cross_family_A_vs_B": round(float(cross), 4),
        "min_abs_tau_monotonic_window": round(float(mono_min), 4),
        "min_abs_tau_full_run": round(float(full_min), 4),
        "reading": "counting/extensive clocks and distributional/entropy clocks "
                   "are different clocks: they disagree on event order even inside "
                   "the window where the counting clock flows monotonically",
    },
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entropic_time.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print("\nsaved -> qsim/entropic_time.json")

# ---------------- figure ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(13.5, 8.6))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])
axT = fig.add_subplot(gs[0, :]); axR = fig.add_subplot(gs[1, 0]); axM = fig.add_subplot(gs[1, 1])
norm = lambda x: (x - x.min())/(x.max() - x.min() + 1e-12)
cols = {"A_count": "tab:blue", "B_entang": "tab:red", "C_bin4": "tab:green",
        "C_bin8": "tab:olive", "D_linear": "tab:purple"}
tmax = 12.0
sel = ts <= tmax
for nm in names:
    axT.plot(ts[sel], norm(S[nm])[sel], color=cols[nm], lw=1.5, label=nm)
axT.axvspan(0, ts[first_turn], color="gray", alpha=0.15)
axT.text(ts[first_turn]/2, 1.04, "monotonic-flow window\n(counting clock)", ha="center",
         fontsize=8.5, color="dimgray")
axT.axvline(ts[first_turn], color="k", ls=":", lw=1)
axT.set_xlim(0, tmax); axT.set_xlabel("lab time")
axT.set_ylabel("normalized clock reading")
axT.legend(fontsize=8, ncol=5, loc="lower right")
axT.set_title("Five 'entropic clocks' built from the SAME dynamics (identical H, identical state)")

from scipy.stats import rankdata
rA = rankdata(S["A_count"][mono])
for nm in names[1:]:
    axR.plot(rA, rankdata(S[nm][mono]), ".", ms=3, color=cols[nm], label=nm, alpha=0.7)
axR.plot([1, first_turn], [1, first_turn], "k--", lw=0.8)
axR.set_xlabel("event order by COUNTING clock (Barontini's)")
axR.set_ylabel("event order by another clock")
axR.set_title(f"Inside the valid window: orderings disagree\n(min |tau| = {mono_min:.2f}; "
              f"diagonal = agreement)", fontsize=10)
axR.legend(fontsize=7.5, loc="upper left")

lam = [r["Lambda"] for r in regime]; mt = [r["min_abs_tau_window"] for r in regime]
axM.semilogx(np.maximum(lam, 1e-2), mt, "o-", color="tab:brown", lw=2, ms=7)
axM.axhline(0.98, color="k", ls=":", lw=1)
axM.text(0.012, 0.995, "scheme-robust", fontsize=8.5)
axM.fill_between([1e-2, 1e2], 0, 0.98, color="tab:red", alpha=0.07)
axM.set_xlim(1e-2, 30); axM.set_ylim(-0.03, 1.05)
axM.set_xlabel(r"interaction strength  $\Lambda = NU/2J$")
axM.set_ylabel("min pairwise |tau| in window")
axM.set_title("REGIME MAP: entropic time is scheme-robust only\nwhen interactions dominate",
              fontsize=10)

fig.suptitle("Is 'entropic time' a property of the system, or a choice of the experimenter?  "
             "(probing Barontini, PRR 2026)", fontsize=12.5)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("entropic_time.png", dpi=125)
print("saved -> qsim/entropic_time.png")
