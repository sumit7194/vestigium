#!/usr/bin/env python3
"""MEASURE where the corner study's memory peak is, and in which phase.

Written instead of projecting, because two projections failed badly today:
ansatz's 4.75 GiB/prime measured the rank step while the assembly preceded it
and was 8x larger, and the bridge's s=6 estimate scaled L when l governs.

The bridge's finding is the reason this reports a PHASE and not just a number:
their wrong model (scale L^2, peak in the correlators) and the measured truth
(scale l, peak in the entropy step) agreed to 1.5% on magnitude. A model can be
wrong about the parameter, wrong about the phase, and still land on the number
-- at which point the number confirms the wrong model and the investigation
stops. The magnitude can be rationalised; a peak in the wrong phase cannot.

So the question here is not "how big" but "which parameter, in which phase",
and it is answered by varying L at fixed l and l at fixed L and watching where
the high-water mark actually lands.
"""
import json
import os
import subprocess
import threading
import time

import numpy as np


# CURRENT RSS, not the high-water mark. The first version used
# resource.getrusage().ru_maxrss, which (a) is a MAXIMUM that never falls, so
# every per-point "peak" was really the running max over the whole process and
# the vary-L comparison was an artifact of monotonicity, and (b) returns BYTES
# on macOS while my unit heuristic tested against 1<<40 -- a threshold that
# never fires -- so every number was 1024x too large. It printed 721 GB on a
# 16 GB machine and I nearly read it as data.
_PID = str(os.getpid())


def rss_mb():
    out = subprocess.run(["ps", "-o", "rss=", "-p", _PID],
                         capture_output=True, text=True).stdout.strip()
    return int(out)/1024 if out.isdigit() else float("nan")


PHASE = {"name": "init"}
SAMPLES = []
_stop = False


def sampler():
    while not _stop:
        SAMPLES.append((PHASE["name"], rss_mb()))
        time.sleep(0.02)


def K2_of(kx, ky):
    return (2 - 2*np.cos(kx)) + (2 - 2*np.cos(ky))


def reg_nn(m):
    return lambda kx, ky: m*m + K2_of(kx, ky)


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


def run(L, l, m=0.01):
    """One (L, l) point, RSS attributed to the phase it occurred in."""
    base = len(SAMPLES)
    PHASE["name"] = "kernels"
    GX, GP = kernels(L, reg_nn(m))
    PHASE["name"] = "submatrices"
    XA, PA = submatrices(square_sites(l, L), L, GX, GP)
    PHASE["name"] = "entropy"
    S = gaussian_entropy(XA, PA)
    PHASE["name"] = "idle"
    del GX, GP, XA, PA
    seen = SAMPLES[base:]
    if len(seen) < 3:
        # Too fast to sample. Reporting 0.0 MB / phase "?" as though it were a
        # measurement is exactly the false pass this probe exists to avoid.
        return dict(L=L, l=l, S=S, valid=False,
                    why=f"only {len(seen)} samples -- too fast to attribute")
    peak_mb = max(v for _, v in seen)
    by_phase = {}
    for ph, v in seen:
        by_phase[ph] = max(by_phase.get(ph, 0.0), v)
    peak_phase = max(by_phase, key=by_phase.get) if by_phase else "?"
    return dict(L=L, l=l, S=S, valid=True, peak_mb=round(peak_mb, 1),
                peak_phase=peak_phase,
                by_phase={k: round(v, 1) for k, v in by_phase.items()})


def _one_point():
    """Run exactly one (L, l) point in THIS process and print it as JSON.

    Each point needs a FRESH PROCESS. Python does not return freed memory to
    the OS promptly, so a long-lived process carries the high-water mark of
    every earlier point: after l=50 the RSS stayed at 705 MB and the following
    L=240 l=30 point -- which really costs about 99 MB -- read 705 MB too. The
    vary-L comparison was measuring the probe's own history, not the point, and
    it looked like a clean result showing L does not matter. It would have been
    the RIGHT CONCLUSION reached by an invalid route, which today has been the
    most expensive kind.
    """
    import sys
    L, l = int(sys.argv[2]), int(sys.argv[3])
    t = threading.Thread(target=sampler, daemon=True)
    t.start()
    r = run(L, l)
    print(json.dumps(r))


if __name__ == "__main__":
    import subprocess as sp
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--point":
        _one_point()
        raise SystemExit(0)

    def point(L, l):
        out = sp.run([sys.executable, os.path.abspath(__file__), "--point",
                      str(L), str(l)], capture_output=True, text=True).stdout
        return json.loads(out.strip().splitlines()[-1])

    def show(tag, r):
        if r["valid"]:
            print(f"   {tag}   peak {r['peak_mb']:7.1f} MB   in {r['peak_phase']:12s}"
                  f" {r['by_phase']}")
        else:
            print(f"   {tag}   INVALID -- {r['why']}")

    rows = []
    print("VARY l AT FIXED L=160   (each point in a fresh process)")
    for l in (30, 40, 50, 60):
        r = point(160, l); rows.append(r); show(f"l={l:3d}", r)

    print("\nVARY L AT FIXED l=40   (each point in a fresh process)")
    for L in (160, 240, 320):
        r = point(L, 40); rows.append(r); show(f"L={L:3d}", r)

    vl = [r for r in rows if r["L"] == 160 and r["valid"]]
    vL = [r for r in rows if r["l"] == 40 and r["valid"]]
    print("\nWHICH PARAMETER GOVERNS THE PEAK")
    if len(vl) >= 2:
        f = vl[-1]["peak_mb"]/vl[0]["peak_mb"]
        print(f"   l {vl[0]['l']} -> {vl[-1]['l']} (x{vl[-1]['l']/vl[0]['l']:.1f}): "
              f"peak x{f:.2f}")
    if len(vL) >= 2:
        f = vL[-1]["peak_mb"]/vL[0]["peak_mb"]
        print(f"   L {vL[0]['L']} -> {vL[-1]['L']} (x{vL[-1]['L']/vL[0]['L']:.1f}): "
              f"peak x{f:.2f}")

    print("\nHOLD-OUT VALIDATION  (fit the smaller points, predict the largest)")
    # An extrapolation nobody has tested is what cost
    # ansatz rank 4 and the bridge their s=6 range. Fit the smaller points,
    # predict the largest, compare against its measurement.
    import math
    base = min(r["by_phase"]["init"] for r in vl)
    pts = [(r["l"], r["peak_mb"] - base) for r in vl]
    holdout = []
    for hold in (60, 50):
        fit = [(l, v) for l, v in pts if l < hold]
        if len(fit) < 2:
            continue
        xs = [math.log(l) for l, _ in fit]
        ys = [math.log(v) for _, v in fit]
        n = len(xs); sx = sum(xs); sy = sum(ys)
        sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
        e = (n*sxy - sx*sy)/(n*sxx - sx*sx)
        a = math.exp((sy - e*sx)/n)
        pred = a*hold**e + base
        meas = next(r["peak_mb"] for r in vl if r["l"] == hold)
        holdout.append(dict(held_out=hold, fitted_exponent=round(e, 3),
                            predicted_mb=round(pred, 1), measured_mb=meas,
                            error_percent=round(abs(pred-meas)/meas*100, 2)))
        print(f"   fit l<{hold} (exp {e:.2f}) -> predict {pred:7.1f} MB, "
              f"measured {meas:7.1f} MB, {abs(pred-meas)/meas*100:.1f}% out")

    out = dict(
        question="which parameter and which phase govern the memory peak?",
        holdout_validation=holdout,
        cross_check=dict(
            note=("bridge measured their s=5 peak independently, different study, "
                  "same n=l^2 matrix structure, peak also in the entropy phase"),
            their_clean_measurement_gb=6.54,
            their_earlier_contaminated_gb=5.92,
            my_prediction_at_l100_gb=6.96,
            agreement_percent=6.4,
            correction=("I first cited 6.96 vs 5.92 as '18% apart'. That 5.92 came "
                        "from their ru_maxrss-contaminated run, which UNDERSTATED "
                        "the peak. Against their clean 6.54 the agreement is 6.4%. "
                        "My cross-check was quoted against a number since retracted "
                        "by the session that produced it."),
        ),
        method="one fresh process per point; current RSS sampled at 20 ms",
        vary_l_fixed_L=vl, vary_L_fixed_l=vL,
    )
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "cost_probe.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nsaved -> qsim/cost_probe.json")
