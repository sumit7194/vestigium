"""
The corner term — the successor to kappa_vs_mutual_info.py.

That study used STRIPS: two straight cuts, zero corners. It showed the area-law
coefficient kappa is regulator-junk (41.6% spread across four regulators, and
unmoved by lattice refinement). But strips are blind to the one quantity in 2D
that is supposed to be genuinely universal: the CORNER coefficient.

A sharp angle in the entangling boundary contributes a logarithmic term,
    S(square, side l) = A * (4l) + B * ln(l) + C ,   corner coeff a = -B/4 ,
and a(theta) is a property of the THEORY, not of the cutoff. So the question is
sharp and it is the same question as before, asked of a different coefficient:

    on ONE lattice with FOUR regulators, is the corner coefficient
    regulator-INDEPENDENT in the same run where kappa is not?

TWO CONTROLS THAT CAN FAIL (a control that cannot fail is decoration):
  C1 SYNTHETIC NO-LOG: feed the fitter data generated from a pure area law with
     NO log term plus realistic noise. It must return B consistent with zero.
     This tests the fitter's own tendency to manufacture a logarithm.
     -> PASSED (B ~ 4e-15 at zero noise; tracks the noise level thereafter).
  C2 PHYSICAL NO-CORNER: half-torus strips (two straight cuts, no corners) fit
     with the IDENTICAL 3-parameter form. B must again come out ~0.
     -> ***FAILED***, B ~ -0.496. Kept in the file rather than deleted. It failed
     because I chose the geometry badly, not because the fitter is broken: the
     half-torus strip scales the REGION with the LATTICE at L = 12..28 while
     xi = 50 >> L, so it sits in the finite-size-dominated regime. DIAGNOSED, not
     asserted -- pushing xi/L from 1.79 down to 0.06 drives B from -0.495 to
     -0.005 (see the C2 DIAGNOSIS block at the bottom). The squares are immune:
     they are measured at fixed L=160 with l/L <= 0.125, where the zero mode
     contributes a constant ~0.002 independent of l.
  C2' THE CONTROL I SHOULD HAVE BUILT: an l x 2l rectangle and an l x l square
     have exactly four pi/2 corners each, so the corner log CANCELS in the
     difference, leaving pure area. Same lattice, same geometry family, same
     fitter, and still able to fail.
     -> PASSED, |B| <= 0.0019 against a corner signal of |B| ~ 0.047. That
     residual IS the method's systematic floor: 4.1% of signal. Every spread
     quoted below must be read against it.

TWO INDEPENDENT EXTRACTIONS of B (agreement is evidence, disagreement is the floor):
  E1 direct 3-parameter fit of S(l);
  E2 successive differences S(l+d) - S(l), which never fit the constant C at all.

Plus: the continuum refinement that decided the previous study, and a mass
sensitivity check so the verdict does not rest on one correlation length.

Honest scope: theta = pi/2 only. A square lattice represents a 90-degree corner
exactly; other angles need staircase boundaries whose steps are themselves
corners, which is a different (and worse) experiment. Absolute comparison of
a(pi/2) to its continuum value needs an extrapolation we are NOT doing here --
the claim under test is regulator-INDEPENDENCE, which is immune to that because
every regulator is compared at identical mass and geometry.
"""
import json
import os

# be a good citizen: a sister project holds a core, so cap BLAS threads
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "4"

import numpy as np

# ---------------- the same four regulators as kappa_vs_mutual_info.py --------
def K2_of(kx, ky):
    return (2 - 2*np.cos(kx)) + (2 - 2*np.cos(ky))

def K4_of(kx, ky):
    f = lambda k: (4/3)*(2 - 2*np.cos(k)) - (1/12)*(2 - 2*np.cos(2*k))
    return f(kx) + f(ky)

def make_regs(m):
    return {
        "nn":           lambda kx, ky: m*m + K2_of(kx, ky),
        "improved":     lambda kx, ky: m*m + K4_of(kx, ky),
        "higher_deriv": lambda kx, ky: m*m + K2_of(kx, ky) + 0.25*K2_of(kx, ky)**2,
        "smeared":      lambda kx, ky: m*m + K2_of(kx, ky)*np.exp(0.15*K2_of(kx, ky)),
    }
NAMES = ["nn", "improved", "higher_deriv", "smeared"]

def kernels(L, reg):
    n = np.arange(L)
    kx, ky = np.meshgrid(2*np.pi*n/L, 2*np.pi*n/L, indexing="ij")
    w = np.sqrt(reg(kx, ky))
    return np.real(np.fft.ifft2(1.0/w))/2.0, np.real(np.fft.ifft2(w))/2.0

def submatrices(sites, L, GX, GP):
    dx = (sites[:, 0][:, None] - sites[:, 0][None, :]) % L
    dy = (sites[:, 1][:, None] - sites[:, 1][None, :]) % L
    return GX[dx, dy], GP[dx, dy]

def gaussian_entropy(XA, PA, clip=1e-12):
    ev, U = np.linalg.eigh(XA)
    Xh = (U*np.sqrt(np.clip(ev, 1e-300, None))) @ U.T
    C = Xh @ PA @ Xh
    nu = np.sqrt(np.clip(np.linalg.eigvalsh(0.5*(C + C.T)), 0.25, None))
    nu = np.maximum(nu, 0.5 + clip)
    a, b = nu + 0.5, nu - 0.5
    return float(np.sum(a*np.log(a) - b*np.log(b)))

def square_sites(l, L, off=None):
    o = (L - l)//2 if off is None else off
    return np.array([(o + i, o + j) for i in range(l) for j in range(l)])

def strip_sites(rows, L):
    return np.array([(i, j) for i in rows for j in range(L)])

# ---------------- the two extractions ----------------
def fit_direct(ls, S, per_unit):
    """S = A*(per_unit*l) + B*ln(l) + C  ->  (A, B, C)"""
    M = np.vstack([per_unit*np.array(ls, float), np.log(ls), np.ones(len(ls))]).T
    coef, *_ = np.linalg.lstsq(M, np.array(S), rcond=None)
    pred = M @ coef
    ss = np.sum((np.array(S) - np.mean(S))**2)
    r2 = 1 - np.sum((np.array(S) - pred)**2)/ss if ss > 0 else float("nan")
    return coef[0], coef[1], coef[2], r2

def fit_increments(ls, S, per_unit):
    """differences kill C entirely: dS = A*per_unit*dl + B*ln(l2/l1)"""
    ls = np.array(ls, float); S = np.array(S)
    dS = S[1:] - S[:-1]
    M = np.vstack([per_unit*(ls[1:] - ls[:-1]), np.log(ls[1:]/ls[:-1])]).T
    coef, *_ = np.linalg.lstsq(M, dS, rcond=None)
    return coef[0], coef[1]

# ---------------- C1: synthetic no-log control ----------------
print("CONTROL C1 — synthetic data with NO log term; the fitter must return B~0")
rng = np.random.default_rng(5)
ls_syn = np.arange(4, 21, 2)
for noise in (0.0, 1e-6, 1e-4):
    S_syn = 0.0730*(4*ls_syn) + 1.234 + rng.normal(0, noise, ls_syn.size)
    _, B, _, _ = fit_direct(ls_syn, S_syn, 4)
    print(f"   noise {noise:.0e}: fitted B = {B:+.3e}   (true B = 0)")

# ---------------- main measurement ----------------
L, ls = 160, list(range(4, 21, 2))
masses = [0.01, 0.02]
results = {}
print(f"\nCORNER COEFFICIENT — squares on a periodic {L}x{L} lattice")
for m in masses:
    REG = make_regs(m)
    print(f"\n  mass m = {m}  (xi = {1/m:.0f}; largest square l/xi = {max(ls)*m:.2f})")
    print(f"  {'regulator':>13} {'A (area)':>11} {'B (log)':>11} {'a=-B/4':>10} "
          f"{'fit R^2':>9} {'B via increments':>18}")
    for nm in NAMES:
        GX, GP = kernels(L, REG[nm])
        S = [gaussian_entropy(*submatrices(square_sites(l, L), L, GX, GP)) for l in ls]
        A, B, C, r2 = fit_direct(ls, S, 4)
        A2, B2 = fit_increments(ls, S, 4)
        results[(m, nm)] = {"S": S, "A": A, "B": B, "a": -B/4, "r2": r2, "B_inc": B2}
        print(f"  {nm:>13} {A:11.5f} {B:+11.5f} {-B/4:10.5f} {r2:9.6f} {B2:+18.5f}")
    Av = np.array([results[(m, n)]["A"] for n in NAMES])
    av = np.array([results[(m, n)]["a"] for n in NAMES])
    ai = np.array([-results[(m, n)]["B_inc"]/4 for n in NAMES])
    sA = (Av.max()-Av.min())/Av.mean()*100
    sa = (av.max()-av.min())/abs(av.mean())*100
    si = (ai.max()-ai.min())/abs(ai.mean())*100
    print(f"  {'SPREAD':>13} {sA:10.1f}% {'':>11} {sa:9.1f}% {'':>9} {si:17.1f}%")
    results[("spread", m)] = {"area": sA, "corner_direct": sa, "corner_incr": si}

# ---------------- C2: physical no-corner control ----------------
print("\nCONTROL C2 — half-torus strips (NO corners), identical 3-parameter fit;")
print("             B must be consistent with zero on real data")
Ls_ctrl = [12, 16, 20, 24, 28]
REG_c = make_regs(0.02)
c2_B = {}                    # <- the WITHDRAWAL's numbers, captured not printed
for nm in NAMES:
    S = []
    for Lc in Ls_ctrl:
        GX, GP = kernels(Lc, REG_c[nm])
        S.append(gaussian_entropy(*submatrices(strip_sites(range(Lc//2), Lc), Lc, GX, GP)))
    A, B, C, r2 = fit_direct(Ls_ctrl, S, 2)
    c2_B[nm] = float(B)
    print(f"   {nm:>13}: A = {A:8.5f}   B = {B:+9.5f}   (must be ~0)   R^2 = {r2:.6f}")

# ---------------- continuum refinement ----------------
print("\nCONTINUUM REFINEMENT — hold physics fixed (m*L, l/L), refine the lattice")
cont = []
for s in (1, 2):
    Lc, mc = 160*s, 0.01/s
    lsc = [l*s for l in ls]
    REGc = make_regs(mc)
    A_s, a_s = [], []
    for nm in NAMES:
        GX, GP = kernels(Lc, REGc[nm])
        S = [gaussian_entropy(*submatrices(square_sites(l, Lc), Lc, GX, GP)) for l in lsc]
        A, B, C, r2 = fit_direct(lsc, S, 4)
        A_s.append(A); a_s.append(-B/4)
    A_s, a_s = np.array(A_s), np.array(a_s)
    spA = (A_s.max()-A_s.min())/A_s.mean()*100
    spa = (a_s.max()-a_s.min())/abs(a_s.mean())*100
    cont.append({"s": s, "L": Lc, "m": mc, "area_spread": spA, "corner_spread": spa,
                 "corner_values": [float(v) for v in a_s]})
    print(f"   s={s}  L={Lc:4d}  m={mc:.4f}:  area spread {spA:6.1f}%   "
          f"corner spread {spa:6.1f}%")

print("\nVERDICT")
for m in masses:
    r = results[("spread", m)]
    print(f"  m={m}: area {r['area']:.1f}%   corner {r['corner_direct']:.1f}% (direct) "
          f"/ {r['corner_incr']:.1f}% (increments)")
print(f"  refinement: area {cont[0]['area_spread']:.1f}% -> {cont[1]['area_spread']:.1f}%   "
      f"corner {cont[0]['corner_spread']:.1f}% -> {cont[1]['corner_spread']:.1f}%")

out = {
    "question": "kappa is regulator-junk in every regime. Is the CORNER coefficient, "
                "in the same run, regulator-independent?",
    "geometry": {"corner_angle": "pi/2 (square, lattice-aligned)", "L": L, "sides": ls,
                 "note": "theta != pi/2 needs staircase boundaries whose steps are "
                         "themselves corners - deliberately not attempted"},
    "regulators": NAMES,
    "by_mass": {str(m): {n: {k: (v if not isinstance(v, list) else [round(float(x), 8) for x in v])
                             for k, v in results[(m, n)].items()} for n in NAMES}
                for m in masses},
    "spreads": {str(m): results[("spread", m)] for m in masses},
    "continuum": cont,
}
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corner_coefficient.json")
with open(ART, "w") as fh:
    json.dump(out, fh, indent=1, default=float)
print("\nsaved -> qsim/corner_coefficient.json")

# =============================================================================
# C2 FAILED (B ~ -0.496 on a provably corner-free geometry). C1 passed, so the
# fitter is not manufacturing logs — the CONTROL GEOMETRY is the suspect.
#
# Diagnosis: the half-torus strip scales the REGION with the LATTICE (width L/2
# on an LxL torus), at L = 12..28 with xi = 50 >> L. So the strip sits in the
# finite-size-dominated regime, where the k=0 mode alone contributes
# 1/(2 L^2 m) — which varies by 5.4x across that L range. Real non-area
# L-dependence, which a 3-parameter fit will happily absorb into ln(L).
# That is a defect of my control, not of the measurement: the SQUARES are
# measured at fixed L=160 with l/L <= 0.125, where the zero mode contributes a
# constant ~0.002 independent of l.
#
# Two follow-ups. (i) TEST the diagnosis rather than assert it: push the strip
# control into the gapped regime (xi << L) where finite-size effects are cut
# off; if B -> 0 the explanation holds. (ii) Build the control I should have
# built: rectangles MINUS squares. An l x 2l rectangle and an l x l square both
# have exactly four pi/2 corners, so the corner log CANCELS in the difference,
# leaving pure area. Same lattice, same geometry family, same fitter — and it
# can still fail.
# =============================================================================
print("\n" + "="*72)
print("C2 DIAGNOSIS — was the strip failure finite-size? push xi << L and watch B")
print(f"   {'mass':>7} {'xi':>6} {'xi/L_max':>9} " + "".join(f"{n[:9]:>11}" for n in NAMES))
c2_diag = {}
for mc in (0.02, 0.1, 0.3, 0.6):
    row = []
    REGd = make_regs(mc)
    for nm in NAMES:
        S = []
        for Lc in Ls_ctrl:
            GX, GP = kernels(Lc, REGd[nm])
            S.append(gaussian_entropy(*submatrices(strip_sites(range(Lc//2), Lc), Lc, GX, GP)))
        row.append(fit_direct(Ls_ctrl, S, 2)[1])
    c2_diag[str(mc)] = {"xi_over_Lmax": 1/mc/max(Ls_ctrl),
                        "B": {n: float(v) for n, v in zip(NAMES, row)}}
    print(f"   {mc:7.2f} {1/mc:6.1f} {1/mc/max(Ls_ctrl):9.2f} "
          + "".join(f"{v:+11.5f}" for v in row))

print("\nCONTROL C2' — rectangles MINUS squares: identical corner content (four")
print("              pi/2 corners each), so the corner log must CANCEL -> B ~ 0")
REGp = make_regs(0.01)
def rect_sites(l, w, Lc):
    ox, oy = (Lc - l)//2, (Lc - w)//2
    return np.array([(ox + i, oy + j) for i in range(l) for j in range(w)])
c2p = {}
for nm in NAMES:
    GX, GP = kernels(L, REGp[nm])
    dS = []
    for l in ls:
        S_sq = gaussian_entropy(*submatrices(square_sites(l, L), L, GX, GP))
        S_re = gaussian_entropy(*submatrices(rect_sites(l, 2*l, L), L, GX, GP))
        dS.append(S_re - S_sq)
    A, B, C, r2 = fit_direct(ls, dS, 2)
    c2p[nm] = B
    print(f"   {nm:>13}: A = {A:8.5f}   B = {B:+9.5f}   (must be ~0)   R^2 = {r2:.6f}")
bs = np.array(list(c2p.values()))
print(f"   |B| max = {np.abs(bs).max():.5f}  vs the measured corner log |B| ~ 0.047 "
      f"-> {np.abs(bs).max()/0.047*100:.1f}% of signal")

# ---------------------------------------------------------------------------
# The controls run AFTER the first artifact write, so their numbers -- including
# the FAILED C2 -- were terminal-only. bridge's 16a: provenance can attach to the
# wrong object. The run was committed; the REDUCTION evaporated. An unreproducible
# withdrawal is worse than an unreproducible claim: a reader can discount a
# positive result they cannot re-derive, but has to take a retraction on trust.
# ---------------------------------------------------------------------------
out["controls"] = {
    "C2_strip_FAILED": {
        "B_by_regulator": c2_B,
        "worst_abs_B": max(abs(v) for v in c2_B.values()),
        "verdict": "FAILED on a provably corner-free geometry; kept, not explained away",
    },
    "C2_finite_size_diagnosis": c2_diag,
    "C2prime_rect_minus_square": {
        "B_by_regulator": {k: float(v) for k, v in c2p.items()},
        "worst_abs_B": float(np.abs(bs).max()),
        "floor_percent_of_corner_signal": float(np.abs(bs).max()/0.047*100),
    },
}
with open(ART, "w") as fh:
    json.dump(out, fh, indent=1, default=float)
print(f"   re-saved with controls -> {ART}")

# =============================================================================
# FIGURE + final verdict against the measured systematic floor
# =============================================================================
FLOOR = np.abs(bs).max()/0.047*100          # C2' residual as % of corner signal
print(f"\nFINAL — every spread read against the C2' systematic floor ({FLOOR:.1f}%)")
print(f"   area  coefficient : {results[('spread',0.01)]['area']:.1f}%  "
      f"-> {cont[1]['area_spread']:.1f}% refined   [{'ABOVE' if cont[1]['area_spread']>FLOOR else 'below'} floor]")
print(f"   corner coefficient: {results[('spread',0.01)]['corner_direct']:.1f}%  "
      f"-> {cont[1]['corner_spread']:.1f}% refined   [{'ABOVE' if cont[1]['corner_spread']>FLOOR else 'below'} floor]")
print("   reading: kappa's regulator dependence is real and permanent; the corner")
print("   coefficient's spread sits at or below what this method can resolve, and")
print("   falls further under refinement. Consistent with exactly zero.")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
cols = {"nn":"tab:blue","improved":"tab:green","higher_deriv":"tab:red","smeared":"tab:purple"}
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

for nm in NAMES:
    ax[0].plot(ls, results[(0.01, nm)]["S"], "o-", color=cols[nm], lw=1.6, ms=5, label=nm)
ax[0].set_xlabel("square side  $\\ell$"); ax[0].set_ylabel("entanglement entropy  $S$")
ax[0].set_title("Squares: four regulators, four different\narea slopes")
ax[0].legend(fontsize=8)

Av = np.array([results[(0.01,n)]["A"] for n in NAMES])
av = np.array([results[(0.01,n)]["a"] for n in NAMES])
x = np.arange(4)
ax[1].bar(x-0.2, Av/Av.mean(), 0.38, color="tab:red", alpha=.85, label="area coeff (norm.)")
ax[1].bar(x+0.2, av/av.mean(), 0.38, color="tab:blue", alpha=.85, label="corner coeff (norm.)")
ax[1].axhline(1, color="k", lw=1, ls="--")
ax[1].set_xticks(x); ax[1].set_xticklabels(NAMES, rotation=20, fontsize=8)
ax[1].set_ylabel("value / mean")
ax[1].set_title(f"Same run, same regulators:\narea spreads {results[('spread',0.01)]['area']:.0f}%, corner {results[('spread',0.01)]['corner_direct']:.1f}%")
ax[1].legend(fontsize=8)

ss = [c["s"] for c in cont]
ax[2].semilogy(ss, [c["area_spread"] for c in cont], "s-", color="tab:red", lw=2, ms=9,
               label="area coeff spread")
ax[2].semilogy(ss, [c["corner_spread"] for c in cont], "o-", color="tab:blue", lw=2, ms=9,
               label="corner coeff spread")
ax[2].axhspan(0, FLOOR, color="gray", alpha=0.18)
ax[2].text(1.05, FLOOR*0.55, f"method floor ({FLOOR:.1f}%)\nfrom control C2'", fontsize=8, color="dimgray")
ax[2].set_xticks(ss); ax[2].set_xlabel("$s$ = lattice refinement at fixed physics")
ax[2].set_ylabel("across-regulator spread (%)")
ax[2].set_title("Refinement separates them:\ncorner falls under the floor, area does not")
ax[2].legend(fontsize=8)

fig.suptitle("Corners are universal where the area law is not — one lattice, four regulators",
             fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("corner_coefficient.png", dpi=125)
print("saved -> qsim/corner_coefficient.png")
