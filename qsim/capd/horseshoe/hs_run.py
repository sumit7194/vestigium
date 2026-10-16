"""Phase-2 runner (PREREG_chaos_horseshoe_phase2.md): builds exact-rational specs for hs_cover, runs them, and writes
one JSON per run under qsim/capd/horseshoe_results/ (input sha256, every decision line, timing). Decisions are made
inside hs_cover on MPFR intervals; this script only collects the booleans it prints.

  hs_run.py r1        Rossler control R1: example port, generic re-check, wrong configurations W1-W3
"""
import hashlib, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "horseshoe_results"
BIN = HERE / "hs_cover"
CORES = 4                                    # core budget (bridge, 2026-10-16)


def q(x):
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def tset(name, c, U, S):
    """t-set from exact centre and frame; inverse chart computed exactly."""
    c, U, S = [tuple(F(v) for v in t) for t in (c, U, S)]
    det = U[0] * S[1] - S[0] * U[1]
    assert det != 0, name
    A = ((S[1] / det, -S[0] / det), (-U[1] / det, U[0] / det))
    return "tset " + name + " " + " ".join(q(v) for v in (*c, *U, *S, A[0][0], A[0][1], A[1][0], A[1][1]))


def run(tag, lines, timeout=48 * 3600):
    OUT.mkdir(exist_ok=True)
    spec = "\n".join(lines) + "\n"
    sha = hashlib.sha256(spec.encode()).hexdigest()
    sp = OUT / f"{tag}.spec"
    sp.write_text(spec)
    t0 = time.time()
    p = subprocess.run(["nice", "-n", "19", str(BIN), str(sp)], capture_output=True, text=True, timeout=timeout)
    dt = time.time() - t0
    out = p.stdout.splitlines()
    res = dict(tag=tag, spec=sp.name, spec_sha256=sha, binary_sha256=hashlib.sha256(BIN.read_bytes()).hexdigest(),
               returncode=p.returncode, seconds=round(dt, 2), stderr_tail=p.stderr.splitlines()[-5:],
               ex=[l for l in out if l.startswith("EX ")], covers=[l for l in out if l.startswith("COVER ")],
               failpieces=[l for l in out if l.startswith("FAILPIECE")][:200],
               n_failpieces=sum(l.startswith("FAILPIECE") for l in out),
               fatal=[l for l in out if l.startswith("FATAL")], done=("DONE" in out))
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, "rc", p.returncode, f"{dt:.1f}s", "done", res["done"])
    for l in res["ex"] + res["covers"] + res["fatal"]:
        print("  ", l)
    return res


# ---------------------------------------------------------------- Rossler (CAPD example, exact decimals)
R_HEAD = ["system rossler", "prec 128", "order 20", "iter 2", "param a 57/10", "param b 1/5"]
Zb, Zt = F(28, 1000), F(34, 1000)
lM, rM, lN, rN = F(-84, 10), F(-76, 10), F(-57, 10), F(-46, 10)
gl, gr = F(-107, 10), F(-23, 10)
zc, zr = (Zb + Zt) / 2, (Zt - Zb) / 2


def rossler_sets(M=None, N=None):
    M = M or (((lM + rM) / 2, zc), ((rM - lM) / 2, 0), (0, zr))
    N = N or (((lN + rN) / 2, zc), ((rN - lN) / 2, 0), (0, zr))
    return [tset("M", *M), tset("N", *N)]


COV4 = [("M", "M"), ("M", "N"), ("N", "M"), ("N", "N")]


def batch(jobs):
    """run {tag: lines} concurrently on at most CORES cores; results in tag order"""
    with ThreadPoolExecutor(CORES) as ex:
        fut = {k: ex.submit(run, k, v) for k, v in jobs.items()}
        return {k: f.result() for k, f in fut.items()}


def r1():
    J = {}
    # (1) exact port of RosslerChaoticDynamics.cpp: same sets, section, order, subdivisions; MPFR. Split into
    #     independent specs only for parallelism (each check is a separate computation in the example too).
    J["r1_ex_trap"] = R_HEAD + [f"ex_trap {q(gl)} {q(gr)} {q(Zb)} {q(Zt)} 200"]
    J["r1_ex_edges"] = R_HEAD + [
        f"ex_edge leftM {q(lM)} {q(Zb)} {q(Zt)} less {q(lM)}",
        f"ex_edge rightM {q(rM)} {q(Zb)} {q(Zt)} greater {q(rN)}",
        f"ex_edge leftN {q(lN)} {q(Zb)} {q(Zt)} greater {q(rN)}",
        f"ex_edge rightN {q(rN)} {q(Zb)} {q(Zt)} less {q(lM)}"]
    J["r1_ex_coneM"] = R_HEAD + [f"ex_cone {q(lM)} {q(rM)} {q(Zb)} {q(Zt)} 80 -100"]
    J["r1_ex_coneN"] = R_HEAD + [f"ex_cone {q(lN)} {q(rN)} {q(Zb)} {q(Zt)} 40 -100"]
    # (2) the same sets through the generic Def. 2 code (frames given, not constructed), one spec per covering
    for s_, t_ in COV4:
        J[f"r1_generic_{s_}{t_}"] = R_HEAD + rossler_sets() + [f"cover {s_} {t_} 64 1 1"]
    # (3) wrong configurations (prereg 6.4): each must be REJECTED (at least one of the four coverings fails)
    Mc = ((lM + rM) / 2, zc); Mu = ((rM - lM) / 2, 0); Ms = (0, zr)
    W = {
        "W1_swap": (Mc, Ms, Mu),                                         # u and s exchanged
        "W2_rot90": (Mc, (-Mu[1], Mu[0]), (-Ms[1], Ms[0])),              # both frame vectors rotated by 90 degrees
        "W3_shrink": (Mc, (Mu[0] / 1000, 0), Ms),                        # unstable half-width x 1e-3
    }
    for k, v in W.items():
        J[f"r1_{k}"] = R_HEAD + rossler_sets(M=v) + [f"cover {s_} {t_} 64 1 1" for s_, t_ in COV4]
    return batch(J)


if __name__ == "__main__":
    {"r1": r1}[sys.argv[1]]()
