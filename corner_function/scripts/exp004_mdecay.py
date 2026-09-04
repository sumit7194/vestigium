import sys, numpy as np, time; sys.path.insert(0,'scripts'); import exp004_ch_solver as cs
from math import pi
degs=[5,15,26.565,45,90,135]; xs=np.radians(degs)
print("M      " + " ".join(f"F({d:>6.1f}deg)" for d in degs) + "   H1        ser/ode")
guess=None
for M in [0.5001,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7]:
    t0=time.time(); sol, rn, guess, H = cs.integrate(M, 0.5, np.radians(4), guess=guess)
    print(f"{M:6.3f} " + " ".join(f"{sol.sol(x)[6].real:+.4e}" for x in xs) + f"   {H.c[1].real:+.2e}  {sol.consistency:.1e}  [{time.time()-t0:.0f}s]", flush=True)
