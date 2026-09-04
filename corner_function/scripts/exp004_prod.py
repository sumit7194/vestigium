"""Production driver for EXP-004 (mp solver): parallel over (t, M) nodes, checkpointed per node.
  mode renyi2 : a = 1/2, real scalar   s_2(x) = 2 Int p^2 F dp
  mode ee     : a = 1/2 - i t, complex scalar (CHL09 eq 61):
                s_S(x) = Int_0^inf dt 2/cosh^2(pi t) Int_{1/2}^inf dM M sqrt(M^2-1/4) tr G_S,  tr G_S = 8 pi a(1-a) F
                = Int dt 2/cosh^2(pi t) * 8 pi (1/4 + t^2) * Int p^2 F dp   (real scalar = half)
Grids: p in [0,4] (n1 GL nodes) + [4, p_max] (n2 GL nodes); t in [0, t_max] GL nodes (weight 2/cosh^2(pi t)).
Usage: exp004_prod.py renyi2|ee  n1 n2 p_max  [nt t_max]  [workers]
"""
import sys, os, json, math, cmath, time, numpy as np
from multiprocessing import Pool
sys.path.insert(0, __file__.rsplit('/',1)[0])
DEG = [5,10,15,20,26.565,30,40,45,50,60,63.435,70,80,90,100,110,116.565,120,130,135,140,150,153.435,160,170]
XG = [math.radians(v) for v in DEG]
OUT = __file__.rsplit('/',1)[0] + "/exp004_nodes"

def branch_by_continuation(M, t, N, re_a, mode, path=None):
    """Physical series branch at a = re_a - i t, relative to the principal square root there.
    The local expansion has beta1^1 = +-sqrt(P b0/c0); the physical root is the continuous continuation of the
    validated branch (-1) at real a = 1/2 (t = 0). The continuous square root differs from the principal one by
    (-1)^(number of crossings of arg(P b0/c0) through +-pi along the path), so only boundary values are needed.
    Path: t' from 0 to t at fixed re_a (default); a custom list of complex a's may be given (fermion family).
    Returns (sign, None, crossings)."""
    import exp004_ch_solver as cs
    if path is None:
        n = max(2, int(math.ceil(t/0.002)) + 1)
        path = [complex(re_a, -t*k/(n-1)) for k in range(n)]
    def z_of(a):
        aa = a if abs(a.imag) > 0 else float(a.real)
        X10, X20, b0, c0 = cs.bc_values(M, aa); P = (aa*(aa-1) + M*M*(1+b0*c0))/(4*M*M); return complex(P*b0/c0)
    phases = np.unwrap([cmath.phase(z_of(a)) for a in path])
    crossings = int(round((phases[-1] - phases[0])/(2*math.pi)))      # net winding about the origin
    # principal sqrt flips sign at each crossing of the negative real axis; the net effect is (-1)^(net winding number)
    # but crossings back and forth cancel only in pairs -> count actual passages through arg = +-pi instead:
    raw = [cmath.phase(z_of(a)) for a in path]
    passages = sum(1 for k in range(1, len(raw)) if abs(raw[k] - raw[k-1]) > math.pi)
    sign = -1 * (-1)**passages
    return sign, None, passages

def worker(args):
    M, t, mode = args
    import mpmath as mp
    import exp004_mp as em
    fn = f"{OUT}/{mode}_M{M:.10f}_t{t:.10f}.json"
    if os.path.exists(fn): return json.load(open(fn))
    a = 0.5 if mode in ("renyi2", "dirac2") else (complex(0.5, -t) if mode == "ee" else complex(0.0, -t))
    t0 = time.time()
    try:
        N = int(2*round((1.6*abs(M) + 8)/2))
        if mode == "ee" and t > 0:
            sign, guess, flips = branch_by_continuation(M, t, N, 0.5, mode)
        elif mode == "dirac":
            # path from the validated real branch: a = 1/2 -> 1/2 - i t (vertical) -> -i t (horizontal), avoiding the pole at a = 0
            n1 = max(2, int(math.ceil(t/0.002)) + 1); n2 = 251
            path = [complex(0.5, -t*k/(n1-1)) for k in range(n1)] + [complex(0.5*(1 - k/(n2-1)), -t) for k in range(1, n2)]
            sign, guess, flips = branch_by_continuation(M, t, N, 0.5, mode, path=path)
        else:
            sign, guess, flips = -1, None, 0
        out, d = em.integrate_mp(M, a, math.radians(4), XG, branch=sign, guess=guess)
        F = [complex(out[x]) for x in XG]
        rec = {"M": M, "t": t, "F_re": [f.real for f in F], "F_im": [f.imag for f in F], "H1": complex(d['H'][1]).real, "H1_im": complex(d['H'][1]).imag,
               "H3": complex(d['H'][3]).real, "dps": mp.mp.dps, "N": len(d['H'])-1, "secs": time.time()-t0, "ok": True, "branch": sign, "flips": flips}
        if mode in ("dirac", "dirac2"):
            # CHL09 eq (59): tr G_D|odd / m = 2 tr G_S - 16 pi a(1-a) (4 beta1 X1 cos(x/2) - b B1 sin^2 x)/(M (4 beta1^2 - b^2 sin^2 x)),  tr G_S = 8 pi a(1-a) F.
            # The second term has a finite, nonzero x -> pi limit (0/0): (2 beta1^1 X1^0 - b0 B1^0)/(4 (beta1^1)^2 - b0^2); the vertex
            # contribution must vanish at x = pi, so subtract that limit per mass node (same regularisation as tr G_S in eq 72).
            aa = mp.mpc(a); Ma = mp.mpf(M); Psi = []
            be11, X10, b0, B10 = d['be1'][1], d['X1'][0], d['b'][0], d['B1'][0]
            Psi_pi = 16*mp.pi*aa*(1-aa)*(0 - (2*be11*X10 - b0*B10)/(2*Ma*(4*be11**2 - b0**2)))
            for x in XG:
                b_, X1_, be1_, B1_ = em.integrate_mp.last_outq[x]; xx = mp.mpf(x)
                val = 16*mp.pi*aa*(1-aa)*(out[x] - (4*be1_*X1_*mp.cos(xx/2) - b_*B1_*mp.sin(xx)**2)/(2*Ma*(4*be1_**2 - b_**2*mp.sin(xx)**2))) - Psi_pi
                Psi.append(complex(val))
            rec["Psi_re"] = [v.real for v in Psi]; rec["Psi_im"] = [v.imag for v in Psi]; rec["Psi_pi"] = [complex(Psi_pi).real, complex(Psi_pi).imag]
    except Exception as e:
        rec = {"M": M, "t": t, "ok": False, "err": repr(e), "secs": time.time()-t0}
    json.dump(rec, open(fn, "w")); return rec

if __name__ == "__main__":
    mode = sys.argv[1]; n1, n2, pmax = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    nt, tmax = (int(sys.argv[5]), float(sys.argv[6])) if mode in ("ee","dirac") else (1, 0.0)
    workers = int(sys.argv[7]) if len(sys.argv) > 7 else 10
    os.makedirs(OUT, exist_ok=True)
    x1, w1 = np.polynomial.legendre.leggauss(n1); x2, w2 = np.polynomial.legendre.leggauss(n2)
    ps = np.concatenate([2*(x1+1), 4 + 0.5*(pmax-4)*(x2+1)]); wps = np.concatenate([2*w1, 0.5*(pmax-4)*w2])
    if mode in ("ee","dirac"):
        xt, wt = np.polynomial.legendre.leggauss(nt); ts = 0.5*tmax*(xt+1); wts = 0.5*tmax*wt
    else:
        ts, wts = np.array([0.0]), np.array([1.0])
    jobs = [(float(np.sqrt(0.25 + p*p)), float(t), mode) for t in ts for p in ps]
    # largest M first so the slow ones start early
    jobs.sort(key=lambda j: j[0])
    print(f"{len(jobs)} nodes, {workers} workers", flush=True)
    t0 = time.time()
    with Pool(workers) as pool:
        recs = pool.map(worker, jobs, chunksize=1)
    print(f"done in {time.time()-t0:.0f}s; failures: {sum(1 for r in recs if not r['ok'])}", flush=True)
    # assemble
    idx = {(round(r['M'],10), round(r['t'],10)): r for r in recs if r['ok']}
    s = np.zeros(len(DEG)); sig = np.zeros(4)
    for it, t in enumerate(ts):
        inner = np.zeros(len(DEG)); innerH = np.zeros(4)
        for ip, p in enumerate(ps):
            M = float(np.sqrt(0.25 + p*p)); r = idx.get((round(M,10), round(float(t),10)))
            if r is None: continue
            inner += wps[ip]*p*p*np.array(r["F_re"]); innerH[0] += wps[ip]*p*p*r["H1"]; innerH[1] += wps[ip]*p*p*r["H3"]
        if mode in ("dirac", "dirac2"):
            # dirac : s_D = Int dt 1/(2 sinh^2(pi t)) * 2 Int_0^inf dm m^2 Psi_reg     (CHL09 eq 60; odd part -> even integrand)
            # dirac2: Renyi-2 Dirac, a = +-1/2 (CHL09 eq 6, n=2): s_2^D = (2/pi) Int_0^inf dm m^2 Psi_reg (two equal k-terms, eq 36-37 prefactor 1/(2 pi))
            innerP = np.zeros(len(DEG))
            for ip, p in enumerate(ps):
                M = float(np.sqrt(0.25 + p*p)); r = idx.get((round(M,10), round(float(t),10)))
                if r is None: continue
                innerP += wps[ip]*p*p*np.array(r["Psi_re"])
            s += (wts[it]*(1/(2*np.sinh(np.pi*t)**2))*2*innerP) if mode == "dirac" else (2/np.pi)*innerP
            continue
        pre = 2.0 if mode == "renyi2" else wts[it]*(2/np.cosh(np.pi*t)**2)*8*np.pi*(0.25 + t*t)/2   # /2 : real scalar
        s += pre*inner
        sig[0] += pre*innerH[0]/2       # sigma  : F = H1 d^2/2 + H3 d^4/4 + ...
        sig[1] += pre*innerH[1]/4       # sigma'
    res = {"mode": mode, "deg": DEG, "s": s.tolist(), "n1": n1, "n2": n2, "p_max": pmax, "nt": nt, "t_max": tmax,
           "sigma_from_H1": sig[0], "sigmap_from_H3": sig[1], "nodes": len(jobs), "failures": int(sum(1 for r in recs if not r['ok']))}
    json.dump(res, open(f"{OUT}/../exp004_{mode}_result_n{n1}_{n2}_p{pmax}_t{nt}.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
