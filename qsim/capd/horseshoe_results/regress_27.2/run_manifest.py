"""Manifest-driven regression runner (the Bridge's mechanism request, 2026-11-17): every check's command, output, exact
reference file and comparison rule come from manifest.tsv; nothing is hard-coded. Refuses to start if a repository
reference is missing; stops at the FIRST difference. Usage: run_manifest.py <manifest.tsv> <scratch out dir> [start id]"""
import os, subprocess, sys, time
Q = "/Users/sumit/Github/quantum"; HS = Q + "/qsim/capd/horseshoe"; D = Q + "/qsim/capd/horseshoe_results/regress_27.2"
S = sys.argv[2]; S2 = os.path.join(os.path.dirname(S), "r2")
P = dict(Q=Q, T=HS + "/tests", HS=HS, R=Q + "/qsim/capd/horseshoe_results", D=D, S=S, S2=S2, BIN=S + "/bin", PY=Q + "/sims/.venv/bin/python")
fill = lambda s: s.format(**P)
OUT = open(D + "/RESULT.txt", "a")
def say(m):
    m = time.strftime("%H:%M:%S ") + m; print(m, flush=True); OUT.write(m + "\n"); OUT.flush()
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
if len(sys.argv) > 3: rows = rows[[r[0] for r in rows].index(sys.argv[3]):]          # resume from a check id (earlier ones passed)
assert all(len(r) == 5 for r in rows), [r for r in rows if len(r) != 5]
os.makedirs(P["BIN"], exist_ok=True)
if os.listdir(S) != ["bin"] and os.listdir(S): sys.exit("output dir not fresh: %s" % S)
missing = []
for i, cmd, out, ref, rule in rows:
    if rule in ("byte", "num40", "steps"):
        r = fill(ref)
        if not (r.startswith(S) or r.startswith(S2)) and not os.path.exists(r): missing.append((i, r))
    if rule == "gitclean":
        missing += [(i, p) for p in ref.split() if not os.path.exists(os.path.join(Q, p))]
if missing: sys.exit("REFUSED: reference files missing: %s" % missing)
say("== PART 3 (manifest %s, %d checks; continue from the section toy)" % (os.path.basename(sys.argv[1]), len(rows)))
for i, cmd, out, ref, rule in rows:
    out = fill(out); c = fill(cmd)
    rc = subprocess.run(c, shell=True, executable="/bin/zsh").returncode
    if rc != 0: say("%s: command failed (exit %d) -- stopping" % (i, rc)); sys.exit(1)
    if rule == "exit0": say("%s: OK" % i); continue
    if rule == "gitclean":
        ok = subprocess.run(["git", "-C", Q, "diff", "--quiet", "--"] + ref.split()).returncode == 0
        res = "IDENTICAL (regenerated, git diff empty)" if ok else "DIFFERS"
    elif rule == "selfreport":
        last = open(out).read().strip().splitlines()[-1]; ok = last.startswith(ref); res = last
    else:
        r = fill(ref)
        if not os.path.exists(r): say("%s: REFUSED, reference missing: %s -- stopping" % (i, r)); sys.exit(1)
        if rule == "byte":
            ok = open(out, "rb").read() == open(r, "rb").read(); res = "IDENTICAL (byte)" if ok else "DIFFERS (byte)"
        elif rule == "num40":
            res = subprocess.run([P["PY"], D + "/numcmp.py", out, r], capture_output=True, text=True).stdout.strip(); ok = not res.startswith("DIFFERS")
        elif rule == "steps":
            res = subprocess.run([P["PY"], D + "/stepcmp.py", out, r], capture_output=True, text=True).stdout.strip(); ok = res.startswith("IDENTICAL")
    say("%s vs %s [%s]: %s" % (i, os.path.basename(fill(ref).split()[0]) if rule != "selfreport" else "-", rule, res))
    if not ok: say("DIFFERS at %s -- stopping here (the Bridge's rule)" % i); sys.exit(1)
say("== PART 3 COMPLETE: every check IDENTICAL / AGREE (w 0.001 section toy: no matching reference, not compared)")
