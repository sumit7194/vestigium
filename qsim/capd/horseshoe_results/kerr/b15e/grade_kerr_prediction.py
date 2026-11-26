"""Grade the SEALED Fable prediction of the Kerr negative control (B15e), mechanically, per BRIEF_FABLE_KERR_PREDICT.md
section 4, with the Bridge's grading rulings recorded in SEALED_KERR_PREDICTION_RECORD.md.

Committed 2026-11-26 BEFORE any registered KERR reading exists, and never to be edited afterwards (the office Bridge's
ruling: the operating session is the prediction's author, so the grading is fixed in code now and run by the personal
Bridge). Written by Claude Opus 5.5 (Quantum-personal). Run with sims/.venv python from qsim/capd/horseshoe/ on the path
(it imports the registered b15d_split.py to read the edge chunks; it changes nothing).

  python grade_kerr_prediction.py --parse-check   verify the sealed sha256 and that it parses (prints counts only)
  python grade_kerr_prediction.py                 grade; needs a "KERR (B15e, final)" or "KERR WITHHELD" line in b15d/run.log

Grading (brief section 4):
  (i)   the edge column: correct calls out of 6 (N1N2 ... N5N1), from each covering's edge chunk (kerr_e/<c>.out);
  (ii)  the final per-covering class: the log score (natural log) of the stated probability of the class that occurred,
        over the coverings actually decided (all 8 rows of the table);
  (iii) the chain class: whether the modal call was correct, and the Brier score of P(RHO>1).
  A covering that never completes (or reads HARNESS-ERROR) is excluded from (i) and (ii) and recorded as such.
Conventions fixed here:
  - edge outcome categories: EDGE-FIXED (b15d_split.edge_fixed = CERTIFIED-FAIL), B1-NOFAIL (complete, valid, b=1,
    certified_fail_b=0, orient_certified_fail=0), B0-UNCERTIFIED (complete, valid, b=0 with no certified failure; matches
    no predicted category), NOT-FINISHED / HARNESS-ERROR (excluded, as section 4 says for a covering that never
    completes; a predicted "not finishing" is therefore never scored).
  - the chain outcome for the modal call: the reading's chain_class; a KERR WITHHELD line, or a reading without
    chain_class, is the category "HARNESS-ERROR or reading withheld". For the Brier score the outcome is 1 iff
    chain_class == "RHO>1".
  - a stated probability of 0 for a class that occurred gives a log score of -inf, reported as such.
  - footnote (the Bridge's ruling): the predictor knew N1N2 and N2N3 had timed out (no outcome); they stay in (i).
"""
import hashlib, json, math, re, subprocess, sys
from pathlib import Path

HS = Path(__file__).resolve().parents[3] / "horseshoe"
sys.path.insert(0, str(HS))
COMMIT = "fd22a7f044728e14365cd5123c3c70e69de3d6ed"
PATH = "qsim/capd/horseshoe_results/kerr/b15e/KERR_PREDICTION_SEALED.md"
SHA = "99e33cd0c5aef82f59a5ece2b9b273c41a1e8a50cdac830e1e5fb9045da4604d"
COVS = ("N0N0", "N0N1", "N1N2", "N2N3", "N3N4", "N4N5", "N5N0", "N5N1")
EDGE6 = COVS[2:]
CLASSES = ("CERTIFIED", "CERTIFIED-FAIL", "UNDECIDED")
CHAIN = ("CERTIFIED-FAIL", "UNDECIDED", "HARNESS-ERROR", "RHO>1")


def sealed():
    raw = subprocess.run(["git", "show", f"{COMMIT}:{PATH}"], capture_output=True, check=True, cwd=HS).stdout
    got = hashlib.sha256(raw).hexdigest()
    if got != SHA: sys.exit(f"REFUSED: sealed file sha256 {got} != registered {SHA}")
    return raw.decode()


def parse_prediction(txt):
    rows = {}
    for m in re.finditer(r"^\| (N\dN\d) \((?:required|optional)\) \| ((?:\\\||[^|])*) \| ((?:\\\||[^|])*) \| ((?:\\\||[^|])*) \|\s*$", txt, re.M):
        c, e, f = m.group(1), m.group(2), m.group(3)
        p = [float(x) for x in re.findall(r"\d+\.\d+", f)]
        edge = ("KNOWN" if "known" in e else "EDGE-FIXED" if "edge-fixed CERTIFIED-FAIL" in e else
                "B1-NOFAIL" if "b = 1" in e else "NOT-FINISHED" if "not finishing" in e else None)
        rows[c] = dict(edge=edge, p=dict(zip(CLASSES, p)) if len(p) == 3 else None)
    ch = txt.split("## 2. Chain class", 1)[1].split("##", 1)[0] if "## 2. Chain class" in txt else ""
    chain, modal = {}, None
    for m in re.finditer(r"^\| ([^|]*) \| (\d+\.\d+) \|\s*$", ch, re.M):
        lab = m.group(1).replace("*", "")
        k = next((c for c in ("CERTIFIED-FAIL", "UNDECIDED", "HARNESS-ERROR", "RHO>1") if c in lab), None)
        if k: chain[k] = float(m.group(2)); modal = k if "(modal call)" in lab else modal
    ok = (set(rows) == set(COVS) and all(r["p"] for r in rows.values()) and all(rows[c]["edge"] not in (None, "KNOWN")
          for c in EDGE6) and set(chain) == set(CHAIN) and modal)
    if not ok: sys.exit("REFUSED: the sealed file does not parse: rows %s, chain %s, modal %s" % (sorted(rows), sorted(chain), modal))
    return rows, chain, modal


def reading():
    import b15d_run as R
    hits = [l for l in R.LOG.read_text().splitlines() if "KERR (B15e, final): " in l or "KERR WITHHELD (B15e" in l]
    if not hits: sys.exit("REFUSED: no registered KERR reading (KERR (B15e, final) / KERR WITHHELD) in b15d/run.log yet")
    l = hits[-1]; withheld = "KERR WITHHELD" in l
    js = l.split("): ", 1)[1] if withheld else l.split("KERR (B15e, final): ", 1)[1]
    if withheld: js = js.rsplit("; to the Bridge", 1)[0]
    return json.loads(js), withheld, l[:19]


def edge_outcome(c):
    import b15d_split as S
    import b15d_run as R
    e = S._read(S.OUT / "kerr_e" / f"{c}.out")
    if not S._complete(e) or not S._cov(e): return "NOT-FINISHED"
    ef = S.edge_fixed(e)
    if ef == "HARNESS-ERROR": return "HARNESS-ERROR"
    if ef == "CERTIFIED-FAIL": return "EDGE-FIXED"
    f = R.fields(S._cov(e)[0])
    return "B1-NOFAIL" if f.get("b") == "1" else "B0-UNCERTIFIED"


def main():
    rows, chain, modal = parse_prediction(sealed())
    if sys.argv[1:] == ["--parse-check"]:
        print("sealed sha256 OK; parses: 8 covering rows, 6 edge calls, 4 chain classes and a modal call (content not printed)"); return
    kt, withheld, when = reading()
    print("# Grading of the sealed Kerr prediction (BRIEF_FABLE_KERR_PREDICT.md section 4; grade_kerr_prediction.py)")
    print(f"- sealed {COMMIT[:7]} sha256 {SHA[:16]}... verified; reading: {'KERR WITHHELD' if withheld else 'KERR (B15e, final)'} at {when}")
    right = n = 0
    print("\n(i) edge column")
    for c in EDGE6:
        a = edge_outcome(c); p = rows[c]["edge"]; fn = " [predictor knew this chunk had timed out (no outcome)]" if c in ("N1N2", "N2N3") else ""
        js = kt["rows"].get(c, {}).get("edge_fixed")
        if (a == "EDGE-FIXED") != (js == "CERTIFIED-FAIL"): fn += f" [NOTE: reading's edge_fixed={js} disagrees with the file as read now]"
        if a in ("HARNESS-ERROR", "NOT-FINISHED"):   # brief section 4: never completes / HARNESS-ERROR -> excluded
            print(f"- {c}: predicted {p}, actual {a} -> excluded{fn}"); continue
        n += 1; right += (a == p)
        print(f"- {c}: predicted {p}, actual {a} -> {'right' if a == p else 'WRONG'}{fn}")
    print(f"(i) {right}/{n} edge calls right (of 6; excluded: {6 - n})")
    print("\n(ii) final per-covering class, log score ln P(actual)")
    tot, k = 0.0, 0
    for c in COVS:
        fin = kt["rows"].get(c, {}).get("final")
        if fin in (None, "HARNESS-ERROR"):
            print(f"- {c}: final {fin or 'not complete'} -> excluded"); continue
        pr = rows[c]["p"].get(fin, 0.0); s = math.log(pr) if pr > 0 else float("-inf"); tot += s; k += 1
        print(f"- {c}: actual {fin}, stated P = {pr} -> {s:.4f}")
    print(f"(ii) total log score {tot:.4f} over {k} decided coverings; mean {tot / k:.4f}" if k else "(ii) no covering decided: not scored")
    cc = kt.get("chain_class"); act = "HARNESS-ERROR" if (withheld or cc is None or cc == "HARNESS-ERROR") else cc
    o = 1.0 if cc == "RHO>1" else 0.0; p = chain["RHO>1"]
    print(f"\n(iii) chain: modal call {modal}, actual {act} (chain_class={cc}) -> {'right' if act == modal else 'WRONG'}")
    print(f"(iii) Brier score of P(RHO>1) = {p}: ({p} - {o:.0f})^2 = {(p - o) ** 2:.6f}")
    print("\nThe grading changes nothing about the registered Kerr reading.")


if __name__ == "__main__":
    main()
