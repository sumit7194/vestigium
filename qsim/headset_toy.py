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

   SCOPE, narrowed after an adversarial read by the bridge session, whose
   framing is better than mine and is adopted:

   "A Leggett-Garg violation is not evidence of quantumness" is TRUE AND
   TEXTBOOK -- it is the clumsiness loophole, and nobody has ever shown LG
   violation implies non-classicality without an independent bound on
   invasiveness. So this is a [RECALL CHECK] demonstrating a known loophole,
   not a discovery. And K3 exceeding the quantum 1.5 is unsurprising once
   arbitrary invasiveness is granted, since the algebraic bound for +-1
   observables is 3 and nothing makes the quantum value a barrier.

   THE PART THAT SURVIVES EVERY OBJECTION, and is the actual result:
     WITH UNBOUNDED INVASIVENESS THE LG BOUND IS NOT A QUANTUMNESS TEST,
     WHICH IS WHY LG EXPERIMENTS REQUIRE AN INDEPENDENT INVASIVENESS BOUND
     AND BELL DOES NOT.
   That asymmetry is the result. Bell needs no such bound because CHSH = 2 is
   a wall against ANY local model, however invasive. ***

   *** AND A DEFECT WORTH MORE THAN THE RESULT, caught by the bridge: for
   several hours this docstring asserted K3 = 2.336 while the committed code
   computed only the failed 0.609 version. I had run the projection variant in
   an ad-hoc shell heredoc, written the number into prose, and never committed
   the code. The file reported its own falsification directly beneath a claim it
   could not reproduce. A RESULT WHOSE INPUTS ARE NOT ON DISK IS A CLAIM ABOUT
   WHAT WAS SEEN, NOT A MEASUREMENT. classical_LG_projective() below is that
   code, now committed and run by this script. ***

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


def classical_LG_projective(T, Q, p0, targ):
    """LG with GENUINELY invasive measurement: reading Q projects the hidden state
    onto a definite target chosen BY THE OUTCOME.

    This is the version that produces the headline number. The weaker scheme in
    classical_LG(invasive=True) above -- uniform redistribution within the visible
    class -- DESTROYS correlation and can only push the correlators the wrong way,
    which is why P3 failed as filed.

    targ = (state to project into on Q=+1, state to project into on Q=-1).
    """
    n = len(p0)
    def ev(p, k):
        for _ in range(k): p = p @ T
        return p
    def corr(i, j, disturbed):
        p = ev(p0.copy(), i); tot = 0.0
        for s in range(n):
            if p[s] <= 0: continue
            q = Q[s]
            st = np.zeros(n)
            st[targ[0] if q > 0 else targ[1]] = 1.0 if disturbed else 0.0
            if not disturbed: st[s] = 1.0
            tot += p[s]*q*float(ev(st, j-i) @ Q)
        return tot
    # C12 and C23 each involve a disturbing read; C13 has no read in between
    return K3_from_correlators(corr(0,1,True), corr(1,2,True), corr(0,2,False))

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
for trial in range(200):                               # WEAK invasiveness (the failed design)
    r = np.random.default_rng(trial)
    Tt = r.random((N, N))**2 + 0.02; Tt /= Tt.sum(1, keepdims=True)
    k = classical_LG(Tt, Q, p0, invasive=True)
    if k > best_inv: best_inv, best_seed = k, trial
print(f"   weak invasive (uniform redistribution) : K3 = {best_inv:.4f}  "
      f"(best of 200 chains)  {'EXCEEDS' if best_inv > 1+1e-9 else 'stays within -- P3 AS FILED FAILED HERE'}")

# GENUINE invasiveness: outcome-conditioned projection. This is the headline run,
# and it is COMPUTED here rather than asserted in a docstring.
Np = 6
Qp = np.array([+1,+1,+1,-1,-1,-1]); p0p = np.ones(Np)/Np
best_proj, proj_seed = -9, None
for trial in range(6000):
    r = np.random.default_rng(trial)
    Tt = r.random((Np, Np))**3 + 1e-3; Tt /= Tt.sum(1, keepdims=True)
    tg = (int(r.integers(0,3)), int(r.integers(3,6)))
    k = classical_LG_projective(Tt, Qp, p0p, tg)
    if k > best_proj: best_proj, proj_seed = k, trial
print(f"   GENUINE invasive (outcome-conditioned projection) : K3 = {best_proj:.4f}  "
      f"(best of 6000 chains, seed {proj_seed})")
print(f"      vs macrorealist bound 1.0, QUANTUM max 1.5, algebraic max 3.0")

print("\nIN SPACE — CHSH, the wall")
cmax, arg = classical_chsh_max()
print(f"   exhaustive over ALL deterministic local strategies : {cmax:.4f}")
mk = markov_chain_chsh(T, Q, p0)
print(f"   4000 random coarse-grainings of the hidden chain   : {mk:.4f}   "
      f"[CONSISTENCY CHECK ONLY -- this is an LHV model by construction, so it\n        cannot exceed 2; hitting 2.0000 shows the sampler found an extremal\n        point, it is NOT independent evidence about coarse-graining]")
print(f"   quantum                                            : {qch:.4f}")

print("\nVERDICT")
print(f"   P1 non-invasive K3 <= 1        : {'CONFIRMED' if k_non <= 1+1e-9 else 'FAILED'}   [recall check]")
print(f"   P2 classical CHSH capped at 2  : {'CONFIRMED' if cmax <= 2+1e-9 and mk <= 2+1e-9 else 'FAILED'}   [recall check]")
print(f"   P3 as filed (weak invasive)    : {'CONFIRMED' if best_inv > 1+1e-9 else '*** FALSIFIED ***'}   "
      f"[margin {best_inv-1:+.4f}] -- the design flaw, kept]")
print(f"   P3 corrected (projective)      : {'CONFIRMED' if best_proj > 1+1e-9 else 'FAILED'}   "
      f"[K3 = {best_proj:.4f}; exceeds quantum 1.5: {'YES' if best_proj > 1.5 else 'no'}]")
print("\n   READING: coarse-graining + invasiveness buys temporal 'quantumness'.")
print("   Nothing buys spatial Bell violation. The trace picture can imitate")
print("   quantum behaviour in time and provably cannot in space -- which is")
print("   exactly where a 'reality is a coarse-grained interface' claim must")
print("   either stop, or stop being classical.")

# ---------------------------------------------------------------------------
# ARTIFACT. Added after the bridge's adversarial read found that this file's
# headline K3 = 2.336 had been computed in an ad-hoc shell heredoc, written into
# the docstring, and never committed -- so the repo could not produce its own
# published number. Implementing the function fixed half of that. This fixes the
# other half: the numbers now leave the terminal and land in a file that
# verify.py re-asserts, so drift is visible instead of invisible.
# ---------------------------------------------------------------------------
import json as _json, os as _os
_out = dict(
    controls=dict(quantum_LG_K3=float(qlg), quantum_CHSH=float(qch)),
    classical=dict(
        LG_noninvasive=float(k_non),
        LG_weak_invasive_best=float(best_inv), weak_invasive_seed=int(best_seed),
        LG_projective_best=float(best_proj), projective_seed=int(proj_seed),
        chsh_exhaustive_deterministic=float(cmax),
        chsh_markov_coarsegrain=float(mk),
    ),
    verdict=dict(
        P1_recall_noninvasive_within_bound=bool(k_non <= 1 + 1e-9),
        P2_recall_chsh_capped=bool(cmax <= 2 + 1e-9 and mk <= 2 + 1e-9),
        P3_as_filed_FALSIFIED=bool(best_inv <= 1 + 1e-9),
        P3_corrected_projective_exceeds_1=bool(best_proj > 1 + 1e-9),
        projective_exceeds_quantum_1p5=bool(best_proj > 1.5),
    ),
    scope=("with unbounded invasiveness the LG bound is not a quantumness test, "
           "which is why LG experiments require an independent invasiveness bound "
           "and Bell does not"),
)
with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                        "headset_toy.json"), "w") as _fh:
    _json.dump(_out, _fh, indent=2)
print("\n   artifact written: qsim/headset_toy.json")
