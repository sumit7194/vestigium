"""A7 (PREREG_mn_equatorial_v2.md): (1) v1 G0 at N=140; (2) v1 re-replay of a SAVED v2 certificate at a given N.

The replay rebuilds S and the singular-point list exactly as the row run did (`locate_a6`, deterministic) and checks
that the rounded list matches the one stored with the certificate, so the replay is the row run's replay, unchanged
except for N.

Usage:  python mr_v2_a7.py G0
        python mr_v2_a7.py REPLAY <row> <N> <procs> <out.json>
        python mr_v2_a7.py FINISH140 <row> <procs>   (N=100 already ran in the row run and failed: N=140 only)
        python mr_v2_a7.py FINISH <row>      (guarded N=100 replay; if it fails without an error, N=140 per A7 term 4;
                                              writes mr_v2_mneq_row<row>_a6.json and appends to the A6 summary)
"""
import functools, glob, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ia_hub as IA
PY = sys.executable
REPO = os.path.dirname(HERE)


def g0_140():
    import mr_mn_axis as MA
    orig = IA.transport
    IA.transport = functools.partial(orig, N=140)        # the G0 tests, unchanged, at N = 140
    try:
        return MA.g0()
    finally:
        IA.transport = orig


def replay_saved(i, N, procs):
    import mr_v2 as V, mr_v2_mneq as M
    d = json.load(open(os.path.join(HERE, f"mr_v2_mneq_row{i}_a6_v2cert.json")))
    p, (En, L, mu2) = M.ROWS[i]
    S = V.system_equatorial("mn", p, En, L, mu2)
    sing = V.locate_a6(S)
    loc = [str(complex(round(c.real, 6), round(c.imag, 6))) for c in sing]
    assert loc == d["located"], "locator output differs from the certificate's run"
    t0 = time.time()
    r = V.replay_v1(S, d, sing, procs=procs, N=N)
    r["seconds"] = round(time.time() - t0, 1)
    return r


def _commit(paths, msg):
    subprocess.run(["git", "add", *[os.path.relpath(p, REPO) for p in paths if os.path.exists(p)]], cwd=REPO)
    if subprocess.run(["git", "commit", "-q", "-m", msg + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"],
                      cwd=REPO).returncode == 0:
        subprocess.run(["git", "push", "-q", "origin", "main"], cwd=REPO)


def finish(i, only140=False, procs140=3):
    import mr_watchdog as W, mr_v2_mneq as M
    cert = json.load(open(os.path.join(HERE, f"mr_v2_mneq_row{i}_a6_v2cert.json")))
    runs = {}
    if only140:      # the N = 100 replay already ran inside the row run: take its logged result, do not repeat it
        prev = json.load(open(os.path.join(HERE, f"mr_v2_mneq_row{i}_a6.json")))
        assert prev["v1_replay"]["replayed"] is False and prev["v1_replay"].get("N", 100) == 100
        runs[100] = prev["v1_replay"]
    for N, procs, tl in ((100, 3, 21600), (140, procs140, 43200)):
        if N in runs:
            continue
        outp = os.path.join(HERE, f"mr_v2_a7_row{i}_N{N}.json")
        g = W.run_guarded([PY, "-u", os.path.abspath(__file__), "REPLAY", str(i), str(N), str(procs), outp],
                          mem_limit_mb=3072, time_limit_s=tl, cwd=HERE, log=os.path.join(HERE, f"mr_v2_a7_row{i}_N{N}.log"))
        r = json.load(open(outp)) if (g["status"] == "ok" and os.path.exists(outp)) else dict(replayed=None, error=g["status"])
        r["guard"] = g
        runs[N] = r
        print(f"row {i} v1 replay N={N}: {r.get('replayed')} [guard {g['status']}, {g['seconds']} s]", flush=True)
        if r.get("replayed") is not False:          # success, or an error (not the tail-limited failure): stop here
            break
    final = runs[max(runs)]
    res = dict(cert, v1_replay=final, v1_replay_by_N={str(k): v for k, v in runs.items()})
    res["assessment"] = ("OBSTRUCTION (v2 certificate, v1 replay)" if final.get("replayed") else
                         "INCONCLUSIVE (v2 certificate, v1 replay FAILED)" if final.get("replayed") is False else
                         f"INCONCLUSIVE (v2 certificate, v1 replay error: {final.get('error')})")
    res.update(point=M.ROWS[i][0], level=M.ROWS[i][1], amendment="A6 post-failure; v1 replay resumed from the saved "
               "certificate after the 2026-10-04 reboot" + ("; A7 term 4 (N=140)" if 140 in runs else ""))
    outp = os.path.join(HERE, f"mr_v2_mneq_row{i}_a6.json")
    json.dump(res, open(outp, "w"), indent=1, default=str)
    M.append_a6_summary(i, res)
    print(f"{i} [A6] MN {M.ROWS[i][0]} eq {M.ROWS[i][1]} => {res['assessment']} [v1 N={max(runs)}]", flush=True)
    _commit([outp, os.path.join(HERE, "mr_v2_mneq_a6.json"), os.path.join(HERE, "mr_v2_mneq_a6.txt"),
             *glob.glob(os.path.join(HERE, f"mr_v2_a7_row{i}_N*"))],
            f"MN equatorial v2 A6 row {i}: v1 replay from the saved certificate, raw output")


if __name__ == "__main__":
    if sys.argv[1] == "G0":
        r = g0_140(); json.dump(r, open(os.path.join(HERE, "mr_v2_a7_G0.json"), "w"), indent=1, default=str)
        print(json.dumps(r, indent=1, default=str))
    elif sys.argv[1] == "REPLAY":
        i, N, procs, outp = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        r = replay_saved(i, N, procs); json.dump(r, open(outp, "w"), indent=1, default=str)
        print(f"A7 v1 replay row {i} at N={N}:", r["replayed"], flush=True)
        print(json.dumps({k: v for k, v in r.items() if "midrad" in k}, indent=1), flush=True)
    elif sys.argv[1] == "FINISH":
        finish(int(sys.argv[2]))
    elif sys.argv[1] == "FINISH140":                       # python mr_v2_a7.py FINISH140 <row> <procs>
        finish(int(sys.argv[2]), only140=True, procs140=int(sys.argv[3]))
