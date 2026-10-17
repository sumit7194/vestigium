"""Phase-2 runner (PREREG_chaos_horseshoe_phase2.md): builds exact-rational specs for hs_cover, runs them, and writes
one JSON per run under qsim/capd/horseshoe_results/ (input sha256, every decision line, timing). Decisions are made
inside hs_cover on MPFR intervals; this script only collects the booleans it prints.

  hs_run.py r1        Rossler control R1: example port, generic re-check, wrong configurations W1-W3
"""
import hashlib, json, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "horseshoe_results"
import os
BIN = Path(os.environ.get("HS_BIN", HERE / "hs_cover"))
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
    bsha = hashlib.sha256(BIN.read_bytes()).hexdigest()          # hashed BEFORE the run
    t0 = time.time()
    p = subprocess.run(["nice", "-n", "19", str(BIN), str(sp)], capture_output=True, text=True, timeout=timeout)
    dt = time.time() - t0
    out = p.stdout.splitlines()
    res = dict(tag=tag, spec=sp.name, spec_sha256=sha, binary=BIN.name, binary_sha256=bsha,
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




# ---------------------------------------------------------------- Henon-Heiles, AZ 2001 sec. 4.2 (exact decimals)
# each t-set: first pair (a1,b1),(a1,b1') gives left (above line 1) / right (below line 2); second pair the strip
AZ = {
    "M0": (("1.819", "0.486"), ("1.819", "0.424"), ("-0.550", "-0.206"), ("-0.550", "-0.069")),
    "M1": (("0.325", "0.223"), ("0.325", "0.143"), ("-3.078", "-0.833"), ("-3.078", "-0.639")),
    "M2": (("0.635", "0.33"), ("0.635", "0.24"), ("-1.576", "0.584"), ("-1.576", "0.659")),
    "M3": (("-0.726", "0.511"), ("-0.726", "0.474"), ("1.376", "-0.129"), ("1.376", "-0.231")),
    "M4": (("1.209", "0.32"), ("1.209", "0.226"), ("-0.827", "0.068"), ("-0.827", "0.03")),
}
AZ_M3_SIDES = (F("0.300"), F("0.290"))          # left adds {p_y >= 0.300}; right is cut to {p_y <= 0.290}
AZ_COVERS = [("M0", "M0"), ("M0", "M1"), ("M1", "M2"), ("M2", "M3"), ("M3", "M4"), ("M4", "M0"), ("M4", "M1")]


def az_frame(lines):
    """(c, U, S) with u = -1 on line 1 (left = above it), u = +1 on line 2, |s| = 1 on the second pair; w = (y, p_y)"""
    (a1, b1), (a1b, b1p), (a2, b2), (a2b, b2p) = [(F(a), F(b)) for a, b in lines]
    assert a1 == a1b and a2 == a2b and a1 != a2 and b1 > b1p and b2 != b2p
    # u = (b1 + b1' - 2 g1)/(b1 - b1'),  s = (2 g2 - b2 - b2')/(b2' - b2),  g_i = p_y - a_i y
    A = ((2 * a1 / (b1 - b1p), -2 / (b1 - b1p)), (-2 * a2 / (b2p - b2), 2 / (b2p - b2)))
    off = ((b1 + b1p) / (b1 - b1p), -(b2 + b2p) / (b2p - b2))       # (u, s) = A w + off
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    Ai = ((A[1][1] / det, -A[0][1] / det), (-A[1][0] / det, A[0][0] / det))
    c = tuple(-(Ai[r][0] * off[0] + Ai[r][1] * off[1]) for r in range(2))
    U, S = (Ai[0][0], Ai[1][0]), (Ai[0][1], Ai[1][1])
    return c, U, S


def corners(c, U, S):
    return [tuple(c[k] + su * U[k] + ss * S[k] for k in range(2)) for su, ss in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def convex_disjoint(P, Q):
    """exact separating-axis test for two convex polygons (vertex lists, Fractions)"""
    for poly in (P, Q):
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            n = (y2 - y1, x1 - x2)
            pa = [n[0] * x + n[1] * y for x, y in P]; pb = [n[0] * x + n[1] * y for x, y in Q]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return True
    return False


def az_checks():
    """exact pre-run checks: frames reproduce the printed lines; S8 (pairwise-disjoint supports, AZ (4.1));
    M3's special sides do not change its edges (so only its TARGET role is special)"""
    fr = {k: az_frame(v) for k, v in AZ.items()}
    for k, (c, U, S) in fr.items():                                  # each corner lies on the printed lines
        (a1, b1), (_, b1p), (a2, b2), (_, b2p) = [(F(a), F(b)) for a, b in AZ[k]]
        for (y, p), (su, ss) in zip(corners(c, U, S), ((-1, -1), (1, -1), (1, 1), (-1, 1))):
            assert p - a1 * y == (b1 if su == -1 else b1p), k
            assert p - a2 * y in (b2, b2p), k
    names = sorted(fr)
    s8 = {f"{a}|{b}": convex_disjoint(corners(*fr[a]), corners(*fr[b])) for i, a in enumerate(names) for b in names[i + 1:]}
    cm = corners(*fr["M3"])
    left_edge_extra_empty = max(p for _, p in cm) < AZ_M3_SIDES[0]     # {p_y >= 0.300} misses |M3|
    right_edge = [pt for pt, (su, _) in zip(cm, ((-1, -1), (1, -1), (1, 1), (-1, 1))) if su == 1]
    right_edge_inside = all(p <= AZ_M3_SIDES[1] for _, p in right_edge)  # u=+1 edge lies in {p_y <= 0.290}
    return fr, dict(S8=s8, S8_all=all(s8.values()), M3_left_edge_standard=left_edge_extra_empty,
                    M3_right_edge_standard=right_edge_inside,
                    M3_max_py=str(max(p for _, p in cm)))


HH_HEAD = ["system hh", "prec 128", "order 20", "iter 1", "param level 1/6"]


def az_tsets(fr, override=None):
    out = []
    for k, (c, U, S) in fr.items():
        if override and k in override:
            c, U, S = override[k]
        line = tset(k, c, U, S)
        if k == "M3":
            line += f" special {q(AZ_M3_SIDES[0])} {q(AZ_M3_SIDES[1])}"
        out.append(line)
    return out


def hh1(nu=16, ns=16, ne=64, prefix="hh1"):
    """HH-PRIMARY (prereg 6.2, B7): AZ 2001 Lemma 5 (5.1) on the published M0-M4, Def. 2 literal, P1; plus the
    wrong configurations W-AZ1 (M2's line pairs exchanged) and W-AZ2 (M2's first pair shrunk to 1e-3)."""
    fr, chk = az_checks()
    (OUT / "hh1_exact_checks.json").write_text(json.dumps(chk, indent=1))
    assert chk["S8_all"] and chk["M3_left_edge_standard"] and chk["M3_right_edge_standard"], chk
    T = az_tsets(fr)
    J = {f"{prefix}_{a}{b}": HH_HEAD + T + [f"cover {a} {b} {nu} {ns} {ne}"] for a, b in AZ_COVERS}
    c, U, S = fr["M2"]
    for tag, ov in (("W_AZ1_swap", (c, S, U)), ("W_AZ2_shrink", (c, (U[0] / 1000, U[1] / 1000), S))):
        TW = az_tsets(fr, override={"M2": ov})
        J[f"{prefix}_{tag}"] = HH_HEAD + TW + [f"cover M1 M2 {nu} {ns} {ne}", f"cover M2 M3 {nu} {ns} {ne}"]
    return batch(J)


def hh1b():
    """B13 re-run of M1=>M2 and M3=>M4 after the reboot: depth-capped bisection, checkpoints, 2 chunks per covering
    (u-pieces [0,8) without edges; [8,16) with edges), leaf cap 2^15 per chunk (2^16 per covering)."""
    fr, chk = az_checks()
    assert chk["S8_all"] and chk["M3_left_edge_standard"] and chk["M3_right_edge_standard"], chk
    T = az_tsets(fr); ck = OUT / "ckpt"; ck.mkdir(exist_ok=True)
    J = {}
    for a, b in (("M1", "M2"), ("M3", "M4")):
        for c, (lo, hi, edges) in enumerate(((0, 8, False), (8, 16, True))):
            body = HH_HEAD + T + ["caps 32768 4096", "depth 16 12", f"arange {lo} {hi}"] + ([] if edges else ["noedges"])
            key = hashlib.sha256(("\n".join(body + [f"cover {a} {b} 16 16 64"]) + "\n").encode()).hexdigest()[:16]
            J[f"hh1b_{a}{b}_c{c}"] = body + [f"checkpoint {ck / f'hh1b_{a}{b}_c{c}_{key}.ckpt'}", f"cover {a} {b} 16 16 64"]
    res = batch(J)
    for a, b in (("M1", "M2"), ("M3", "M4")):
        c0, c1 = res[f"hh1b_{a}{b}_c0"], res[f"hh1b_{a}{b}_c1"]
        get = lambda r, k: re.search(k + r"=(\S+)", r["covers"][0]).group(1) if r["covers"] else None
        merged = dict(covering=f"{a}=>{b}", chunks=[c0["tag"], c1["tag"]],
                      a=(get(c0, "a") == "1" and get(c1, "a") == "1"), b=(get(c1, "b") == "1"),
                      leaves_a=sum(int(get(r, "leaves_a") or 0) for r in (c0, c1)),
                      fail_a=sum(int(get(r, "fail_a") or 0) for r in (c0, c1)), fail_b=int(get(c1, "fail_b") or 0),
                      both_done=c0["done"] and c1["done"])
        merged["COVERS"] = merged["a"] and merged["b"] and merged["both_done"]
        (OUT / f"hh1b_{a}{b}.json").write_text(json.dumps(merged, indent=1))
        print("MERGED", merged)
    return res


if __name__ == "__main__":
    {"r1": r1, "hh1": hh1, "hh1a": lambda: hh1(prefix="hh1a"), "hh1b": hh1b}[sys.argv[1]]()

