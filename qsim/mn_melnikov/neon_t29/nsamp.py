import sys; sys.path.insert(0, sys.argv[1])
import numpy as np, mn_splitting_scout as N
prev=None
for b in [float(x) for x in sys.argv[2].split(",")]:
    rg,tg=(prev['r0'],prev['th0']) if prev else (N.R_U_BASE,np.arccos(N.Z_M_BASE))
    for n in (32,64,128):
        r=N.measure_splitting(b,r_guess=rg,th_guess=tg,n_samples=n,rtol=2e-12,atol=2e-13); prev=r
        fs0=2*r['A1']+4*r['A2']+6*r['A3']; fsp=-2*r['A1']+4*r['A2']-6*r['A3']
        print(f"b {b:+.4f} n {n:3d} A1 {r['A1']:+.6e} A2 {r['A2']:+.3e} A3 {r['A3']:+.3e} forb {r['max_forb']:.1e} | spline slope0 {r['slope_0']:+.5e} pi2 {r['slope_pi2']:+.5e} | fourier slope0 {fs0:+.5e} pi2 {fsp:+.5e}",flush=True)
