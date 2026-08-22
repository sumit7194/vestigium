import re, subprocess, sys
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout

raw = sh("git","log","-14","--format=COMMIT%x00%H%x00%s%x00%b%x00END")
rows, bad = [], 0
for m in re.finditer(r"COMMIT\x00([0-9a-f]+)\x00(.*?)\x00(.*?)\x00END", raw, re.S):
    sha, subj, body = m.group(1), m.group(2), m.group(3)
    text = subj + "\n" + body
    ids  = set(re.findall(r"\b([a-z_]{6,}\.(?:py|sh|json))\b", text))
    ids |= set(re.findall(r"\b([a-z_]{8,}_[a-z_]{3,})\b", text))
    # only OUR files: identifiers naming another session's artefacts are evidence,
    # not claims about this repo.
    OTHERS = ("bridge_", "_keepalive", "keepalive.sh", "status_read", "peak_probe")
    ids = {i for i in ids if not any(o in i for o in OTHERS)}
    # check against THE TREE AT THAT COMMIT, not HEAD -- an identifier deliberately
    # removed later is not a commit that lied.
    files = set(sh("git","ls-tree","-r","--name-only",sha).split())
    blob = "".join(sh("git","show",f"{sha}:{f}")
                   for f in files if f.endswith((".py",".sh",".md")))
    missing = [i for i in sorted(ids) if i not in files and i not in blob]
    if missing: bad += 1
    rows.append((sha[:8], subj[:56], "ok" if not missing else "MISSING "+",".join(missing[:2])))

print(f"{'commit':10s} {'subject':58s} verdict")
for r in rows: print(f"{r[0]:10s} {r[1]:58s} {r[2]}")

# CONTROLS: the audit must fire on a real absence, and must not fire on a real presence.
sha = rows[0][0]
files = set(sh("git","ls-tree","-r","--name-only",sha).split())
blob = "".join(sh("git","show",f"{sha}:{f}") for f in files if f.endswith((".py",".sh",".md")))
neg = "this_identifier_does_not_exist_anywhere"
pos = "writer_cmd_match"
print()
print(f"  CONTROL absent  ({neg[:28]}...): "
      f"{'MISSING -> audit can fire' if neg not in blob else 'FAIL: inert'}")
print(f"  CONTROL present ({pos}): "
      f"{'found -> audit not trivially failing' if pos in blob else 'FAIL: cannot see real content'}")
sys.exit(1 if bad else 0)
