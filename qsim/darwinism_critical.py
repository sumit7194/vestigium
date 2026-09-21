#!/usr/bin/env python3
"""H3 route A — does a record crystallise differently in a critical environment?

Pre-registered in qsim/PREREG_darwinism_critical.md BEFORE this file existed.
Read that first; the predictions, controls and named failure modes are there and
are not restated here except where the code enforces them.

ROUTE A: exact, full Hilbert space, L <= 16 environment spins + 1 system qubit.
Gives the FULL I(S:F) including coherences, which is what makes control C3 (the
pure-state sum rule I(S:F=all) = 2 S(rho_S)) available at all. Route B, the
Gaussian one, cannot do C3 and is a separate file by design.

THE ONE THING THE CODE ENFORCES RATHER THAN DOCUMENTS: every critical-vs-gapped
comparison is made at MATCHED DECOHERENCE, i.e. equal S(rho_S), never at equal
time. match_time() below solves for the time at which a chain reaches a target
S(rho_S). Comparing at equal t would let any difference be a difference in how
far decoherence had got -- hazard 1 in the registration, and the shape of the
error this repo has logged six times.
"""
import json
import numpy as np
from itertools import combinations

I2 = np.eye(2)
SX = np.array([[0, 1], [1, 0]], float)
SZ = np.array([[1, 0], [0, -1]], float)


# ----------------------------------------------------------- the environment
def tfi_hamiltonian(L, g, J=1.0, local_field=None):
    """H = -J sum sx_i sx_{i+1} - h sum sz_i, open chain, h = g*J.
    local_field: optional array added to the transverse field site by site."""
    dim = 1 << L
    H = np.zeros((dim, dim))
    h = g*J*np.ones(L)
    if local_field is not None:
        h = h + local_field

    def op_at(op, i):
        M = np.array([[1.0]])
        for k in range(L):
            M = np.kron(M, op if k == i else I2)
        return M

    for i in range(L - 1):
        H -= J*(op_at(SX, i) @ op_at(SX, i + 1))
    for i in range(L):
        H -= h[i]*op_at(SZ, i)
    return H


def ground_state(H):
    w, v = np.linalg.eigh(H)
    return v[:, 0]


# ------------------------------------------------------------ the joint state
def branches(L, g, lam, i0, t, J=1.0):
    """|E_+-(t)> = exp(-i H_+- t)|E_0>, H_+- = H_E(g) +- lam sz_{i0}.
    Both branches start from the SAME ground state of the unperturbed chain."""
    H0 = tfi_hamiltonian(L, g, J)
    e0 = ground_state(H0)
    out = []
    for sgn in (+1.0, -1.0):
        f = np.zeros(L); f[i0] = sgn*lam
        w, v = np.linalg.eigh(tfi_hamiltonian(L, g, J, local_field=f))
        out.append(v @ (np.exp(-1j*w*t)*(v.T @ e0)))
    return out[0], out[1]


def joint_state(ep, em):
    """(|0>|E_+> + |1>|E_->)/sqrt(2), system qubit as the MOST significant bit."""
    return np.concatenate([ep, em])/np.sqrt(2.0)


# ------------------------------------------------------- reductions, exactly
def rdm(psi, L, keep_env, keep_sys):
    """Reduced density matrix on (system if keep_sys) + environment sites keep_env.
    psi is indexed as [s, e_0, ..., e_{L-1}] with s the most significant bit."""
    t = psi.reshape([2] + [2]*L)
    keep = ([0] if keep_sys else []) + [1 + i for i in keep_env]
    rest = [ax for ax in range(L + 1) if ax not in keep]
    t = np.transpose(t, keep + rest)
    d = 1 << len(keep)
    t = t.reshape(d, -1)
    return t @ t.conj().T


def vn_entropy(rho):
    w = np.linalg.eigvalsh(0.5*(rho + rho.conj().T))
    w = w[w > 1e-13]
    return float(-(w*np.log2(w)).sum())


def sub_entropy(psi, L, keep_env, keep_sys):
    """Entropy of a subsystem, tracing to whichever SIDE IS SMALLER.

    The global state is pure, so S(A) = S(complement of A) exactly. Without this
    the f = L term builds an 8192x8192 matrix (1.07 GB) for L = 12 and the cost
    is 2^L rather than 2^(L/2). Caught by watching RSS climb past 0.95 GB on a
    shared box -- my bug, and the identity was available the whole time."""
    kept = (1 if keep_sys else 0) + len(keep_env)
    total = L + 1
    if kept*2 <= total:
        return vn_entropy(rdm(psi, L, keep_env, keep_sys))
    comp_env = [i for i in range(L) if i not in set(keep_env)]
    return vn_entropy(rdm(psi, L, comp_env, not keep_sys))


def mutual_info(psi, L, frag):
    """I(S:F) = S(S) + S(F) - S(SF), full quantum mutual information."""
    sS = sub_entropy(psi, L, [], True)
    sF = sub_entropy(psi, L, list(frag), False)
    sSF = sub_entropy(psi, L, list(frag), True)
    return sS + sF - sSF, sS


def pip(psi, L, n_samp=60, rng=None):
    """Partial-information plot: mean I(S:F) over UNIFORMLY RANDOM fragments of
    each size f. Sampling convention fixed in the registration (hazard 4)."""
    rng = rng or np.random.default_rng(0)
    out = []
    for f in range(0, L + 1):
        if f == 0:
            out.append(0.0); continue
        n_all = len(list(combinations(range(L), f))) if f <= 2 or f >= L - 2 else None
        if n_all is not None and n_all <= n_samp:
            frags = list(combinations(range(L), f))
        else:
            frags = [tuple(rng.choice(L, size=f, replace=False)) for _ in range(n_samp)]
        out.append(float(np.mean([mutual_info(psi, L, fr)[0] for fr in frags])))
    return np.array(out)


def redundancy(pi, sS, delta=0.1):
    """R_delta = L / f_delta, f_delta the smallest fragment reaching (1-delta) S(S)."""
    L = len(pi) - 1
    tgt = (1.0 - delta)*sS
    for f in range(1, L + 1):
        if pi[f] >= tgt:
            return L/f, f
    return float("nan"), None


# --------------------------------------------- matched decoherence, enforced
def s_sys(L, g, lam, i0, t):
    ep, em = branches(L, g, lam, i0, t)
    return vn_entropy(rdm(joint_state(ep, em), L, [], True))


def match_time(L, g, lam, i0, target, t_hi=40.0, tol=1e-3):
    """Smallest t with S(rho_S) = target. Bisection on the first crossing.
    THIS is what makes the comparison legitimate -- see module docstring."""
    ts = np.linspace(0.05, t_hi, 240)
    prev_t, prev_s = ts[0], s_sys(L, g, lam, i0, ts[0])
    for t in ts[1:]:
        s = s_sys(L, g, lam, i0, t)
        if (prev_s - target)*(s - target) <= 0 and s != prev_s:
            lo, hi = prev_t, t
            for _ in range(40):
                mid = 0.5*(lo + hi)
                if (s_sys(L, g, lam, i0, mid) - target)*(s_sys(L, g, lam, i0, lo) - target) <= 0:
                    hi = mid
                else:
                    lo = mid
                if hi - lo < tol:
                    break
            return 0.5*(lo + hi)
        prev_t, prev_s = t, s
    return None


# ================================== CONTROLS, run before any physics is read
def controls(L=10, g=1.0, lam=0.6, t=6.0):
    i0 = L//2
    rep = {}
    print("="*70); print("CONTROLS — these run first and gate everything below")
    print("="*70)

    # C1 TRIVIAL: lam = 0 must give I = 0 for every f, WHILE the chain is entangled.
    ep, em = branches(L, g, 0.0, i0, t)
    psi0 = joint_state(ep, em)
    worst = max(mutual_info(psi0, L, tuple(range(f)))[0] for f in range(1, L))
    chain_S = vn_entropy(rdm(psi0, L, list(range(L//2)), False))
    rep["C1_worst_I_at_lambda0"] = worst
    rep["C1_chain_half_entropy"] = chain_S
    ok1 = worst < 1e-10 and chain_S > 0.5
    print(f"  C1 TRIVIAL  lambda=0: worst I(S:F) = {worst:.3e}   (need < 1e-10)")
    print(f"     and the chain is NOT trivially unentangled: S(half) = {chain_S:.4f} (need > 0.5)")
    print(f"     -> {'PASS' if ok1 else '*** FAIL ***'}")

    # C3 SUM RULE: pure global state => I(S:all) = 2 S(rho_S), machine precision.
    ep, em = branches(L, g, lam, i0, t)
    psi = joint_state(ep, em)
    I_all, sS = mutual_info(psi, L, tuple(range(L)))
    rep["C3_I_all"] = I_all; rep["C3_2S"] = 2*sS
    ok3 = abs(I_all - 2*sS) < 1e-9
    print(f"  C3 SUM RULE I(S:all) = {I_all:.10f}  vs  2 S(rho_S) = {2*sS:.10f}"
          f"   -> {'PASS' if ok3 else '*** FAIL ***'}")

    # C4 MONOTONICITY of the averaged partial-information plot.
    pi = pip(psi, L, n_samp=40)
    dmin = float(np.min(np.diff(pi)))
    rep["C4_min_increment"] = dmin
    ok4 = dmin > -1e-9
    print(f"  C4 MONOTONIC  min increment = {dmin:+.3e}   -> {'PASS' if ok4 else '*** FAIL ***'}")

    # C2 KNOWN ANSWER: J=0, every env qubit coupled -> textbook sharp plateau.
    dim = 1 << L
    psi_ind = np.zeros(2*dim, complex)
    th = 0.9
    single = np.array([np.cos(th/2), np.sin(th/2)])
    upv, dnv = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    a = np.array([1.0]); b = np.array([1.0])
    for _ in range(L):
        a = np.kron(a, np.cos(th/2)*upv + np.sin(th/2)*dnv)
        b = np.kron(b, np.cos(th/2)*upv - np.sin(th/2)*dnv)
    psi_ind[:dim] = a/np.sqrt(2.0); psi_ind[dim:] = b/np.sqrt(2.0)
    pi_ind = pip(psi_ind, L, n_samp=40)
    sS_ind = vn_entropy(rdm(psi_ind, L, [], True))
    R_ind, f_ind = redundancy(pi_ind, sS_ind)
    rep["C2_R"] = R_ind; rep["C2_f"] = f_ind; rep["C2_plateau"] = float(pi_ind[L//2])
    ok2 = (f_ind is not None and f_ind <= 3 and abs(pi_ind[L//2] - sS_ind) < 0.05)
    print(f"  C2 KNOWN    independent qubits: plateau {pi_ind[L//2]:.4f} vs S(S) {sS_ind:.4f},"
          f" f_delta = {f_ind}, R = {R_ind:.2f}  -> {'PASS' if ok2 else '*** FAIL ***'}")
    print(f"     (textbook Darwinism: a few qubits carry the record, R ~ L)")
    rep["all_pass"] = bool(ok1 and ok2 and ok3 and ok4)
    print(f"\n  CONTROLS {'ALL PASS' if rep['all_pass'] else '*** FAILED — nothing below is readable ***'}")
    return rep


# ============================================ the measurement, routed through
# a cached evolver. branches() above re-diagonalises per time point, which is
# fine for the controls and hopeless for a sweep: H_+- do not depend on t, so
# the spectra are computed once and every time is a phase multiply.
class Branches:
    def __init__(self, L, g, lam, i0, J=1.0):
        self.L = L
        e0 = ground_state(tfi_hamiltonian(L, g, J))
        self.w, self.v, self.c = [], [], []
        for sgn in (+1.0, -1.0):
            f = np.zeros(L); f[i0] = sgn*lam
            w, v = np.linalg.eigh(tfi_hamiltonian(L, g, J, local_field=f))
            self.w.append(w); self.v.append(v); self.c.append(v.T @ e0)

    def psi(self, t):
        b = [self.v[k] @ (np.exp(-1j*self.w[k]*t)*self.c[k]) for k in (0, 1)]
        return joint_state(b[0], b[1])

    def sS(self, t):
        return vn_entropy(rdm(self.psi(t), self.L, [], True))

    def match(self, target, t_hi=60.0, n=400, t_lo=1e-4):
        """First time reaching target S(rho_S). THE comparison is made here:
        equal decoherence, never equal t (hazard 1 of the registration).

        LOG-SPACED from t_lo. A linear scan starting at t=0.05 reported "no
        crossing" for the critical chain at a target it passes before t=0.05 --
        the fast chain looked like the one that never got there. A scan floor is
        an assumption about rates, and it was wrong by the largest margin
        exactly where the physics was fastest."""
        ts = np.geomspace(t_lo, t_hi, n)
        pv = self.sS(ts[0])
        for a, b in zip(ts[:-1], ts[1:]):
            sv = self.sS(b)
            if (pv - target)*(sv - target) <= 0 and sv != pv:
                lo, hi = a, b
                for _ in range(45):
                    m = 0.5*(lo + hi)
                    if (self.sS(m) - target)*(self.sS(lo) - target) <= 0:
                        hi = m
                    else:
                        lo = m
                return 0.5*(lo + hi)
            pv = sv
        return None


def measure(L=12, lam=0.6, target=0.30, gs=(1.0, 2.0, 3.0), n_samp=80, seed=0):
    """Critical (g=1) vs gapped, AT MATCHED DECOHERENCE."""
    i0 = L//2
    rng = np.random.default_rng(seed)
    rows = []
    print("\n" + "="*70)
    print(f"MEASUREMENT  L={L}  lambda={lam}  matched at S(rho_S)={target}")
    print("="*70)
    print(f"  {'g':>5}{'t_match':>10}{'S(S)':>9}{'f_delta':>9}{'R':>8}{'chi_inf':>10}")
    for g in gs:
        br = Branches(L, g, lam, i0)
        tm = br.match(target)
        if tm is None:
            print(f"  {g:5.2f}   never reaches S={target} within t_hi — excluded")
            continue
        psi = br.psi(tm)
        sS = vn_entropy(rdm(psi, L, [], True))
        pi = pip(psi, L, n_samp=n_samp, rng=rng)
        R, fd = redundancy(pi, sS)
        rows.append(dict(g=g, t_match=tm, sS=sS, f_delta=fd, R=R,
                         pi=[float(x) for x in pi]))
        print(f"  {g:5.2f}{tm:10.3f}{sS:9.4f}{str(fd):>9}{R:8.2f}{pi[L//2]:10.4f}")
    return rows


if __name__ == "__main__":
    import sys
    rep = controls()
    json.dump(rep, open("qsim/darwinism_controls.json", "w"), indent=1)
    if not rep["all_pass"]:
        sys.exit(1)
    rows = measure()
    json.dump({"controls": rep, "rows": rows},
              open("qsim/darwinism_critical.json", "w"), indent=1)
