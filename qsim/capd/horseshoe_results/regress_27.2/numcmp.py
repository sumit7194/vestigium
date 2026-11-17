"""Token-wise numeric comparison of two CAPD text outputs (27.0.1 criterion for the toys and the lift: agreement to the saved
files' print resolution). Prints IDENTICAL, or AGREE, or DIFFERS.
Post-stop rule clarification (2026-11-17, agreed with the Bridge BEFORE the resume): the bound is RELATIVE to each
reference entry's own last printed digit. Every number must be within 1 unit of the REFERENCE file's last printed digit
(the saved files print 41 significant digits; the binaries now print 61). The old absolute bound of 1e-39 failed
entries of magnitude ~100 whose saved print resolution is 1e-38."""
import sys, re, mpmath as mp
mp.mp.dps = 80
a, b = open(sys.argv[1]).read(), open(sys.argv[2]).read()
if a == b: print("IDENTICAL"); sys.exit()
num = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
sa, sb = re.split(num, a), re.split(num, b)
na, nb = re.findall(num, a), re.findall(num, b)
if len(na) != len(nb): print("DIFFERS (number count %d vs %d)" % (len(na), len(nb))); sys.exit()
nonnum = [x for x, y in zip(sa, sb) if x != y]
def ulp(tok):
    m = re.match(r"[-+]?(\d*)\.?(\d*)(?:[eE]([-+]?\d+))?$", tok); return mp.mpf(10) ** (int(m.group(3) or 0) - len(m.group(2)))
d = max((abs(mp.mpf(x) - mp.mpf(y)) for x, y in zip(na, nb)), default=0)
units = max((abs(mp.mpf(x) - mp.mpf(y)) / ulp(y) for x, y in zip(na, nb)), default=0)
ws = lambda s: " ".join(s.split())
if any(ws(x) != ws(y) for x, y in zip(sa, sb)): print("DIFFERS (text) max|diff| %s" % mp.nstr(d, 3)); sys.exit()
print(("AGREE" if units <= 1 else "DIFFERS") + " max|diff| %s, max %s units of the reference's last printed digit" % (mp.nstr(d, 3), mp.nstr(units, 3)))
