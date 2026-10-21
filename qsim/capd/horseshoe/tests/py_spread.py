import sys, numpy as np, sympy as sp, mpmath as mp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
f = MNN.MNFlow(89, 80, sp.Rational(13394411,1186380), sp.Rational(19,20), sp.Integer(267))
x0, px0, h = 3.6419361737, 6.0360992808, 1e-6
v = [f.py_of(x0+a*h, px0+b*h) for a in (-1,0,1) for b in (-1,0,1)]
print("true p_y spread over the box (double):", max(v)-min(v))
gxx, gyy, V = f._g(x0, 0.0); print("gxx gyy V at centre", gxx, gyy, V)
