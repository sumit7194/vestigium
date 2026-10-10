"""Plan A validation V1 (2abb00d): the full Stage-2-range quadrature (same grid, same q cut t + 7.5, Stage-2 method
parameters) run with stepper v2. Checkpointed per node, restart-safe. Gate: a(90) vs Stage 1 <= 1e-9; a(40), a(45)
inside the tight D1 interval; c2 as before."""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chl_run_controls as R, chl_run_sub45 as S2
CKPT = os.path.join(HERE, "chl_planA_V1_nodes.jsonl")
OUT = os.path.join(HERE, "chl_planA_V1_run.json")

def _init():
    sys.path.insert(0, HERE)

def _work(tq):
    import chl_node as nd, chl_run_sub45 as S
    t, q = tq
    try:
        r = nd.compute_node(t, q, S.XS, stepper="v2"); r["ok"] = True
    except Exception as e:
        r = dict(t=t, q=q, ok=False, error=f"{type(e).__name__}: {e}")
    return r

def load_done():
    done = {}
    if os.path.exists(CKPT):
        for line in open(CKPT):
            r = json.loads(line); done[R.key(r["t"], r["q"])] = r
    return done

def main(workers=2):
    from multiprocessing import Pool
    done = load_done()
    todo = []
    for res in R.RESOLUTIONS:
        for t, _, q, _ in R.nodes(res):
            if R.key(t, q) not in done and (t, q) not in todo:
                todo.append((t, q))
    print(f"{len(done)} done, {len(todo)} to run", flush=True)
    t0 = time.time()
    if todo:
        with Pool(workers, initializer=_init) as pool, open(CKPT, "a") as fh:
            for i, r in enumerate(pool.imap_unordered(_work, todo), 1):
                fh.write(json.dumps(r) + "\n"); fh.flush()
                if i % 50 == 0 or not r["ok"]:
                    print(f"  {i}/{len(todo)} ({time.time()-t0:.0f}s)" + ("" if r["ok"] else f" FAILED {r['error'][:80]}"), flush=True)
    done = load_done()
    summary = dict(stage="plan A V1 (stepper v2)", xs=S2.XS, resolutions={})
    for res in R.RESOLUTIONS:
        acc, tail, missing = S2.integrate(res, done)
        summary["resolutions"][res] = dict(values=acc, t_tail_bound=tail, missing=missing)
    json.dump(summary, open(OUT, "w"), indent=1)
    print("V1 RUN DONE", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
