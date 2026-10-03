"""MN equatorial target under iahub v2 (PREREG_mn_equatorial_v2.md, 28f42f9). One guarded child per row
(2 GB, 6 h: v2 search + v1 replay). Usage: python mr_v2_mneq.py  |  python mr_v2_mneq.py --one i out.json"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROWS = [(p, lev) for p in ("p1", "p2") for lev in ((1, 0, 4), (1, 0, 9), (1, 1, 4))]


def run_row(i):
    import mr_v2 as V
    p, (En, L, mu2) = ROWS[i]
    t0 = time.time()
    S = V.system_equatorial("mn", p, En, L, mu2)
    sing = V.locate(S)
    print(f"[{time.time()-t0:.0f}s] MN {p} eq ({En},{L},{mu2}): {len(sing)} located singular points", flush=True)
    r = V.search(S, sing, log=lambda m: print(f"[{time.time()-t0:.0f}s] {m}", flush=True))
    r["located"] = [str(complex(round(c.real, 6), round(c.imag, 6))) for c in sing]
    print(f"[{time.time()-t0:.0f}s] v2 certificate found: {r['found']} {r.get('why', '')}", flush=True)
    if r["found"]:
        # save the v2 certificate BEFORE the (slow) v1 replay, so a later guard kill cannot lose it
        json.dump(dict(r, assessment="v2 certificate found; v1 replay pending"), open(
            os.path.join(HERE, f"{os.path.basename(__file__)[:-3]}_row{i}_v2cert.json"), "w"), indent=1, default=str)
        r["v1_replay"] = V.replay_v1(S, r, sing)
        print(f"[{time.time()-t0:.0f}s] v1 replay: {r['v1_replay']['replayed']}", flush=True)
        r["assessment"] = "OBSTRUCTION (v2 certificate, v1 replay)" if r["v1_replay"]["replayed"] else \
            "INCONCLUSIVE (v2 certificate, v1 replay FAILED)"
    else:
        r["assessment"] = "INCONCLUSIVE (no certificate)"
    r["seconds"] = round(time.time() - t0, 1)
    return r


def run_all():
    import mr_watchdog as W
    res = []
    for i, (p, lev) in enumerate(ROWS):
        outp = os.path.join(HERE, f"mr_v2_mneq_row{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([sys.executable, "-u", os.path.abspath(__file__), "--one", str(i), outp], mem_limit_mb=2048,
                          time_limit_s=21600, cwd=HERE, log=os.path.join(HERE, f"mr_v2_mneq_row{i}.log"))
        r = json.load(open(outp)) if (g["status"] == "ok" and os.path.exists(outp)) else \
            dict(assessment=f"INCONCLUSIVE (guard: {g['status']})")
        r.update(point=p, level=lev, guard=g)
        res.append(r)
        print(f"{i} MN {p} eq {lev} => {r['assessment']} [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]",
              flush=True)
        json.dump(res, open(os.path.join(HERE, "mr_v2_mneq.json"), "w"), indent=1, default=str)
        os.system(f"cd {os.path.dirname(HERE)} && git add qsim/mr_v2_mneq.json qsim/mr_v2_mneq_row{i}.json "
                  f"qsim/mr_v2_mneq_row{i}.log qsim/mr_v2_mneq.txt 2>/dev/null; git commit -q -m 'MN equatorial v2: row {i} "
                  f"raw output\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>' && git push -q origin main")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        json.dump(run_row(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1, default=str)
    else:
        run_all()
