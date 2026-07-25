"""
BRIDGE ASK 2 (round 6, 2026-07-10) — the entropic hinge on a harmonic chain.

Longo (2019) exact identity, the computable core behind Dorau & Much
(PRL 2026, arXiv:2510.24491): for a COHERENT excitation f of a free field,
the relative entropy w.r.t. vacuum restricted to the right wedge equals the
boost energy of the classical wave:

    S_rel = 2*pi * INT_{x>0} x * T00[f](x) dx          (c = hbar = 1)

Lattice check, independent implementation:
  - harmonic chain, N sites, open BC:  H = 1/2 SUM p^2 + m^2 q^2 + (q_{i+1}-q_i)^2
  - vacuum covariance from the exact DCT-II normal modes (no matrix diag needed)
  - coherent state = vacuum displaced by classical profile f (same covariance)
  - EXACT lattice S_rel = 1/2 d^T M d, with M the modular (entanglement)
    Hamiltonian matrix of the reduced right-half vacuum, built by Williamson
    symplectic diagonalization of the reduced covariance
  - target = 2*pi * SUM_j x_j T00_j,  T00 = 1/2[(grad f)^2 + m^2 f^2]
    (x measured from the cut; gradient terms weighted at link midpoints)

Honest systematics, reported not hidden:
  - the identity is a CONTINUUM/Lorentz statement; the lattice breaks boosts,
    so agreement should improve as sigma, x0, 1/m >> lattice spacing
  - O(a) ambiguity in the lattice x-weight convention
  - deep-wedge symplectic eigenvalues nu -> 1/2 exponentially: beta_k =
    ln((nu+1/2)/(nu-1/2)) is precision-limited in float64. We CLIP nu at
    1/2 + eps and SWEEP eps over decades: if S_rel is clip-stable, float64
    suffices for this displacement; the spread across clips is quoted as a
    numerical-precision band.

Self-test: single thermal mode, displaced — machinery must reproduce the
analytic S_rel = |d|^2/2 * ln((nu+1/2)/(nu-1/2)) at machine precision.
"""
import json
import numpy as np

# ---------------- vacuum covariance from exact open-chain modes --------------
def chain_covariance(N, m):
    n = np.arange(N)
    k = np.pi*n/N
    om = np.sqrt(m*m + 2 - 2*np.cos(k))                  # mode frequencies
    j = np.arange(N)
    V = np.cos(np.outer(k, j + 0.5))                     # DCT-II modes, rows=k
    norm = np.full(N, N/2.0); norm[0] = N
    Vn = V/np.sqrt(norm)[:, None]                        # orthonormal rows
    X = (Vn.T*(1.0/(2*om))) @ Vn                         # <q q>
    P = (Vn.T*(om/2.0)) @ Vn                             # <p p>
    return X, P

def modular_matrix(X_A, P_A, clip):
    """M with  -ln rho_A = 1/2 R^T M R + c,  R=(q,p).

    Direct functional calculus (no symplectic-basis construction):
        M = 2 i Omega * arccoth(2 i gamma Omega)          <-- ordering matters!
    and  i gamma Omega = gamma^{1/2} (iT) gamma^{-1/2}  with  T = g^{1/2} Om g^{1/2}
    (iT Hermitian), so
        M = 2 i Om * gh * W arccoth(2w) W^dag * ghi .
    Ordering verified analytically on a SQUEEZED thermal mode
    gamma = diag(nu e^{2r}, nu e^{-2r})  ->  M = diag(beta e^{-2r}, beta e^{2r});
    the wrong ordering (i Om gamma) gives the inverse-squeezed M and passes the
    unsqueezed self-test silently — caught 2026-07-10.
    """
    nA = X_A.shape[0]
    gamma = np.block([[X_A, np.zeros((nA, nA))], [np.zeros((nA, nA)), P_A]])
    Om = np.block([[np.zeros((nA, nA)), np.eye(nA)], [-np.eye(nA), np.zeros((nA, nA))]])
    ev, U = np.linalg.eigh(gamma)
    gh = (U*np.sqrt(ev)) @ U.T
    ghi = (U*(1.0/np.sqrt(ev))) @ U.T
    T = gh @ Om @ gh                                     # antisymmetric
    w, W = np.linalg.eigh(1j*T)                          # Hermitian, evals = +-nu
    wc = np.where(np.abs(w) < 0.5 + clip, np.sign(w)*(0.5 + clip), w)
    ac = 0.5*np.log((2*wc + 1)/(2*wc - 1))               # arccoth(2w), odd
    F = (W*ac[None, :]) @ W.conj().T                     # arccoth(2iT), Hermitian
    M = 2j*Om @ gh @ F @ ghi
    herm = np.max(np.abs(M.imag))/max(1e-300, np.max(np.abs(M.real)))
    Mr = M.real
    sym = np.max(np.abs(Mr - Mr.T))/np.max(np.abs(Mr))
    return 0.5*(Mr + Mr.T), herm, sym, np.abs(w[nA:])

def s_rel_exact(X, P, N, f, clip):
    A = slice(N//2, N)
    M, a1, a2, nus = modular_matrix(X[A, A], P[A, A], clip)
    d = np.concatenate([f[A], np.zeros(N - N//2)])
    return 0.5*float(d @ M @ d), a1, a2

def s_rel_target(f, N, m):
    """2*pi * sum x*T00 ; x from the cut (between sites N/2-1 and N/2)."""
    xs = np.arange(N) - N/2 + 0.5                        # site positions
    site = 0.5*m*m*f*f
    df = f[1:] - f[:-1]
    xlink = np.arange(N - 1) - N/2 + 1.0                 # link midpoints
    return 2*np.pi*(np.sum(xs*site) + np.sum(xlink*0.5*df*df))

# ---------------- self-test: single displaced thermal mode -------------------
nu0, dq, dp = 1.7, 0.6, -0.3
M1, _, _, _ = modular_matrix(np.array([[nu0]]), np.array([[nu0]]), 1e-14)
got = 0.5*np.array([dq, dp]) @ M1 @ np.array([dq, dp])
want = 0.5*(dq*dq + dp*dp)*np.log((nu0 + 0.5)/(nu0 - 0.5))
print(f"SELF-TEST single mode: machinery {got:.12f} vs analytic {want:.12f} "
      f"(diff {abs(got-want):.2e})")

# self-test 2: SQUEEZED thermal mode — the case that distinguishes the ordering
r = 0.4
M2, _, _, _ = modular_matrix(np.array([[nu0*np.exp(2*r)]]),
                             np.array([[nu0*np.exp(-2*r)]]), 1e-14)
beta0 = np.log((nu0 + 0.5)/(nu0 - 0.5))
want2 = np.diag([beta0*np.exp(-2*r), beta0*np.exp(2*r)])
print(f"SELF-TEST squeezed mode: max|M - analytic| = {np.max(np.abs(M2 - want2)):.2e}")

# ---------------- main sweep -------------------------------------------------
# float64 resolves modular weights beta up to ~28 (nu - 1/2 down to ~1e-13).
# beta_effective ~ 2*pi*x0*omega_packet, omega ~ sqrt(m^2 + (1/2sigma)^2):
# the m=0.10 rows below EXCEED that (kept, flagged, as the honest boundary);
# the m=0.02 soft-mode family sits at beta_eff ~ 13 — inside float64's reach.
N = 400
cases = [(10, 3, 0.10), (15, 4, 0.10),                    # precision-limited zone
         (24, 6, 0.02), (28, 8, 0.02), (36, 10, 0.02), (48, 12, 0.02)]
clips = [1e-8, 1e-10, 1e-12]

rows = []
print(f"\nchain N={N}, cut at center; packet f = exp(-(x-x0)^2/(4 sigma^2))")
print(f"{'x0':>4} {'sigma':>6} {'m':>5} {'S_exact':>12} {'S_target':>12} {'dev %':>7} "
      f"{'clip band %':>12} {'M-checks':>10}")
xs_all = np.arange(N) - N/2 + 0.5
cov_cache = {}
for x0, sig, m in cases:
    if m not in cov_cache:
        cov_cache[m] = chain_covariance(N, m)
    X, P = cov_cache[m]
    f = np.exp(-(xs_all - x0)**2/(4.0*sig*sig))
    vals = []
    for c in clips:
        v, a1, a2 = s_rel_exact(X, P, N, f, c)
        vals.append(v)
    v_mid = vals[1]
    band = (max(vals) - min(vals))/v_mid*100
    tgt = s_rel_target(f, N, m)
    dev = (v_mid - tgt)/tgt*100
    ok = band < 0.5
    rows.append({"x0": x0, "sigma": sig, "m": m,
                 "S_rel_exact_lattice": round(v_mid, 8),
                 "S_rel_boost_formula": round(float(tgt), 8),
                 "deviation_percent": round(float(dev), 4),
                 "clip_stability_band_percent": round(float(band), 6),
                 "precision_ok": bool(ok)})
    print(f"{x0:4d} {sig:6.1f} {m:5.2f} {v_mid:12.6f} {tgt:12.6f} {dev:7.2f} "
          f"{band:12.2e} {a1:8.1e},{a2:6.1e}" + ("" if ok else "  <-- precision-limited"))

# continuum-limit trend among precision-clean rows of the soft-mode family
trend = [r["deviation_percent"] for r in rows if r["m"] == 0.02 and r["precision_ok"]]
print("\ncontinuum trend (m=0.02 scaled family, precision-clean rows):", trend, "%")

out = {
    "ask": "bridge round-6 ask-2: Longo relative-entropy identity on a harmonic chain",
    "identity": "S_rel(coherent||vacuum)|wedge = 2*pi*INT x T00[f]",
    "method": "exact Gaussian S_rel = 1/2 d^T M d via Williamson modular matrix; "
              "independent implementation, no code shared with the bridge",
    "chain": {"N": N, "mass": m, "cut": "center", "bc": "open"},
    "rows": rows,
    "notes": [
        "identity is a continuum/Lorentz statement; deviations = lattice artifacts",
        "clip_stability_band ~ float64 precision band on the exact lattice value",
        "O(a) x-weight convention on the lattice target (links at midpoints)",
    ],
}
with open("entropic_hinge.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("saved -> qsim/entropic_hinge.json")
