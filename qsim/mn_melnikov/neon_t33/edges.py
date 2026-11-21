# Quantum's T33 checks: (1) A2 sensitivity to eps_init / rtol / n at beta*; (2) the convention-invariant window edges
# (beta where the slope of dK_r at the symmetric zeros pi/2 and 0 vanishes) and beta* (A1 = 0, Kerr-angle convention).
# usage: python -I edges.py <dir of mn_splitting_scout.py>
import sys; sys.path.insert(0, sys.argv[1])
import numpy as np, scipy.optimize as opt, mn_splitting_scout as N
BS = -0.206224720
rg, tg = N.R_U_BASE, np.arccos(N.Z_M_BASE)
sec0 = N.compute_section_points(BS, n_samples=32, rtol=2e-12, atol=2e-13); rg, tg = sec0['r0'], sec0['th0']
def run(b, n=64, K=20, eps=1e-6, rtol=2e-12, atol=2e-13, matching='kerr_angle'):
    s = N.compute_section_points(b, r_guess=rg, th_guess=tg, n_samples=n, eps_init=eps, rtol=rtol, atol=atol)
    return N.analyze_section(s, interp='spectral', K_deg=K, matching=matching)
print("== (1) sensitivity at beta* =", BS, flush=True)
for kw in [dict(), dict(eps=5e-7), dict(eps=2e-6), dict(eps=2.5e-7), dict(rtol=5e-13, atol=5e-14), dict(n=256, K=40)]:
    r = run(BS, **kw)
    print(f"{str(kw):32s} A1 {r['A1']:+.5e} A2 {r['A2']:+.6e} A3 {r['A3']:+.3e} slope0 {r['slope_0']:+.5e} slope_pi2 {r['slope_pi2']:+.5e} nz {len(r['zeros'])}", flush=True)
print("== (2) edges (n 128, K 30)", flush=True)
for name, f, lo, hi in [
        ("beta* (A1=0, kerr_angle)", lambda b: run(b, n=128, K=30)['A1'], BS - 1e-6, BS + 1e-6),
        ("edge_pi2 (slope at pi/2 = 0, kerr)", lambda b: run(b, n=128, K=30)['slope_pi2'], BS - 3e-6, BS - 1.5e-6),
        ("edge_0 (slope at 0 = 0, kerr)", lambda b: run(b, n=128, K=30)['slope_0'], BS + 1.5e-6, BS + 3e-6),
        ("edge_pi2 (geom_angle)", lambda b: run(b, n=128, K=30, matching='geom_angle')['slope_pi2'], BS - 3e-6, BS - 1.5e-6),
        ("edge_0 (geom_angle)", lambda b: run(b, n=128, K=30, matching='geom_angle')['slope_0'], BS + 1.5e-6, BS + 3e-6)]:
    z = opt.brentq(f, lo, hi, xtol=1e-11)
    print(f"{name:38s} beta = {z:+.10f}  (beta - beta*_Neon = {z - BS:+.3e})", flush=True)
