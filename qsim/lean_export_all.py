"""Item 2 batch driver (PREREG_lean_certificate_arithmetic.md): every certificate in scope, cheapest first, one guarded
child each (<= 3 threads), committed and pushed per certificate so a reboot loses at most one run.
A certificate whose export file already exists with a passing gate is skipped (resume-safe)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "lean_export")

JOBS = ([("ts2", r, w, 3600) for r in range(6) for w in ("v2", "v1")]
        + [("tschaos", r, w, 3600) for r in range(8) for w in ("v2", "v1")]
        + [("mnaxv2", r, w, 3600) for r in range(4) for w in ("v2", "v1")]
        + [("mneq", r, "v2", 7200) for r in range(6)]
        + [("mneq", r, "v1", 21600) for r in (0, 2, 3)]
        + [("mneq", r, "v1", 43200) for r in (1, 4, 5)])


def done(f, r, w):
    fn = os.path.join(OUT, f"{f}_{r}_{w}.json")
    if not os.path.exists(fn):
        return False
    d = json.load(open(fn))
    return bool(d.get("gate_bit_for_bit") and d.get("certificate_ok") and d.get("readback"))


def main():
    import mr_watchdog as W
    for f, r, w, tl in JOBS:
        if done(f, r, w):
            print(f"skip {f} {r} {w} (already exported)", flush=True)
            continue
        log = os.path.join(OUT, f"{f}_{r}_{w}.log")
        os.makedirs(OUT, exist_ok=True)
        g = W.run_guarded([sys.executable, "-u", os.path.join(HERE, "lean_export.py"), f, str(r), w],
                          mem_limit_mb=3072, time_limit_s=tl, cwd=HERE, log=log)
        status = "EXPORTED" if done(f, r, w) else f"NOT EXPORTED (guard {g['status']})"
        print(f"{f} {r} {w} => {status} [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        paths = [p for p in (os.path.join(OUT, f"{f}_{r}_{w}.json"), log) if os.path.exists(p)]
        subprocess.run(["git", "add", *[os.path.relpath(p, REPO) for p in paths]], cwd=REPO)
        if subprocess.run(["git", "commit", "-q", "-m", f"lean export: {f} row {r} {w}: {status}\n\n"
                           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=REPO).returncode == 0:
            subprocess.run(["git", "push", "-q", "origin", "main"], cwd=REPO)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
