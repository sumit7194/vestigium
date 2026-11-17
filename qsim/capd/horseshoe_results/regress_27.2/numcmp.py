"""Token-wise numeric comparison of two CAPD text outputs (27.0.1 criterion for the toys and the lift: agreement to the saved
files' print resolution). Prints IDENTICAL, or AGREE max|diff| (structure equal, numbers within 1e-39), or DIFFERS."""
import sys, re, mpmath as mp
mp.mp.dps = 80
a, b = open(sys.argv[1]).read(), open(sys.argv[2]).read()
if a == b: print("IDENTICAL"); sys.exit()
num = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
sa, sb = re.split(num, a), re.split(num, b)
na, nb = re.findall(num, a), re.findall(num, b)
if len(na) != len(nb): print("DIFFERS (number count %d vs %d)" % (len(na), len(nb))); sys.exit()
nonnum = [x for x, y in zip(sa, sb) if x != y]
d = max((abs(mp.mpf(x) - mp.mpf(y)) for x, y in zip(na, nb)), default=0)
ws = lambda s: " ".join(s.split())
if any(ws(x) != ws(y) for x, y in zip(sa, sb)): print("DIFFERS (text) max|diff| %s" % mp.nstr(d, 3)); sys.exit()
print(("AGREE max|diff| %s" if d <= mp.mpf("1e-39") else "DIFFERS max|diff| %s") % mp.nstr(d, 3))
