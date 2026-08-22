"""
BRIDGE ASK 2 — high-precision certification leg (mpmath, dps=60).

float64 verdict from entropic_hinge.py: the exact lattice S_rel is precision-
limited at the 10% level for ALL tested packets (clip bands ~1e1 %), because
the wedge modular weights live in exponentially small tails of the covariance
(nu - 1/2 ~ e^-100) that double precision cannot represent. So the identity
check is re-run here end-to-end in 60-digit arithmetic on a smaller chain:

  chain N=100 (wedge = 50 sites), m=0.10, open BC, exact DCT-II modes;
  M = 2 i Om * gamma^{1/2} arccoth(2iT) gamma^{-1/2}   (ordering bug-fixed,
  squeezed-mode regression test passes at 2e-16);
  packets (x0, sigma) = (14, 3.5) and (20, 5);
  clip = 1e-50 (irrelevant at dps 60 — that IS the point);
  report S_rel_exact vs 2*pi*SUM x T00 and the float64 deficit.
"""
import json
import os
import time
import numpy as np
from mpmath import mp, mpf, mpc, matrix, eigsy, eighe, sqrt as msqrt, log as mlog, \
    cos as mcos, pi as mpi

mp.dps = 60
t0 = time.time()

def log_(s):
    print(f"[{time.time()-t0:7.1f}s] {s}", flush=True)

def build_M(N, m):
    """modular matrix of the reduced right-half vacuum, dps-60 exact."""
    nA = N//2
    ks = [mpi*n/N for n in range(N)]
    oms = [msqrt(m*m + 2 - 2*mcos(k)) for k in ks]
    sites = list(range(nA, N))
    norms = [mpf(N)] + [mpf(N)/2]*(N-1)
    XA = matrix(nA, nA); PA = matrix(nA, nA)
    for a, i in enumerate(sites):
        for b, j in enumerate(sites):
            if b < a:
                XA[a, b] = XA[b, a]; PA[a, b] = PA[b, a]; continue
            sx = mpf(0); sp = mpf(0)
            for n in range(N):
                vv = mcos(ks[n]*(i + mpf("0.5")))*mcos(ks[n]*(j + mpf("0.5")))/norms[n]
                sx += vv/(2*oms[n]); sp += vv*oms[n]/2
            XA[a, b] = sx; PA[a, b] = sp
    log_(f"N={N}: covariance done.")
    tw = 2*nA
    gamma = matrix(tw, tw)
    for a in range(nA):
        for b in range(nA):
            gamma[a, b] = XA[a, b]; gamma[nA+a, nA+b] = PA[a, b]
    Om = matrix(tw, tw)
    for a in range(nA):
        Om[a, nA+a] = mpf(1); Om[nA+a, a] = mpf(-1)
    E, U = eigsy(gamma)
    gh = matrix(tw, tw); ghi = matrix(tw, tw)
    sqE = [msqrt(E[i]) for i in range(tw)]
    for a in range(tw):
        for b in range(tw):
            s1 = mpf(0); s2 = mpf(0)
            for k in range(tw):
                s1 += U[a, k]*sqE[k]*U[b, k]
                s2 += U[a, k]/sqE[k]*U[b, k]
            gh[a, b] = s1; ghi[a, b] = s2
    log_(f"N={N}: gamma^(+-1/2) done.")
    T = gh*Om*gh
    iT = matrix(tw, tw)
    for a in range(tw):
        for b in range(tw):
            iT[a, b] = mpc(0, 1)*T[a, b]
    W_E, W = eighe(iT)
    log_(f"N={N}: eighe done.")
    clip = mpf("1e-50")
    ac = []
    for i in range(tw):
        w = W_E[i]
        if abs(w) < mpf("0.5") + clip:
            w = (mpf("0.5") + clip)*(1 if w >= 0 else -1)
        ac.append(mlog((2*w + 1)/(2*w - 1))/2)
    F = matrix(tw, tw)
    for a in range(tw):
        for b in range(tw):
            s = mpc(0)
            for k in range(tw):
                s += W[a, k]*ac[k]*W[b, k].conjugate()
            F[a, b] = s
    Mc = (Om*gh)*F*ghi
    M = matrix(tw, tw)
    for a in range(tw):
        for b in range(tw):
            M[a, b] = 2*(mpc(0, 1)*Mc[a, b]).real
    log_(f"N={N}: M done.")
    return M, sites, tw

def run_case(M, sites, tw, N, m, x0, sig):
    xs = [j - N/2 + 0.5 for j in range(N)]
    f = np.array([float(np.exp(-((x - x0)**2)/(4.0*sig*sig))) for x in xs])
    d = matrix(tw, 1)
    for a, j in enumerate(sites):
        d[a] = mpf(repr(float(f[j])))
    Md = M*d
    s = mpf(0)
    for a in range(tw):
        s += d[a]*Md[a]
    site = 0.5*float(m)**2*f*f
    df = f[1:] - f[:-1]
    xl = np.arange(N-1) - N/2 + 1.0
    tgt = 2*np.pi*(np.sum(np.array(xs)*site) + np.sum(xl*0.5*df*df))
    return float(s/2), float(tgt)

# chain A (N=100, m=0.10) + chain B: same PHYSICAL setup on a 1.6x finer lattice
# (lengths x1.6, mass /1.6) -> deviations should drop if they are lattice artifacts
chains = [
    (100, mpf("0.10"),   [(10, 2.5), (14, 3.5), (20, 5.0)]),
    (160, mpf("0.0625"), [(16, 4.0), (22.4, 5.6), (32, 8.0)]),
]
results = []
for N, m, packets in chains:
    M, sites, tw = build_M(N, m)
    for (x0, sig) in packets:
        Se, St = run_case(M, sites, tw, N, m, x0, sig)
        dev = (Se - St)/St*100
        results.append({"x0": x0, "sigma": sig, "m": float(m), "N": N,
                        "S_rel_exact_mp60": round(Se, 8),
                        "S_rel_boost_formula": round(St, 8),
                        "deviation_percent": round(dev, 4)})
        log_(f"N={N} case (x0={x0}, sigma={sig}):  S_exact={Se:.6f}  "
             f"target={St:.6f}  dev={dev:+.3f}%")

print("\ncontinuum trend (same physical packet, lattice 1.6x finer):")
for i in range(3):
    a, b = results[i], results[i+3]
    print(f"  packet {i+1}: dev {a['deviation_percent']:+.3f}% (N=100) -> "
          f"{b['deviation_percent']:+.3f}% (N=160)")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hinge_mp_certification.json"), "w") as fh:
    json.dump({"leg": "high-precision certification (dps=60)",
               "results": results,
               "note": "float64 leg is precision-limited (~10% clip bands); "
                       "this mp leg resolves all modular weights exactly"}, fh, indent=1)
log_("saved -> qsim/hinge_mp_certification.json")
