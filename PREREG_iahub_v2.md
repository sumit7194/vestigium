# DRAFT for review — Interval-arithmetic hub v2: certified monodromy, done properly

**Status: DESIGN DRAFT, for review by the user and the bridge. Not registered for running.** Nothing in here
touches a target until this draft is accepted and committed as a registration.

**Goal (the user's framing):** the *best* result, not the fastest. Up-front work is welcome when it buys rigour.

**What "best" means here:**
1. **Proofs that are checked twice and checked properly.**
   - Every certificate is found by one implementation and replayed by an independent one.
   - Every hand-written glue lemma is machine-checked in Lean.
2. **The tool finishes the questions that matter.** The immediate case is the MN equatorial rows, including L ≠ 0.
3. **The tool is reusable** across fleet items (K19, C18).

**Measured starting point** (`qsim/mr_mneq_step_profile.log`, 2026-10-03):
- One certified step on the MN equatorial ξ₁ equation takes **0.67 s**.
- **About 98 %** of that is evaluating the reduced coefficient r = P/Q (1389/1361 terms; about 4.7·10³ operations
  after cse) as a 100-term power series. That cost is roughly half Arb's C series arithmetic (34 µs per
  length-102 multiply at 192 bits) and half Python walking the expression tree.
- The Taylor recursion is **0.2 %**.
- P and Q are evaluated **twice** per step (once for the bound, once for the coefficients), and again on every
  rejected (halved) step.

**Conclusion:** the language is a second-order cost. The first-order costs are **which equation we integrate**
and **how often we evaluate it**.

---

## 1. Mathematics: integrate a smaller equation

**Current:** the reduced form y″ = r y, with r = p²/4 + p′/2 − q. It needs p′ and p², which is where the
1389-term blow-up comes from.

**v2:** integrate the **non-reduced** ξ₁ equation as a first-order system,

    ξ₁″ + p ξ₁′ + q ξ₁ = 0,   p = −(A′/A − X′/(2X)),   q = AB/X,   X = ṫ²,
    Y′ = M(t) Y,   M = [[0, 1], [−q, −p]].

- p and q are rational in ℚ(t, E) **with no square root**. The profile shows p₁ at 194/170 terms, against r₁'s
  1389/1361.
- ξ₁ is the NVE component itself. There is **no gauge factor at all**, so the t-plane monodromy of this system is
  the NVE monodromy on the fibre product. That holds because p and q depend only on ṫ², so they are the same on
  both sheets; loops lift after at most squaring, as before.
- **The certificate becomes scale-free, in GL(2).** det Y is no longer 1: it equals exp(−∫p). So conditions (i)–(ii)
  become **tr(g)²/det(g) ∉ [0, 4]**, which is equivalent to tr(g/√det g) ∉ [−2, 2] for either root and needs no
  branch. Condition (iii), **tr[g, h] ≠ 2**, is unchanged, because [g, h] ∈ SL(2) automatically. The equivalence
  proof is Lean lemma L5 below.
- **Majorant for first-order systems (a new derivation, to be written out in full in the registration).**
  - For Y = Σ Y_n tⁿ, the recursion is (n+1) Y_{n+1} = Σ_{k=0}^{n} M_k Y_{n−k}.
  - Write m_k = ‖M_k‖ρᵏ ≤ M̄, and set B_n = ‖Y_n‖ρⁿ and S_n = Σ_{j≤n} B_j. Then
    `S_{n+1} ≤ S_n(1 + ρM̄/(n+1))`, so `B_n ≤ S_N (n/N)^{ρM̄}` for n > N. At q = |t|/ρ = ½ the tail is explicitly
    summable.
  - For k ≤ N use the exact ‖M_k‖ (A2); for k > N use the centred Cauchy bound on a 1.5× disk (A4).

## 2. Evaluation: once per step, compiled

- P and Q, as polynomials in (t, E₁, E₂, E₃), are compiled **once** into a **straight-line program**: Horner in t,
  with coefficients polynomial in the E's.
- Per step:
  - each E_i series is computed **once**, as exp of a rational series;
  - P and Q series are computed **once** and reused for both the centred sup-bound and the Taylor coefficients;
  - a rejected step reuses nothing it can't, but its disk test runs *before* the expensive series.
- **Adaptive steps:** the step size comes from the certified radius rather than a fixed 0.2 × dist, and the
  order N is chosen per step (60–150) against the tail bound. These are policy only; rigour stays in the
  enclosures.

## 3. Native core (Rust, FFI to FLINT/Arb 3.6.0)

- **Inputs:** the straight-line programs, with exact rational constants and exp definitions; the loop geometry;
  the precision.
- **Outputs:** monodromy enclosures written as exact Arb balls (midpoint and radius strings).
- **Rust owns the hot loop:** series ops, the recursion, majorants, transport.
- **Python/SymPy stays as the front end:** exact equation building, about 46 s per row.
- **Loops run in parallel**, one thread each. They are independent, and the machine has 10 cores.
- **Process discipline:** its own process, pausable with SIGSTOP, a thread count adjustable at runtime, memory
  sized by the whole process tree, and runs under the existing watchdog.
- **The setup is already verified** (ec16ee2): the Rust→Arb FFI gives an enclosure of exp(1+i) byte-identical to
  python-flint's.

## 4. Two-implementation proof rule

A certificate counts only if:
1. **the Rust v2 core finds it** (the search);
2. **the frozen, G0-validated Python v1 hub independently replays it.** v1 uses the *reduced* form, a different
   equation and different code, and only the 2–4 certifying loops need replaying, not the whole search, which keeps
   it affordable. v1's enclosures must satisfy the certificate on their own.

Agreement here is two rigorous enclosures, each sufficient alone, not two numbers that are "close".

## 5. Lean 4 + Mathlib: machine-check the glue lemmas

**Formalised (targets):**
- **L1.** For g, h ∈ SL(2, ℂ): tr[g, h] = 2 ⇔ g and h have a common eigenvector.
- **L2.** tr g ∉ [−2, 2] ⇒ g has two distinct eigenvalues of modulus ≠ 1, so infinite order and exactly two
  eigenlines.
- **L3.** Every element of N(T) \ T in SL(2) has trace 0.
- **L4.** Invariance of (i)–(iii) under g ↦ λg and under (g, h) ↦ (g², h²).
- **L5.** The GL(2) restatement: tr²/det ∉ [0, 4] ⇔ the normalised trace ∉ [−2, 2].
- **L6.** The group-theoretic core of the certificate: a subgroup of SL(2, ℂ) containing g, h as in (i)–(iii) is
  **not virtually abelian**, and has no finite-index subgroup fixing a line or a pair of lines.
- **L7** (TS route). The algebraic core of the 2b′ uniqueness lemma: ±(unipotent ≠ I) has exactly one eigenline.

**Cited, not formalised (stated as such in every verdict):**
- the Ziglin / Morales–Ramis theorem;
- Schlesinger's theorem;
- the classification of algebraic subgroups of SL(2) by their identity component;
- Kovacic's algorithm.

Formalising differential Galois theory is out of scope; to my knowledge it isn't in Mathlib.

**Setup in progress** (2026-10-03): elan 4.2.4 via Homebrew; Mathlib project `lean/ZiglinCert` with the pre-built
cache. A disk guard stops the setup if free disk falls below 4 GB, per the user.

## 6. Validation ladder (all before any target; each rung committed and pushed)

1. **V-G0:** the known-monodromy tests now include a **first-order test with p ≠ 0** (a hypergeometric equation in
   non-reduced form, with exact local monodromy). Rust and Python v2 enclosures must each **contain the exact
   value**, and must overlap each other.
2. **V-controls:**
   - ZV δ=2 equatorial (must find) and axial (info);
   - Kerr equatorial and axial at all levels (must not find);
   - on the **same** v2 pipeline.
3. **V-reproduce:** the **already proven axial MN certificates** (2ce8b41) must come out again. Overlapping balls
   with v1 are fine; a different certifying pair is also fine, provided it is replayed by v1.
4. **V-Lean:** L1–L7 checked by Lean, with no `sorry`.

Only then: the MN equatorial target, all 6 rows at the registered levels, under the two-implementation rule.

## 7. Open questions for review

- **Scope of v2's first target:** MN equatorial only, or also re-certify TS δ=2 by this independent route?
- **Who replays:** keep v1 as the replay engine (most independent), or also add a Python v2 for a three-way check?
- **The L6 boundary:** how much of the algebraic-group step to formalise versus cite. The proposal is to cite
  the classification and formalise everything around it.
