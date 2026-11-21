import sys; sys.path.insert(0, sys.argv[1])
import numpy as np, mn_splitting_scout as N
prev=None
for b in [float(x) for x in sys.argv[2].split(",")]:
    rg,tg=(prev['r0'],prev['th0']) if prev else (N.R_U_BASE,np.arccos(N.Z_M_BASE))
    r=N.measure_splitting(b,r_guess=rg,th_guess=tg,n_samples=64,rtol=2e-12,atol=2e-13); prev=r
    print(f"{b:+.4f} A1 {r['A1']:+.6e} A1/b/2.86726e-3 {r['A1']/b/2.86726e-3:.5f} A2 {r['A2']:+.3e} forb {r['max_forb']:.1e} r0 {r['r0']:.4f} lam_u {r['lam_u']:.3f}",flush=True)
