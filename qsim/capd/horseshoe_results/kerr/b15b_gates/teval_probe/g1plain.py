import sys, json, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
G = "/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15b_gates/"
t = [t for t in json.load(open(G + "tasks.json")) if t["id"] == "G1_00_P"][0]
kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
kerr.P(np.array(t["w"]), 1, jac=t["jac"], tmax=t["tmax"], rtol=t["tol"], atol=t["tol"])
