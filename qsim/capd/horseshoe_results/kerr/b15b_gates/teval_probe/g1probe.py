import sys, json, signal, tracemalloc, resource, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
G = "/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15b_gates/"
t = [t for t in json.load(open(G + "tasks.json")) if t["id"] == "G1_00_P"][0]
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
n = [0]; last = [0.0]; rhs0 = kerr.rhs
def rhs(tt, s): n[0] += 1; last[0] = tt; return rhs0(tt, s)
kerr.rhs = rhs
class Stop(Exception): pass
import time; T0=time.time(); K=[0]
def alarm(*a):
    K[0]+=1; cur,_=tracemalloc.get_traced_memory()
    print("%4.0fs rhs %d t %.9g traced %.1f MB rss %.0f MB" % (time.time()-T0, n[0], last[0], cur/2**20, resource.getrusage(0).ru_maxrss/2**20), flush=True)
    if K[0]==1 or K[0]%4==0:
        for st in tracemalloc.take_snapshot().statistics("lineno")[:3]: print("   ", str(st)[-110:], flush=True)
    if K[0]>=int(sys.argv[1]): raise Stop
    signal.alarm(30)
tracemalloc.start(); signal.signal(signal.SIGALRM, alarm); signal.alarm(30)
try: kerr.P(np.array(t["w"]), 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"]); print("finished")
except Stop: pass
cur, peak = tracemalloc.get_traced_memory()
print("rhs calls %d (~%d steps), t reached %.6g, traced %.1f MB, maxrss %.0f MB" % (n[0], n[0] // 12, last[0], cur / 2**20, resource.getrusage(0).ru_maxrss / 2**20))
for s in tracemalloc.take_snapshot().statistics("lineno")[:6]: print(s)
