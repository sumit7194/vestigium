"""Plan A validation V2 + V3 (PREREG_cuspis_sub45_check.md, PLAN A, 2abb00d). Checkpointed per job; detached run.
V2: 30 Stage-2 nodes -- frozen v1 DENSE vs recorded sparse (<= 1e-8); v2 sparse vs v2 dense (<= 1e-10).
V3: 3a-failed nodes with v2 on the SPARSE Stage-2 list, sets B and C (<= 1e-8) + smooth decay."""
import json, math, os, random, sys, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chl_run_controls as R, chl_run_sub45 as S2
SPARSE = S2.XS
DENSE = sorted(set([math.radians(d) for d in range(15, 180, 2)] + list(SPARSE)), reverse=True)
SETS = {"S2": dict(N=26, eps0="0.15", taylor_N=30, dplus=0), "B": dict(N=54, eps0="0.05", taylor_N=60, dplus=15),
        "C": dict(N=72, eps0="0.035", taylor_N=80, dplus=30)}
CK = os.path.join(HERE, "chl_planA_V23_nodes.jsonl")

def jobs():
    done = S2.load_done()
    grid = R.nodes("fine")
    W = {(t, q): wt*wq*q*q/math.cosh(math.pi*t)**2 for t, wt, q, wq in grid}
    x15 = math.radians(15.0)
    pick = lambda r: [v[0] for k, v in r["trG"].items() if abs(float(k) - x15) < 1e-9][0]
    heavy = sorted(W, key=lambda k: -abs(W[k]*pick(done[R.key(*k)])))[:10]
    highM = sorted(W, key=lambda k: -done[R.key(*k)]["M"])[:10]
    rnd = random.Random(7).sample(sorted(W), 10)
    v2nodes = list(dict.fromkeys(heavy + highM + rnd))
    J = []
    for t, q in v2nodes:
        J += [("V2", t, q, "S2", "v1", "dense"), ("V2", t, q, "S2", "v2", "sparse"), ("V2", t, q, "S2", "v2", "dense")]
    for t, q in ((0.3, 22.8), (0.3, 31.8), (1.37, 23.9), (1.37, 32.9)):
        for s in ("B", "C"):
            J.append(("V3", t, q, s, "v2", "sparse"))
    return J

def work(j):
    import chl_node as nd
    tag, t, q, s, stepper, grid = j
    p = SETS[s]; M = math.sqrt(0.25 + q*q); t0 = time.time()
    xs = SPARSE if grid == "sparse" else DENSE
    try:
        r = nd.compute_node(t, q, xs, N=p["N"], eps0=p["eps0"], taylor_N=p["taylor_N"], dps=int(30 + 3*M) + p["dplus"],
                            stepper=stepper)
        r["ok"] = True
        r["trG"] = {k: v for k, v in r["trG"].items() if any(abs(float(k) - x) < 1e-9 for x in SPARSE)}
    except Exception as e:
        r = dict(ok=False, error=f"{type(e).__name__}: {e}"[:300])
    r.update(tag=tag, t=t, q=q, set=s, stepper=stepper, grid=grid, seconds=round(time.time() - t0, 1))
    return r

if __name__ == "__main__":
    J = jobs()
    done = set()
    if os.path.exists(CK):
        for line in open(CK):
            r = json.loads(line); done.add((r["tag"], round(r["t"], 9), round(r["q"], 9), r["set"], r["stepper"], r["grid"]))
    todo = [j for j in J if (j[0], round(j[1], 9), round(j[2], 9), j[3], j[4], j[5]) not in done]
    print(len(J), "jobs,", len(todo), "to run", flush=True)
    with Pool(2) as pool, open(CK, "a") as fh:
        for r in pool.imap_unordered(work, todo):
            fh.write(json.dumps(r) + "\n"); fh.flush()
            print(f"{r['tag']} t={r['t']:.3f} q={r['q']:.3f} {r['set']} {r['stepper']} {r['grid']} ok={r['ok']} [{r['seconds']}s]", flush=True)
    print("V23 DONE", flush=True)
