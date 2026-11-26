"""Grade the SEALED Fable prediction of the branch-S retry, mechanically, per BRIEF_FABLE_PREDICT.md section 4.

Committed 2026-11-26 BEFORE any retry result exists, and never to be edited afterwards (the office Bridge's ruling: the
operating session is the prediction's author, so the grading is fixed in code now and run by the personal Bridge).
Written by Claude Opus 5.5 (Quantum-personal).

  python grade_prediction.py --parse-check         verify the sealed file's sha256 and that it parses (prints counts only)
  python grade_prediction.py <read_retry output>   grade; <read_retry output> = the saved stdout of read_retry.sh

Inputs:
  - the sealed file, read from git (commit d31ac7f), sha256 checked first; the script refuses on any mismatch;
  - the saved output of the registered reader read_retry.sh (unchanged), which must contain its VERDICT line.
Grading (brief section 4, verbatim in effect):
  (i)   fraction of the 32 cells whose actual u2 ratio lies inside the predicted 80% interval, and the same for u1;
  (ii)  whether each piece's PASS/FAIL call was right (4 calls);
  (iii) whether the overall verdict was right;
  (iv)  the Brier score of the stated PASS probability.
  A piece that THREW, or a checkpoint not reached, counts as FAIL for (ii) and (iii) and is excluded from (i).
Conventions fixed here: the actual ratio is the PRINTED value on the CHECKPOINT line (2 decimals), as the prediction's own
units state; intervals are inclusive. An INVALID verdict (a control failed) is not covered by section 4: (iii) and (iv)
are then reported as "not scored (INVALID)", and (i)/(ii) are still computed from what was read.
"""
import hashlib, re, subprocess, sys
from pathlib import Path

COMMIT = "d31ac7f72099ee8be38a607cea5dd953a5031bca"
PATH = "qsim/capd/horseshoe_results/so_mn/erep/retry_s/PREDICTION_SEALED.md"
SHA = "0a6d7f99cd90d736de858083028c1da2f91bcfa926b9feccac5933648547c70c"
PIECES = ("mm", "mp", "pm", "pp")
TIMES = ("283.8852", "290.8497", "291.8852", "295.8852", "793.2346", "800.0941", "801.2346", "805.2346")


def sealed():
    raw = subprocess.run(["git", "show", f"{COMMIT}:{PATH}"], capture_output=True, check=True, cwd=Path(__file__).resolve().parent).stdout
    got = hashlib.sha256(raw).hexdigest()
    if got != SHA: sys.exit(f"REFUSED: sealed file sha256 {got} != registered {SHA}")
    return raw.decode()


def parse_prediction(txt):
    cell = re.compile(r"^\| (mm|mp|pm|pp) \| (\d+\.\d+) \| ([\d.]+)[^|]*\| \[([\d.]+), ([\d.]+)\] \| ([\d.]+) \| "
                      r"\[([\d.]+), ([\d.]+)\] \| (PASS|FAIL) \|\s*$", re.M)
    cells = {}
    for m in cell.finditer(txt):
        p, t = m.group(1), m.group(2)
        cells[(p, t)] = dict(u2=float(m.group(3)), u2_lo=float(m.group(4)), u2_hi=float(m.group(5)),
                             u1=float(m.group(6)), u1_lo=float(m.group(7)), u1_hi=float(m.group(8)), call=m.group(9))
    pp = re.search(r"\*\*Per piece\.\*\*(.*)", txt)
    calls = dict(re.findall(r"\b(mm|mp|pm|pp) (PASS|FAIL)\b", pp.group(1))) if pp else {}
    ov = re.search(r"\*\*Overall verdict\.\*\*\s*(PASS|FAIL)", txt)
    pr = re.search(r"Probability that the retry reads PASS:\s*(\d+(?:\.\d+)?)", txt)
    ok = (len(cells) == 32 and set(cells) == {(p, t) for p in PIECES for t in TIMES} and set(calls) == set(PIECES)
          and ov and pr)
    if not ok:
        sys.exit("REFUSED: the sealed file does not parse: %d cells, piece calls %s, verdict %s, probability %s"
                 % (len(cells), sorted(calls), bool(ov), bool(pr)))
    return cells, calls, ov.group(1), float(pr.group(1))


def parse_reader(txt):
    vm = re.search(r"^VERDICT: (PASS|FAIL|INVALID)", txt, re.M)
    if not vm: sys.exit("REFUSED: no VERDICT line in the read_retry.sh output")
    act, piece, cur = {}, {}, None
    for l in txt.splitlines():
        m = re.match(r"== piece (mm|mp|pm|pp):", l)
        if m: cur = m.group(1); continue
        m = re.match(r"checkpoint (\d+\.\d+): (.*)", l)
        if m and cur:
            t, rest = m.group(1), m.group(2)
            r = re.search(r"u1 \S+/\S+=([\d.]+) u2 \S+/\S+=([\d.]+)", rest)
            act[(cur, t)] = None if ("NOT REACHED" in rest or not r) else dict(u1=float(r.group(1)), u2=float(r.group(2)))
        m = re.match(r"piece (mm|mp|pm|pp): (PASS|FAIL|NO RUN)", l)
        if m: piece[m.group(1)] = "PASS" if m.group(2) == "PASS" else "FAIL"
    return act, piece, vm.group(1)


def main():
    pred = parse_prediction(sealed())
    if sys.argv[1:] == ["--parse-check"]:
        print("sealed sha256 OK; parses: 32 cells, 4 piece calls, a verdict and a probability (content not printed)"); return
    if len(sys.argv) != 2: sys.exit(__doc__)
    cells, calls, verdict, prob = pred
    act, piece, av = parse_reader(open(sys.argv[1]).read())
    print("# Grading of the sealed retry prediction (BRIEF_FABLE_PREDICT.md section 4; grade_prediction.py)")
    print(f"- sealed {COMMIT[:7]} sha256 {SHA[:16]}... verified; reader verdict: {av}")
    n = in2 = in1 = 0
    print("\n| Piece | Checkpoint | u2 actual | u2 interval | in? | u1 actual | u1 interval | in? |\n|---|---|---|---|---|---|---|---|")
    for p in PIECES:
        for t in TIMES:
            c, a = cells[(p, t)], act.get((p, t))
            if a is None:
                print(f"| {p} | {t} | not reached | [{c['u2_lo']:.2f}, {c['u2_hi']:.2f}] | excluded | - | [{c['u1_lo']:.2f}, {c['u1_hi']:.2f}] | excluded |"); continue
            i2 = c["u2_lo"] <= a["u2"] <= c["u2_hi"]; i1 = c["u1_lo"] <= a["u1"] <= c["u1_hi"]
            n += 1; in2 += i2; in1 += i1
            print(f"| {p} | {t} | {a['u2']:.2f} | [{c['u2_lo']:.2f}, {c['u2_hi']:.2f}] | {'yes' if i2 else 'NO'} | {a['u1']:.2f} | [{c['u1_lo']:.2f}, {c['u1_hi']:.2f}] | {'yes' if i1 else 'NO'} |")
    print(f"\n(i) u2: {in2}/{n} cells inside the 80% interval ({in2 / n:.3f}); u1: {in1}/{n} ({in1 / n:.3f})" if n else
          "\n(i) no cell reached: not scored")
    right = 0
    for p in PIECES:
        a = piece.get(p, "FAIL"); right += (a == calls[p])
        print(f"(ii) piece {p}: predicted {calls[p]}, actual {a} -> {'right' if a == calls[p] else 'WRONG'}")
    print(f"(ii) {right}/4 piece calls right")
    if av == "INVALID":
        print("(iii) not scored (INVALID: a control failed; brief section 4 has no rule for it)")
        print("(iv) not scored (INVALID)")
    else:
        o = 1.0 if av == "PASS" else 0.0
        print(f"(iii) overall: predicted {verdict}, actual {av} -> {'right' if verdict == av else 'WRONG'}")
        print(f"(iv) Brier score of P(PASS) = {prob}: ({prob} - {o:.0f})^2 = {(prob - o) ** 2:.4f}")
    print("\nThe grading changes nothing about the retry's own reading.")


if __name__ == "__main__":
    main()
