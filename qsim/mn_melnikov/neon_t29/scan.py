"""Quantum's driver for T29 verification: beta values the T29 summary reports but the delivered script's grid omits.
Imports the delivered module read-only; prints one row per beta, two tolerances each."""
import sys, time
sys.path.insert(0, sys.argv[1])
import numpy as np
import mn_splitting_scout as N
betas = [float(b) for b in sys.argv[2].split(",")]
prev = None
for b in betas:
    t0 = time.time()
    rg, tg = (prev['r0'], prev['th0']) if prev else (N.R_U_BASE, np.arccos(N.Z_M_BASE))
    try:
        r1 = N.measure_splitting(b, r_guess=rg, th_guess=tg, rtol=1e-11, atol=1e-12)
        r2 = N.measure_splitting(b, r_guess=r1['r0'], th_guess=r1['th0'], rtol=2e-12, atol=2e-13)
        prev = r2
        print(f"{b:+.4f} r0 {r2['r0']:.5f} lam_u {r2['lam_u']:.4f} A1 {r2['A1']:+.6e} A1/b {r2['A1']/b:+.6e} A2 {r2['A2']:+.3e} "
              f"forb {r2['max_forb']:.1e} step {abs(r2['A1']-r1['A1']):.1e} slope0 {r2['slope_0']:+.5e} slopepi2 {r2['slope_pi2']:+.5e} "
              f"Kerr {r2['max_K_err']:.1e} {time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        print(f"{b:+.4f} FAILED: {e!r}", flush=True)
