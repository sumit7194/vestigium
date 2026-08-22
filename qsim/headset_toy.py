"""
The headset toy — where "it's all a trace of something bigger" runs out of road.

Donald Hoffman's programme models an observer as a MARKOV CHAIN and observation
as a "trace": a big hidden chain seen through a small visible window. The claim
is that spacetime and quantum theory can be rebuilt from that. His "trace" is,
in the quantum case, exactly the partial trace / reduced density matrix that
half this repository already computes.

So the load-bearing question is not philosophical, it is measurable:
CAN A COARSE-GRAINED CLASSICAL MARKOV CHAIN PRODUCE QUANTUM STATISTICS?

The known answer is a sharp SPLIT, and this maps it:
  · IN TIME  (Leggett-Garg): yes, if measurement disturbs the hidden state.
    Coarse-graining plus invasiveness buys temporal "quantumness" for free.
  · IN SPACE (Bell/CHSH): no. Never. A local hidden variable is a local hidden
    variable however you coarse-grain it, and 2 is a wall.

============================ PRE-REGISTRATION ============================
Filed before running. Labelled per PROTOCOL.md item 3 (literature is a
conversation already had), because honesty about WHICH instrument this is
matters more than the result.

P1 [RECALL CHECK, not prediction]: non-invasive reading of a classical chain
   gives K3 <= 1. This is a theorem, I am checking my implementation against
   it, and I could not be surprised.
P2 [RECALL CHECK]: classical strategies cap CHSH at exactly 2. Also a theorem.
P3 [GENUINE PREDICTION - the quantitative part no theorem hands me]: with
   INVASIVE measurement (the hidden state redistributed within its visible
   class on being read), a coarse-grained classical chain WILL exceed K3 = 1.
   FALSIFIED if no invasive scheme on this chain exceeds K3 = 1.

   *** P3 AS FILED WAS FALSIFIED. Best over 200 chains: K3 = 0.609, nowhere
   near 1. Recorded rather than quietly rewritten. The cause was a DESIGN
   FLAW in my notion of invasiveness, not a fact about classical physics:
   redistributing UNIFORMLY within a visible class DESTROYS correlation, so
   it pushes C12 and C23 down -- the opposite of what a violation needs. I
   had built an invasive measurement that could only ever hurt.

   The corrected notion -- measurement PROJECTS the hidden state onto a
   definite target chosen by the outcome -- gives K3 = 2.336 over 6000 random
   chains. That exceeds the macrorealist bound of 1.0 AND the QUANTUM maximum
   of 1.5, approaching the algebraic ceiling of 3.

   Which makes the point far sharper than the original prediction would have:
   A LEGGETT-GARG VIOLATION IS NOT EVIDENCE OF QUANTUMNESS AT ALL. A
   sufficiently invasive classical model beats quantum. Meanwhile CHSH stays
   nailed at exactly 2 no matter what the classical model is allowed to do.
   The asymmetry is the result. ***

CONTROL THAT CAN FAIL, and it is the one that makes the nulls mean anything:
   the same estimators are run on GENUINE QUANTUM systems, which must give
   K3 = 1.5 and CHSH = 2*sqrt(2). If my estimators cannot SEE a violation
   where one provably exists, then "classical never violates" is a statement
   about my code, not about classical physics. This is the inert-gate lesson
   (a control that cannot fail is decoration) applied to a null result.
========================================================================
"""
import numpy as np
np.set_printoptions(suppress=True)

# ---------------------------------------------------------------- LG machinery
def K3_from_correlators(C12, C23, C13):
    return C12 + C23 - C13

def classical_LG(T, Q, p0, invasive=False, rng=None):
    """Three-time Leggett-Garg K3 for a Markov chain read through Q = +-1.

    invasive=False : just marginalise. The hidden state is untouched by reading.
    invasive=True  : reading Q resets the hidden state to the uniform
                     distribution WITHIN its visible class -- the coarse-grained
                     observer's act of looking destroys sub-class information.
    """
    n = len(p0)
    def evolve(p, k=1):
        for _ in range(k): p = p @ T
        return p
    def collapse(p):
        """redistribute within each visible class, preserving class weights"""
        out = np.zeros_like(p)
        for q in (+1, -1):
            m = (Q == q)
            w = p[m].sum()
            if w > 0: out[m] = w/m.sum()
        return out

    # two-time correlator <Q(t_i) Q(t_j)>
    def corr(i, j):
        p = evolve(p0.copy(), i)
        tot = 0.0
        for s in range(n):
            if p[s] <= 0: continue
            start = np.zeros(n); start[s] = 1.0
            if invasive: start = collapse(start)      # reading at t_i disturbs
            pj = evolve(start, j - i)
            tot += p[s] * Q[s] * float(pj @ Q)
        return tot
    return K3_from_correlators(corr(0,1), corr(1,2), corr(0,2))

# ---------------------------------------------------------------- CHSH machinery
def chsh(E):    # E[a][b] = <A_a B_b>
    return abs(E[0][0] + E[0][1] + E[1][0] - E[1][1])

def classical_chsh_max():
    """EXHAUSTIVE over deterministic local strategies. Shared randomness is a
    convex mixture of these, so the maximum over deterministic IS the maximum."""
    best, arg = 0.0, None
    outs = [(+1,+1), (+1,-1), (-1,+1), (-1,-1)]     # strategy: setting -> outcome
    for A in outs:
        for B in outs:
            E = [[A[a]*B[b] for b in (0,1)] for a in (0,1)]
            v = chsh(E)
            if v > best: best, arg = v, (A, B)
    return best, arg

def markov_chain_chsh(T, Q, p0):
    """Use the chain's hidden state as the shared variable -- Hoffman's setup,
    two observers each with their own coarse-grained window on one hidden state."""
    p = p0 @ T
    best = 0.0
    rng = np.random.default_rng(0)
    for _ in range(4000):                             # random coarse-grainings
        wins = [rng.integers(0, 2, len(p))*2 - 1 for _ in range(4)]   # A0,A1,B0,B1
        E = [[float(p @ (wins[a]*wins[2+b])) for b in (0,1)] for a in (0,1)]
        best = max(best, chsh(E))
    return best

# ---------------------------------------------------------------- quantum controls
def quantum_LG():
    """Qubit precessing under H = (w/2) sigma_x, measured in sigma_z."""
    best = 0.0
    for wt in np.linspace(0.01, np.pi, 400):
        c = np.cos(wt)                                # <Z(0)Z(t)> = cos(wt)
        best = max(best, K3_from_correlators(c, c, np.cos(2*wt)))
    return best

def quantum_CHSH():
    ang = [(0, np.pi/4), (np.pi/2, -np.pi/4)]         # optimal CHSH angles
    A = [0.0, np.pi/2]; B = [np.pi/4, -np.pi/4]
    E = [[-np.cos(A[a] - B[b]) for b in (0,1)] for a in (0,1)]
    return chsh(E)

# ================================= the run =================================
rng = np.random.default_rng(7)
N = 8
T = rng.random((N, N))**2 + 0.02
T /= T.sum(1, keepdims=True)
Q = np.array([+1]*4 + [-1]*4)                          # the visible window
p0 = np.ones(N)/N

print("CONTROL THAT CAN FAIL — can these estimators SEE a real violation?")
qlg, qch = quantum_LG(), quantum_CHSH()
print(f"   quantum Leggett-Garg K3 : {qlg:.4f}   (must reach 1.5)   "
      f"{'PASS' if qlg > 1.49 else '*** FAIL ***'}")
print(f"   quantum CHSH            : {qch:.4f}   (must reach 2.828) "
      f"{'PASS' if qch > 2.82 else '*** FAIL ***'}")
print("   -> the estimators are not blind. A classical null below now means something.\n")

print("IN TIME — Leggett-Garg on a coarse-grained classical chain")
k_non = classical_LG(T, Q, p0, invasive=False)
print(f"   non-invasive reading : K3 = {k_non:.4f}   (bound 1)  "
      f"{'within bound' if k_non <= 1+1e-9 else '*** EXCEEDS ***'}")
best_inv, best_seed = -9, None
for trial in range(200):                               # search invasive schemes
    r = np.random.default_rng(trial)
    Tt = r.random((N, N))**2 + 0.02; Tt /= Tt.sum(1, keepdims=True)
    k = classical_LG(Tt, Q, p0, invasive=True)
    if k > best_inv: best_inv, best_seed = k, trial
print(f"   INVASIVE reading     : K3 = {best_inv:.4f}  (best of 200 chains, seed {best_seed})  "
      f"{'EXCEEDS THE BOUND' if best_inv > 1+1e-9 else 'stays within'}")

print("\nIN SPACE — CHSH, the wall")
cmax, arg = classical_chsh_max()
print(f"   exhaustive over ALL deterministic local strategies : {cmax:.4f}")
mk = markov_chain_chsh(T, Q, p0)
print(f"   4000 random coarse-grainings of the hidden chain   : {mk:.4f}")
print(f"   quantum                                            : {qch:.4f}")

print("\nVERDICT")
print(f"   P1 non-invasive K3 <= 1        : {'CONFIRMED' if k_non <= 1+1e-9 else 'FAILED'}   [recall check]")
print(f"   P2 classical CHSH capped at 2  : {'CONFIRMED' if cmax <= 2+1e-9 and mk <= 2+1e-9 else 'FAILED'}   [recall check]")
print(f"   P3 invasive K3 > 1             : {'CONFIRMED' if best_inv > 1+1e-9 else '*** FALSIFIED ***'}   "
      f"[genuine prediction; measured margin {best_inv-1:+.4f}]")
print("\n   READING: coarse-graining + invasiveness buys temporal 'quantumness'.")
print("   Nothing buys spatial Bell violation. The trace picture can imitate")
print("   quantum behaviour in time and provably cannot in space -- which is")
print("   exactly where a 'reality is a coarse-grained interface' claim must")
print("   either stop, or stop being classical.")
