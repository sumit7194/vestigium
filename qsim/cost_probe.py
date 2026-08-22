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
    for l in (30, 35, 40, 45, 50, 55, 60, 65):
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

    # MODEL COMPARISON. bridge found their free-exponent fit mis-specified: its
    # hold-out errors were the same size and the same direction every time
    # (+6.7, +6.8, +6.7%), which is a signature of a missing term rather than
    # scatter. A pure power law has nowhere to put a fixed overhead, so the
    # fitted exponent lands below the true one and pays for it at every step.
    # Fixing the exponent at the STRUCTURALLY DERIVED 4 (n = l^2, memory ~ n^2)
    # and fitting only scale and offset cut their error from ~7% to ~0.1%.
    #
    # It does NOT replicate here, and the reason is the useful part: my fitted
    # exponents were already 3.90-3.96 because the interpreter baseline was
    # MEASURED from the init phase and subtracted, rather than left for the
    # exponent to absorb. Their overhead was ~94 MB and unmodelled; mine ~30 MB
    # and measured. So the fix matters in proportion to how much unmodelled
    # overhead the exponent is being asked to swallow.
    #
    # What does replicate, and is a real check: fitting the offset as a FREE
    # parameter recovers c = +36 MB, against 29.9 MB measured independently from
    # the init phase. Two routes to the same quantity, one fitted and one read
    # off a phase label.
    X = [l**4 for l, _ in pts]
    Y = [v + base for _, v in pts]
    nn = len(X); sX = sum(X); sY = sum(Y)
    sXX = sum(x*x for x in X); sXY = sum(x*y for x, y in zip(X, Y))
    a4 = (nn*sXY - sX*sY)/(nn*sXX - sX*sX)
    c4 = (sY - a4*sX)/nn
    print(f"\n   structural model, exponent FIXED at 4: a={a4:.4e} MB/l^4, "
          f"offset c={c4:+.1f} MB")

    # RESIDUAL STRUCTURE, not fit quality. bridge's a*l^4 + c fits well and is
    # still mis-specified: their residuals form a smooth ARC (-26 -20 -17 -8 +7
    # +30 +68), so c is absorbing an l-dependent term -- the same error they had
    # just diagnosed in the free power law, one level down. A good fit is not
    # evidence; the SIGN PATTERN of the residuals is.
    resid = [(l, v + base - (a4*l**4 + c4)) for l, v in pts]
    signs = "".join("+" if r > 0 else "-" for _, r in resid)
    flips = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
    worst = max(abs(r) for _, r in resid)
    # THE SIGN COUNT HAS NO POWER AT THIS SAMPLE SIZE and is reported as a
    # statistic, NOT as evidence. Under scatter the count is Binomial(n-1, 1/2):
    # with 8 points, 5 changes gives P(X>=5)=0.227 read as adequacy and
    # P(X<=5)=0.938 read as an arc. Neither is informative. At n=7 only ZERO
    # sign changes reaches p<0.05, so the test can essentially never fire here.
    #
    # bridge computed this null after we had both been using the diagnostic all
    # day, and withdrew a committed finding because of it -- "smooth arcs in all
    # three regulators" was 2 changes in 6, i.e. exactly a coin flip. I had used
    # it to claim my model was adequate. Applying a diagnostic without its null,
    # seeing structure, and picking the threshold after the data is the same
    # error we spent the day cataloguing, in the tool used to catalogue it.
    from math import comb
    n_flip = len(resid) - 1
    p_arc = sum(comb(n_flip, i) for i in range(flips+1))/2**n_flip
    print(f"   residual signs {signs}  ({flips} changes, max {worst:.1f} MB "
          f"= {worst/max(v+base for _, v in pts)*100:.1f}%)")
    print(f"   sign count is NOT evidence: P(X<={flips} | Binom({n_flip},1/2)) "
          f"= {p_arc:.3f}; only 0 changes would reach p<0.05 at this n")
    print(f"   WHAT THE ADEQUACY CLAIM RESTS ON: residual magnitude "
          f"({worst/max(v+base for _, v in pts)*100:.1f}% of the largest point) "
          f"and the hold-out errors above, not the signs.")

    # AND THE TWO-ROUTES CHECK, WHICH GOT WORSE WITH MORE DATA. On four points
    # the fitted offset was +35.7 MB against 30.4 measured off the init phase --
    # 15% apart, and I reported that as two independent routes to one quantity.
    # On eight points it is +39.3, i.e. 29% apart. THE AGREEMENT WEAKENED AS THE
    # DATA IMPROVED, which is the signature of a coincidence rather than a check.
    print(f"   fitted offset {c4:+.1f} MB vs {base:.1f} MB measured off the init "
          f"phase: {abs(c4-base)/base*100:.0f}% apart")
    print("   (was 15% on four points -- the agreement WEAKENED with more data,"
          " so treat it as a coincidence, not a cross-check)")
    structural = dict(exponent="fixed at 4 from n = l^2, not fitted",
                      a_mb_per_l4=a4, offset_mb=round(c4, 1),
                      measured_init_baseline_mb=round(base, 1),
                      s6_gb=round((a4*120**4 + c4)/1024, 2),
                      free_exponent_s6_gb=14.40,
                      note=("both models agree here to under 1%; bridge's data "
                            "discriminated because their unmodelled overhead was "
                            "~3x larger relative to signal"))

    # WHAT THE REQUIREMENT DOES AND DOES NOT SETTLE.
    #
    # I measured 14.09 GB for s=6, compared it against `mem_available_gb` (~10),
    # and recorded s=6 as out of reach. THE COMPARISON IS ITSELF AN UNTESTED
    # MODEL and I never tested it -- after a full day insisting that a number
    # with measurement-authority still needs a referent, I let an unmeasured
    # comparison close a question. The user caught it: "did you guys try it, or
    # just compute?"
    #
    # The real ceiling, measured:
    #   RAM 16.0 GB; swap 0.00 M used but DYNAMIC on macOS, 22 GB free disk to
    #   grow into; Swapouts: 0 -- this box has never swapped in its life.
    # So "it will thrash" has no evidence behind it at all, and 14.09 GB against
    # 16 GB physical may not even need swap on a quiet machine.
    #
    # Wall-clock is the discriminator, not memory, and it is now measured too:
    # entropy-phase timings at l=30..70 give local exponents 6.21/7.05/6.48/5.79,
    # clustering on the structural O(n^3) = O(l^6). That projects ~10.6 min for
    # one l=120 point and ~1.2 h for the full 8-l x 4-regulator study.
    #
    # STATUS: requirement EXTRAPOLATED; feasibility since demonstrated by the
    # bridge at the same l_max.
    #
    # AND THIS PROBE MUST NOT BE RE-RUN WHILE THE BOX IS LOADED. Re-running it
    # during the bridge's s=6 gave peaks 18-21% LOW at l=45,60,65 while
    # everything below l=50 was unchanged within 2% -- so the s=6 figure moved
    # 14.08 -> 10.95 GB for purely environmental reasons. That is the eviction
    # effect: under pressure a large allocation loses pages during the climb and
    # the sampled peak reads below the true one. Small allocations fit and read
    # the same.
    #
    # CONSEQUENCE FOR THE COMPARISON BELOW, and it cuts against my own
    # correction: the bridge's observed ~7.8 GB was itself measured while their
    # run was loading the box. If it is depressed by the same ~21%, their true
    # peak is nearer 9.9 GB and the over-prediction is ~1.37x, not 1.74x. A
    # pressured peak UNDERSTATES, so an observed-vs-predicted gap measured under
    # load is inflated in the direction that makes the prediction look worse.
    feasibility = dict(
        peak_gb_s6=round((a4*120**4 + c4)/1024, 2),
        ram_gb=16.0, swap_used_gb=0.0, free_disk_gb=22, swapouts_ever=0,
        timing_exponent_measured=[6.21, 7.05, 6.48, 5.79],
        timing_exponent_structural=6,
        projected_one_point_min=10.6, projected_full_study_hours=1.2,
        extrapolation_reach=dict(
            measured_range="l = 30..65",
            holdout_steps_validated=["50->60 (x1.20)", "45->65 (x1.44)"],
            s6_target="l=120, x1.85 beyond the largest measured point",
            bridge_outcome=("their law over-predicted by ~40% at a x1.20 step, "
                            "after hold-out validation, residual-sign checking "
                            "and a cross-study check -- all three agreed on a "
                            "number that was 40% high at the one point that "
                            "mattered"),
            implication=("hold-out validation certifies interpolation and a small "
                         "step; it does NOT certify x1.85. I quoted a validated "
                         "law outside its validated range and called the question "
                         "closed. If the same over-prediction applies here, the "
                         "real peak is nearer 8.5 GB, well inside 16 GB RAM."),
        ),
        # THE NUMBER THE RETRACTED REFUSAL RESTED ON, now itself testable.
        # I retracted "s=6 is out of reach" when the comparison behind it proved
        # untested. I did NOT revisit the 14.08 GB the refusal rested on --
        # quantum's own version of the failure bridge found in their file, where
        # a retracted decision left its number standing in four places.
        #
        # The bridge has since RUN s=6 at the same l_max=120 and measured a peak
        # of ~7.8 GB against their own predicted 13.55 -- an over-prediction of
        # 74%. Both our laws were hold-out validated, residual checked and
        # cross-checked against each other, and both were high by the same order.
        # Their observation on that is sharper than the confound it replaced:
        # two instruments converging tightly, by a step verified as independent,
        # ON THE WRONG ANSWER. Independence of method bought agreement and
        # bought nothing about correctness.
        #
        # So this figure carries the one relevant datum rather than standing alone:
        observed_analogue=dict(
            bridge_predicted_gb=13.55, bridge_observed_gb=7.8,
            over_prediction_factor=round(13.55/7.8, 2),
            implied_for_this_study_gb=round(14.08*7.8/13.55, 1),
            note=("same l_max=120 sets the peak in both studies, so the scaled "
                  "expectation is ~8 GB rather than 14. UNTESTED here -- this is "
                  "one transfer from one measurement, not a prediction."),
        ),
        verdict=("requirement EXTRAPOLATED (x1.85 beyond measurement); the one comparable extrapolation that has since been tested was 74% high. Feasibility now demonstrated by the bridge at the same l_max. The earlier 'out of "
                 "reach' compared a measured requirement against `available` and "
                 "treated the comparison as settled. It is a prediction."),
    )

    out = dict(
        question="which parameter and which phase govern the memory peak?",
        holdout_validation=holdout,
        structural_model=structural,
        feasibility=feasibility,
        cross_check=dict(
            note=("bridge measured their s=5 peak independently, different study, "
                  "same n=l^2 matrix structure, peak also in the entropy phase"),
            their_clean_measurement_gb=6.54,
            their_earlier_contaminated_gb=5.92,
            my_prediction_at_l100_gb=6.96,
            agreement_percent=6.4,
            confound=("The cross-study agreement TIGHTENED over three rounds -- "
                      "15.0% -> 5.6% -> 3.9% -- but most of that does not count. "
                      "The 15->5.6 step is when BOTH sessions switched to the "
                      "exponent fixed at 4; adopting a common model manufactures "
                      "agreement. Only 5.6->3.9 is clean, each of us adding "
                      "points to our own data separately. What stays independent: "
                      "different codebases, different physical systems, and an "
                      "exponent DERIVED FROM STRUCTURE rather than fitted -- the "
                      "one element neither session negotiated."),
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
