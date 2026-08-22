#!/usr/bin/env python3
"""The s=6 corner rung — the point that decides whether the s^-2 constant's
1.3% scatter over s=3,4,5 is noise or drift.

This was recorded as permanently blocked this afternoon. It was not: the block
was an arithmetic comparison (14.09 GB > ~10 GB available) that nobody tested.
The user asked whether we tried it or only computed it. We had only computed it.
The bridge then RAN their s=6 in 929 s with a ~7.8 GB peak against a 13.55 GB
prediction -- their law over-predicted by 40% at a x1.20 extrapolation, after
hold-out validation and residual checks. Mine extrapolates x1.85, so 14.09 GB
is the least certified number in this repo, not the most.

CALIBRATION FIRST. Run with --calibrate to reproduce the KNOWN s=1 answer
(corner spread 1.69%) before trusting this code on a resolution nobody has run.
The functions here are copied from corner_coefficient.py rather than imported,
because that module executes its whole study on import -- so the calibration is
also what proves the copy is faithful.

Regulators run SEQUENTIALLY so the memory peak stays per-regulator rather than
accumulating, and RSS plus swapouts are sampled throughout: swapouts is the
unambiguous paging signal on this box (it was identically 0 all day), whereas
`free` sits near zero routinely while gigabytes are reclaimable.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "4"

import numpy as np


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


def square_sites(l, L):
    o = (L - l)//2
    return np.array([(o + i, o + j) for i in range(l) for j in range(l)])


def fit_direct(ls, S, per_unit):
    M = np.vstack([per_unit*np.array(ls, float), np.log(ls), np.ones(len(ls))]).T
    coef, *_ = np.linalg.lstsq(M, np.array(S), rcond=None)
    return coef[0], coef[1], coef[2]


# ---------------- instrumentation ----------------
_PID = str(os.getpid())
STATE = {"phase": "init"}
PEAK = {"rss_mb": 0.0, "phase": "init", "swapouts": 0}
_stop = False


def _swapouts():
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    m = re.search(r"Swapouts:\s+(\d+)", out)
    return int(m.group(1)) if m else -1


def sampler():
    while not _stop:
        o = subprocess.run(["ps", "-o", "rss=", "-p", _PID],
                           capture_output=True, text=True).stdout.strip()
        if o.isdigit():
            mb = int(o)/1024
            if mb > PEAK["rss_mb"]:
                PEAK["rss_mb"], PEAK["phase"] = mb, STATE["phase"]
        PEAK["swapouts"] = max(PEAK["swapouts"], _swapouts())
        time.sleep(1.0)


def run(s, ls_base=range(4, 21, 2), L_base=160, m_base=0.01):
    """One resolution. Regulators sequential so the peak stays per-regulator."""
    L, m = L_base*s, m_base/s
    ls = [l*s for l in ls_base]
    regs = make_regs(m)
    out = {}
    for nm in NAMES:
        t0 = time.time()
        STATE["phase"] = f"{nm}:kernels"
        GX, GP = kernels(L, regs[nm])
        S = []
        for l in ls:
            STATE["phase"] = f"{nm}:entropy l={l}"
            XA, PA = submatrices(square_sites(l, L), L, GX, GP)
            S.append(gaussian_entropy(XA, PA))
            del XA, PA
        A, B, C = fit_direct(ls, S, 4)
        out[nm] = dict(A=A, B=B, S=S, seconds=round(time.time()-t0, 1))
        print(f"   {nm:>13}  B = {B:+.6f}   {out[nm]['seconds']:7.1f}s   "
              f"peak {PEAK['rss_mb']/1024:.2f} GB   swapouts {PEAK['swapouts']:,}",
              flush=True)
        del GX, GP
    Bs = [abs(out[n]["B"]) for n in NAMES]
    spread = (max(Bs) - min(Bs))/(sum(Bs)/len(Bs))*100
    As = [abs(out[n]["A"]) for n in NAMES]
    area = (max(As) - min(As))/(sum(As)/len(As))*100
    return dict(s=s, L=L, m=m, ls=ls, per_regulator=out,
                corner_spread_percent=spread, area_spread_percent=area,
                peak_gb=round(PEAK["rss_mb"]/1024, 2), peak_phase=PEAK["phase"],
                swapouts=PEAK["swapouts"])


if __name__ == "__main__":
    s = 1 if "--calibrate" in sys.argv else 6
    t = threading.Thread(target=sampler, daemon=True)
    t.start()
    base = _swapouts()
    print(f"{'CALIBRATION s=1 (known answer: corner spread 1.69%)' if s == 1 else 'S=6 RUN'}"
          f"   swapouts at start: {base:,}", flush=True)
    t0 = time.time()
    r = run(s)
    _stop = True
    r["swapouts_delta"] = PEAK["swapouts"] - base
    r["total_seconds"] = round(time.time()-t0, 1)
    print(f"\n   corner spread {r['corner_spread_percent']:.4f}%   "
          f"area spread {r['area_spread_percent']:.2f}%")
    print(f"   peak {r['peak_gb']:.2f} GB in {r['peak_phase']}   "
          f"swapouts +{r['swapouts_delta']:,}   total {r['total_seconds']:.0f}s")
    if s == 1:
        err = abs(r["corner_spread_percent"] - 1.69)/1.69*100
        print(f"\n   CALIBRATION vs known 1.69%: {err:.1f}% off  "
              f"{'PASS' if err < 5 else '*** FAIL -- copy is not faithful ***'}")
    fn = f"corner_s{s}.json"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fn), "w") as fh:
        json.dump(r, fh, indent=1)
    print(f"   saved -> qsim/{fn}")
