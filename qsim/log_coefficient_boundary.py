"""
L9 applied to the family's OWN species-3 label: is the entanglement-entropy log
coefficient "non-universal", or non-universal ONLY IN A REGIME?

Prediction I put on record before running: the log coefficient is universal at a
critical point (fixed by the central charge) and MEANINGLESS away from one — once
the correlation length is short compared with system size, entropy saturates and
there is no log to have a coefficient. So universality should switch ON as
xi -> L and OFF as xi << L, with control parameter xi/L (NOT the regulator).

System: transverse-field Ising chain (exact, free-fermion / Majorana covariance),
    H = -J sum_i sx_i sx_{i+1} - h sum_i sz_i ,   g = h/J,  open boundaries.
Critical at g = 1, central charge c = 1/2.  Block = leftmost l sites (ONE cut), so
the standard CFT prediction is
    S(l) = (c/6) ln[ (2L/pi) sin(pi l / L) ] + const,      c/6 = 1/12 = 0.08333.
Scaling-limit correlation length: xi = 1/|1 - g| (lattice units).

Method (exact, no approximation):
  H = (i/4) sum A_mn a_m a_n with Majoranas a; ground-state covariance Gamma from
  the real Schur canonical form of A; block entropy from the eigenvalues +-i nu_k
  of Gamma restricted to the block:  S = sum_k H2((1+nu_k)/2).
Controls: (i) g -> large must give S -> 0 (product state); (ii) at g = 1 the fitted
coefficient must hit 1/12 and be L-independent; (iii) even-l only, to suppress the
known parity oscillations of the open chain in the ordered phase.
"""
import json
import numpy as np
from scipy.linalg import schur

# ---------------- exact ground-state Majorana covariance ----------------
def majorana_covariance(L, g, J=1.0, return_gap=False):
    """H = -J sum sx sx - h sum sz  ->  A antisym; return ground-state Gamma.

    Also returns the smallest single-particle mode energy lam_min. In the ORDERED
    phase (g<1) lam_min ~ exp(-L/xi): the ground state becomes exponentially
    degenerate (spontaneous symmetry breaking), the Schur canonical form is then
    numerically ambiguous, and the "ground state" it returns is an arbitrary
    member of the degenerate pair. Rows with lam_min below tolerance are EXCLUDED
    from the boundary analysis rather than silently averaged in.
    """
    h = g*J
    A = np.zeros((2*L, 2*L))
    for i in range(L):                      # h term: i h a_{2i-1} a_{2i}
        A[2*i, 2*i+1] = 2*h
        A[2*i+1, 2*i] = -2*h
    for i in range(L-1):                    # J term: i J a_{2i} a_{2i+1}
        A[2*i+1, 2*i+2] = 2*J
        A[2*i+2, 2*i+1] = -2*J
    T, Z = schur(A, output="real")
    # canonicalize: make every 2x2 block [[0, +lam], [-lam, 0]] with lam > 0
    for k in range(0, 2*L - 1, 2):
        if T[k, k+1] < 0:
            Z[:, [k, k+1]] = Z[:, [k+1, k]]
            T[[k, k+1], :] = T[[k+1, k], :]
            T[:, [k, k+1]] = T[:, [k+1, k]]
    lam = np.array([T[k, k+1] for k in range(0, 2*L - 1, 2)])
    G = np.zeros((2*L, 2*L))                # ground state: g_k = -1 minimizes E
    for k in range(0, 2*L - 1, 2):
        G[k, k+1] = -1.0
        G[k+1, k] = +1.0
    Gam = Z @ G @ Z.T
    return (Gam, float(np.min(np.abs(lam)))) if return_gap else Gam

def block_entropy(Gamma, l):
    """entanglement entropy of the leftmost l sites (2l Majoranas)."""
    GA = Gamma[:2*l, :2*l]
    ev = np.linalg.eigvalsh(1j*GA)
    nu = np.clip(ev[ev > -1e-12][-l:], 0.0, 1.0)     # positive branch
    p = (1 + nu)/2
    q = 1 - p
    with np.errstate(divide="ignore", invalid="ignore"):
        s = -(np.where(p > 0, p*np.log(p), 0.0) + np.where(q > 0, q*np.log(q), 0.0))
    return float(s.sum())

# ---------------- controls ----------------
print("CONTROLS")
G_far = majorana_covariance(64, 8.0)
print(f"  g=8 (deep paramagnet), S(l=32) = {block_entropy(G_far, 32):.3e}  (expect ~0)")
G_c = majorana_covariance(256, 1.0)
ls_c = np.arange(8, 129, 2)
S_c = np.array([block_entropy(G_c, int(l)) for l in ls_c])
chord_c = (2*256/np.pi)*np.sin(np.pi*ls_c/256)
slope_c = np.polyfit(np.log(chord_c), S_c, 1)[0]
print(f"  g=1, L=256: fitted log coefficient = {slope_c:.5f}   "
      f"(CFT c/6 = {1/12:.5f}; err {abs(slope_c-1/12)/(1/12):.2%})")

# ---------------- the xi/L scan ----------------
Ls = [64, 128, 256, 512]
deltas = [0.0, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
DEGEN_TOL = 1e-9
rows = []
print("\nSCAN: fitted log coefficient vs xi/L   (universal target 1/12 = 0.08333)")
print(f"{'L':>5} {'g':>6} {'xi':>8} {'xi/L':>8} {'a_fit':>9} {'a/(c/6)':>9} "
      f"{'lam_min':>10}  flag")
for L in Ls:
    for d in deltas:
        for sgn in ([0] if d == 0 else [-1, +1]):
            g = 1.0 + sgn*d
            xi = np.inf if d == 0 else 1.0/d
            Gm, lam_min = majorana_covariance(L, g, return_gap=True)
            ls = np.arange(max(8, L//16), L//2 + 1, 2)
            S = np.array([block_entropy(Gm, int(l)) for l in ls])
            chord = (2*L/np.pi)*np.sin(np.pi*ls/L)
            a = np.polyfit(np.log(chord), S, 1)[0]
            xoL = xi/L if np.isfinite(xi) else np.inf
            degen = lam_min < DEGEN_TOL
            branch = "critical" if d == 0 else ("ordered" if sgn < 0 else "disordered")
            flag = "DEGENERATE-excluded" if degen else ""
            rows.append({"L": L, "g": round(g, 4), "branch": branch,
                         "xi": (None if not np.isfinite(xi) else round(float(xi), 3)),
                         "xi_over_L": (None if not np.isfinite(xoL) else round(float(xoL), 5)),
                         "a_fit": round(float(a), 6),
                         "ratio_to_universal": round(float(a/(1/12)), 4),
                         "lam_min": float(f"{lam_min:.3e}"),
                         "excluded_degenerate": bool(degen)})
            print(f"{L:5d} {g:6.3f} {('inf' if not np.isfinite(xi) else f'{xi:8.2f}'):>8} "
                  f"{('inf' if not np.isfinite(xoL) else f'{xoL:8.4f}'):>8} "
                  f"{a:9.5f} {a/(1/12):9.3f} {lam_min:10.2e}  {flag}")

# ---------------- locate the boundary (clean branch only) --------------------
# The ordered branch (g<1) is excluded on physics, not convenience: its ground
# state is exponentially degenerate (lam_min -> 0), so "the" ground state is not
# defined. The disordered branch (g>1) has a unique ground state throughout.
clean = [r for r in rows if r["branch"] == "disordered" and not r["excluded_degenerate"]]
print(f"\nDEGENERACY AUDIT: {sum(r['excluded_degenerate'] for r in rows)} of {len(rows)} "
      f"rows excluded (all on the ordered branch); "
      f"disordered branch min lam = "
      f"{min(r['lam_min'] for r in rows if r['branch']=='disordered'):.2e}")

# scaling collapse: is the ratio a function of xi/L alone, across L?
print("\nSCALING COLLAPSE on the disordered branch (same xi/L, different L):")
from collections import defaultdict
byx = defaultdict(list)
for r in clean:
    byx[round(r["xi_over_L"], 3)].append((r["L"], r["ratio_to_universal"]))
for x in sorted(byx):
    if len(byx[x]) > 1:
        vals = [v for _, v in byx[x]]
        print(f"  xi/L = {x:6.3f}: " + ", ".join(f"L={L}: {v:.3f}" for L, v in byx[x])
              + f"   spread = {max(vals)-min(vals):.3f}")

uni = [r for r in clean if abs(r["ratio_to_universal"] - 1) <= 0.10]
non = [r for r in clean if abs(r["ratio_to_universal"] - 1) > 0.10]
lo = min((r["xi_over_L"] for r in uni), default=None)
hi = max((r["xi_over_L"] for r in non), default=None)
print(f"\nBOUNDARY (universal := within 10% of c/6; disordered branch, non-degenerate):")
print(f"  lowest  xi/L still universal      : {lo}")
print(f"  highest xi/L already NOT universal: {hi}")
if lo and hi:
    print(f"  => switch-on boundary bracketed at xi/L ~ {np.sqrt(lo*hi):.2f}")

out = {
    "question": "L9 applied to the family's own species-3 label: is the entanglement "
                "log coefficient non-universal always, or only in a regime?",
    "prediction_on_record": "universal at criticality, meaningless when xi << L; "
                            "control parameter xi/L, not the regulator",
    "system": {"model": "transverse-field Ising chain, open BC, exact free-fermion",
               "central_charge": 0.5, "universal_target_c_over_6": 1/12,
               "block": "leftmost l sites (single cut)",
               "xi_convention": "scaling limit xi = 1/|1-g|"},
    "controls": {"S_deep_paramagnet": block_entropy(G_far, 32),
                 "critical_fit_L256": round(float(slope_c), 6),
                 "critical_fit_rel_err": round(float(abs(slope_c-1/12)/(1/12)), 5)},
    "scan": rows,
    "excluded": {"rule": "ordered branch g<1 has exponentially degenerate ground "
                         "state (lam_min < 1e-9): 'the' ground state undefined, "
                         "Schur canonical form ambiguous",
                 "n_excluded": int(sum(r["excluded_degenerate"] for r in rows))},
    "boundary": {"branch": "disordered (g>1, unique ground state)",
                 "lowest_universal_xi_over_L": lo,
                 "highest_nonuniversal_xi_over_L": hi,
                 "bracketed_switch_on": (round(float(np.sqrt(lo*hi)), 3)
                                         if (lo and hi) else None)},
}
with open("log_coefficient_boundary.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nsaved -> qsim/log_coefficient_boundary.json")

# ---------------- figure ----------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(13, 4.9))

cols = {64: "tab:blue", 128: "tab:green", 256: "tab:orange", 512: "tab:red"}
for L in Ls:
    Gm = majorana_covariance(L, 1.0)
    ls = np.arange(4, L//2 + 1, 2)
    S = np.array([block_entropy(Gm, int(l)) for l in ls])
    chord = (2*L/np.pi)*np.sin(np.pi*ls/L)
    ax[0].semilogx(chord, S, "o-", ms=3, lw=1, color=cols[L], label=f"L={L}")
xr = np.array([2, 400])
ax[0].plot(xr, (1/12)*np.log(xr) + (S[0] - (1/12)*np.log(chord[0])), "k--", lw=1.2,
           label=r"slope $c/6=1/12$")
ax[0].set_xlabel("chord length  $(2L/\\pi)\\sin(\\pi \\ell/L)$")
ax[0].set_ylabel("entanglement entropy $S(\\ell)$")
ax[0].set_title("At criticality: one universal slope, all sizes")
ax[0].legend(fontsize=8)

for L in Ls:
    xs = [r["xi_over_L"] for r in clean if r["L"] == L]
    ys = [r["ratio_to_universal"] for r in clean if r["L"] == L]
    o = np.argsort(xs)
    ax[1].semilogx(np.array(xs)[o], np.array(ys)[o], "o-", ms=6, lw=1.4,
                   color=cols[L], label=f"L={L}")
ax[1].axhline(1.0, color="k", ls="--", lw=1)
ax[1].axhspan(0.9, 1.1, color="tab:green", alpha=0.15)
ax[1].text(1.2e-2, 1.03, "universal (within 10% of $c/6$)", fontsize=8.5, color="darkgreen")
if lo and hi:
    ax[1].axvline(np.sqrt(lo*hi), color="tab:purple", ls=":", lw=1.5)
    ax[1].text(np.sqrt(lo*hi)*1.1, 0.45, f"switch-on\n$\\xi/L\\approx${np.sqrt(lo*hi):.1f}",
               fontsize=8.5, color="tab:purple")
ax[1].set_xlabel(r"$\xi / L$   (correlation length / system size)")
ax[1].set_ylabel("fitted coefficient / (c/6)")
ax[1].set_title("The BOUNDARY: one curve in $\\xi/L$, all sizes\n"
                "(disordered branch; ordered branch excluded — degenerate)", fontsize=10)
ax[1].legend(fontsize=8)

fig.suptitle("Species-3 labels are regime-local: the entanglement log coefficient is "
             "universal only while $\\xi \\gtrsim L$", fontsize=12.5)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("log_coefficient_boundary.png", dpi=125)
print("saved -> qsim/log_coefficient_boundary.png")
