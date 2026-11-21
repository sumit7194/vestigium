# Quantum's verification driver for Neon T33 (non-rigorous float). Imports the delivered module read-only.
# usage: python -I verify.py <dir of mn_splitting_scout.py> <comma list of beta> [n list, default 32,64,128]
import sys; sys.path.insert(0, sys.argv[1])
import numpy as np, mn_splitting_scout as N
betas = [float(x) for x in sys.argv[2].split(",")]
ns = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [32, 64, 128]
rg, tg = N.R_U_BASE, np.arccos(N.Z_M_BASE)
def zs(r):
    return " ".join(f"{z/np.pi:.4f}pi({s:+.2e})" for z, s in r['zeros'])
for b in betas:
    for n in ns:
        sec = N.compute_section_points(b, r_guess=rg, th_guess=tg, n_samples=n, rtol=2e-12, atol=2e-13)
        rg, tg = sec['r0'], sec['th0']
        Ks = [K for K in (12, 16, 20, 24, 30, 40) if 2 * K + 1 <= (2 * n) // 3]
        for K in Ks:
            r = N.analyze_section(sec, interp='spectral', K_deg=K)
            print(f"b {b:+.9f} n {n:3d} spec K{K:2d} A1 {r['A1']:+.6e} A2 {r['A2']:+.4e} A3 {r['A3']:+.3e} A4 {r['A4']:+.2e} "
                  f"forb {r['max_forb']:.1e} resid {r['fit_resid']:.1e} Kerr {sec['max_K_err']:.1e} lam_u {sec['lam_u']:.3f} | nz {len(r['zeros'])}: {zs(r)}", flush=True)
        r = N.analyze_section(sec, interp='cubic')
        print(f"b {b:+.9f} n {n:3d} cubic    A1 {r['A1']:+.6e} A2 {r['A2']:+.4e} A3 {r['A3']:+.3e} | nz {len(r['zeros'])}: {zs(r)}", flush=True)
        if n == ns[-1]:
            for m in ('geom_angle', 'arclength'):
                K = Ks[-1]
                r = N.analyze_section(sec, interp='spectral', K_deg=K, matching=m)
                print(f"b {b:+.9f} n {n:3d} {m:10s} K{K} A1 {r['A1']:+.6e} A2 {r['A2']:+.4e} | nz {len(r['zeros'])}: {zs(r)}", flush=True)
