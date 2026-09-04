"""Driver: mass integral over a Gauss-Legendre grid in p with continuation; Renyi-2 controls or the EE."""
import sys, json, time, numpy as np
from math import pi
sys.path.insert(0, __file__.rsplit('/',1)[0])
import exp004_ch_solver as cs

def mass_integral(a, nodes=32, p_max=3.5, x_grid=None, x_min=0.05, N=12, delta0=None, verbose=True):
    """Returns dict with F-integral Int p^2 F(x,M(p)) dp on x_grid, and coefficient integrals Int p^2 H_k dp for k=1,3,5."""
    xs, ws = np.polynomial.legendre.leggauss(nodes)
    ps = 0.5*p_max*(xs+1); wps = 0.5*p_max*ws
    order = np.argsort(-ps)                      # continuation from large p (small H) down to p->0 is less robust; go increasing p from the smallest
    order = np.argsort(ps)
    Fint = np.zeros(len(x_grid), dtype=complex); Hk = {1:0j,3:0j,5:0j,7:0j}
    guess=None; t0=time.time(); worst_res=0
    for i in order:
        p = ps[i]; M = np.sqrt(0.25 + p*p)
        sol, rn, guess, H = cs.integrate(M, a, x_min, N=N, delta0=delta0, guess=guess)
        worst_res = max(worst_res, rn)
        if sol.status != 0: print(f"  WARNING ivp status {sol.status} at p={p:.4f}", file=sys.stderr)
        F = np.array([sol.sol(x)[6] for x in x_grid])
        Fint += wps[i]*p*p*F
        for k in Hk: Hk[k] += wps[i]*p*p*H.c[k]
        if verbose: print(f"  p={p:7.4f} M={M:7.4f} H1={H.c[1].real:+.3e} F(pi/2)={sol.sol(pi/2)[6].real:+.3e} F(5deg)={sol.sol(np.radians(5))[6].real:+.3e} resid={rn:.1e} ser/ode@0.3={sol.consistency:.1e} diag={dict(cs.DIAG)}  [{time.time()-t0:5.1f}s]", file=sys.stderr)
    return Fint, Hk, worst_res

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv)>1 else "renyi2"
    nodes = int(sys.argv[2]) if len(sys.argv)>2 else 32
    pmax = float(sys.argv[3]) if len(sys.argv)>3 else 3.5
    deg = [5,10,15,20,26.565,30,40,45,50,60,63.435,70,80,90,100,110,116.565,120,130,135,140,150,153.435,160,170]
    x_grid = np.radians(deg)
    if mode == "renyi2":
        # CH07 eq (40), n=2, real scalar: s_2 = 2 Int p^2 F dp ; sigma_2 = Int p^2 H1 ; sigma_2' = Int p^2 H3/2 ; sigma_2'' = Int p^2 H5/3
        Fint, Hk, wr = mass_integral(0.5, nodes=nodes, p_max=pmax, x_grid=x_grid)
        s2 = 2*Fint.real
        out = {"mode":"renyi2","nodes":nodes,"p_max":pmax,"deg":deg,"s2_real_scalar":s2.tolist(),
               "sigma2":Hk[1].real,"sigma2p":Hk[3].real/2,"sigma2pp":Hk[5].real/3,"sigma2ppp":Hk[7].real/4,"worst_series_resid":wr}
        print(json.dumps(out, indent=1))
        print(f"\nCONTROLS (real scalar): sigma_2={out['sigma2']:.9e} vs 1/(48pi^2)={1/(48*pi**2):.9e} ratio {out['sigma2']*48*pi**2:.7f}")
        print(f"  sigma_2'={out['sigma2p']:.7e} vs (5+pi^2)/(960pi^4)={(5+pi**2)/(960*pi**4):.7e} ratio {out['sigma2p']/((5+pi**2)/(960*pi**4)):.6f}")
        print(f"  sigma_2''={out['sigma2pp']:.7e} vs Helmes/2={3.11534753e-5/2:.7e} ratio {out['sigma2pp']/(3.11534753e-5/2):.6f}")
        print(f"  sigma_2'''={out['sigma2ppp']:.7e} vs Helmes/2={3.12412616e-6/2:.7e} ratio {out['sigma2ppp']/(3.12412616e-6/2):.6f}")
        for d,v in zip(deg,s2):
            ref = {45:0.0453/2, 90:0.0130/2, 135:0.00273/2, 26.565:0.0881/2, 63.435:0.0267/2, 116.565:0.00572/2, 153.435:0.000923/2}.get(d)
            print(f"  s_2({d:7.3f} deg) = {v:.6e}" + (f"   [HHCWM16 alpha=2 complex/2: {ref:.5e}  ratio {v/ref:.4f}]" if ref else ""))
        json.dump(out, open(__file__.rsplit('/',1)[0]+f"/exp004_renyi2_n{nodes}_p{pmax}.json","w"), indent=1)
