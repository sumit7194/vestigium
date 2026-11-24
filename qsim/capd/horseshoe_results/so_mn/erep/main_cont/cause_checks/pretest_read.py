"""Branch-S scaling pre-test reader (RETRY_S_REGISTRATION.md). Usage: pretest_read.py run.out
g = dDe / inherited on the u2 'INJ cp' line at 793.2346; ratio = g / g_ref, with g_ref from the counted replay (d21fa6b).
PASS if ratio <= 0.70, FAIL if ratio >= 0.90, INCONCLUSIVE otherwise. The u1 line is reported, not read.
Must-fire F1: on the replay's own run.out this must print FAIL."""
import re, sys

G_REF = 3.306762e-08 / 1.437117e-06


def g_of(path, cov):
    for l in open(path):
        if l.startswith("INJ cp t=793.2346306025 %s " % cov):
            inh = float(re.search(r"inherited (\S+)", l).group(1)); dde = float(re.search(r" dDe (\S+) \|", l).group(1))
            if "new<=sum OK" not in l: raise SystemExit("consistency VIOLATED: " + l)
            return dde / inh
    raise SystemExit("no INJ cp line for %s at 793.2346 in %s" % (cov, path))


g2, g1 = g_of(sys.argv[1], "u2"), g_of(sys.argv[1], "u1")
r = g2 / G_REF
verdict = "PASS" if r <= 0.70 else "FAIL" if r >= 0.90 else "INCONCLUSIVE"
print("g_u2 %.6e  g_ref %.6e  ratio %.4f  -> %s   (u1 g %.6e, reported only)" % (g2, G_REF, r, verdict, g1))
