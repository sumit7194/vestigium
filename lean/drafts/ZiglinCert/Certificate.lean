/-
  ZiglinCert.Certificate — the GLUE LEMMAS of the certified-monodromy obstruction route
  (PREREG_iahub_v2.md §5, L1–L7).

  STATUS: DRAFT. These are statements with proof plans; the proofs are `sorry` until Mathlib is installed and
  each one is completed AGAINST THE COMPILER. Nothing here is "checked" until `lake build` passes with no `sorry`
  (rung V-Lean).

  What is formalised: every step between "two certified monodromy matrices g, h" and "the monodromy group is not
  virtually abelian". What stays CITED (not formalised): the Ziglin / Morales–Ramis theorem (meromorphic
  integrability ⇒ G⁰ abelian), and the elementary fact that G⁰ has finite index in G.

  Conventions: 2×2 complex matrices `Matrix (Fin 2) (Fin 2) ℂ`; the SL(2) statements take `det = 1` as a
  hypothesis; "certainly" ball statements live in the Rust/Arb code, not here — here the inputs are exact numbers.
-/
import Mathlib

open Matrix Complex

namespace ZiglinCert

/-- Membership of a complex number in the real segment `[a, b] ⊂ ℝ ⊂ ℂ`. -/
def InRealSegment (z : ℂ) (a b : ℝ) : Prop := z.im = 0 ∧ a ≤ z.re ∧ z.re ≤ b

/-- `v` is an eigenvector of `g` (nonzero, `g v = μ v` for some `μ`). -/
def IsEigvec (g : Matrix (Fin 2) (Fin 2) ℂ) (v : Fin 2 → ℂ) : Prop :=
  v ≠ 0 ∧ ∃ μ : ℂ, g.mulVec v = μ • v

/-- Loxodromic in SL(2): trace outside the real segment `[-2, 2]`. -/
def IsLoxodromic (g : Matrix (Fin 2) (Fin 2) ℂ) : Prop := ¬ InRealSegment g.trace (-2) 2

/-- The commutator `g h g⁻¹ h⁻¹` (for `det = 1` the inverse is the adjugate). -/
noncomputable def comm (g h : Matrix (Fin 2) (Fin 2) ℂ) : Matrix (Fin 2) (Fin 2) ℂ :=
  g * h * g⁻¹ * h⁻¹

/-! ### L1. `tr[g,h] = 2` ⇔ common eigenvector (SL(2, ℂ)).
Plan: Fricke identity `tr[g,h] = tr g² + tr h² + tr(gh)² − tr g·tr h·tr(gh) − 2`, and the classical
equivalence "the pair is reducible ⇔ tr[g,h] = 2". (⇐) conjugate to upper-triangular: the commutator is
unipotent upper-triangular, trace 2. (⇒) if tr[g,h] = 2 then [g,h] is ±I-free unipotent or I; in either case
a fixed vector of [g,h] (or of g when [g,h] = I and g is not scalar) is a common eigenvector — case analysis
on whether g is scalar. -/
theorem L1_comm_trace_two_iff (g h : Matrix (Fin 2) (Fin 2) ℂ) (hg : g.det = 1) (hh : h.det = 1) :
    (comm g h).trace = 2 ↔ ∃ v, IsEigvec g v ∧ IsEigvec h v := by
  sorry

/-! ### L2. Loxodromic ⇒ two distinct eigenvalues `μ, μ⁻¹` with `‖μ‖ ≠ 1`; hence infinite order and exactly
two eigenlines. Plan: eigenvalues are the roots of `X² − tr·X + 1`; if `|μ| = 1` then `tr = μ + μ̄ = 2 Re μ`
is real in `[−2, 2]`. Distinctness: `μ = μ⁻¹` forces `μ = ±1`, `tr = ±2`. -/
theorem L2_loxodromic_eigen (g : Matrix (Fin 2) (Fin 2) ℂ) (hg : g.det = 1) (hl : IsLoxodromic g) :
    ∃ μ : ℂ, μ ≠ 0 ∧ ‖μ‖ ≠ 1 ∧ μ ≠ μ⁻¹ ∧ g.trace = μ + μ⁻¹ := by
  sorry

theorem L2_loxodromic_infinite_order (g : Matrix (Fin 2) (Fin 2) ℂ) (hg : g.det = 1)
    (hl : IsLoxodromic g) : ∀ n : ℕ, 0 < n → g ^ n ≠ 1 := by
  sorry

/-! ### L3. In SL(2), elements of `N(T) \ T` (anti-diagonal) have trace 0. Immediate from the shape. -/
theorem L3_antidiag_trace_zero (b c : ℂ) :
    (!![0, b; c, 0] : Matrix (Fin 2) (Fin 2) ℂ).trace = 0 := by
  simp [Matrix.trace_fin_two]

/-! ### L4. Invariances. (a) scalars: `tr[λg, κh] = tr[g,h]`; eigenvectors unchanged. (b) squaring: for a
loxodromic `g`, `g²` is loxodromic with the same eigenvectors. Plan: (a) scalars commute and cancel in the
commutator; (b) `μ²` still has `‖μ²‖ ≠ 1`, distinct from `μ⁻²`. -/
theorem L4a_comm_scalar (g h : Matrix (Fin 2) (Fin 2) ℂ) (l k : ℂ) (hl : l ≠ 0) (hk : k ≠ 0)
    (hg : IsUnit g.det) (hh : IsUnit h.det) :
    comm (l • g) (k • h) = comm g h := by
  sorry

theorem L4b_sq_loxodromic (g : Matrix (Fin 2) (Fin 2) ℂ) (hg : g.det = 1) (hl : IsLoxodromic g) :
    IsLoxodromic (g ^ 2) := by
  sorry

/-! ### L5. GL(2) restatement (non-reduced system, `det ≠ 1`): for `s² = det g`, the normalised trace
`tr g / s ∉ [−2, 2]` ⇔ `tr(g)² / det g ∉ [0, 4]`. Plan: `(tr/s)² = tr²/det`; for `x : ℂ`,
`x ∈ [−2,2] ⇔ x² ∈ [0,4]` (if `x² ≥ 0` real then `x` real; `x² ≤ 4 ⇔ |x| ≤ 2`). -/
theorem L5_gl2_restatement (g : Matrix (Fin 2) (Fin 2) ℂ) (s : ℂ) (hs : s ^ 2 = g.det) (hs0 : s ≠ 0) :
    InRealSegment (g.trace / s) (-2) 2 ↔ InRealSegment (g.trace ^ 2 / g.det) 0 4 := by
  sorry

/-! ### L6. The group-theoretic core (bridge's argument, no classification needed).
If `g, h ∈ SL(2, ℂ)` are loxodromic and `tr[g,h] ≠ 2`, then no finite-index subgroup of `⟨g, h⟩` is abelian.
Plan: a finite-index subgroup `A` contains `g^m, h^m` for some `m ≥ 1` (pigeonhole on cosets). `g^m, h^m` commute
⇒ (loxodromic, distinct eigenvalues) they share both eigenlines; eigenlines of `g^m` are those of `g` (L2/L4b)
⇒ `g, h` share an eigenvector ⇒ `tr[g,h] = 2` (L1), contradiction. -/
theorem L6_not_virtually_abelian
    (g h : Matrix.SpecialLinearGroup (Fin 2) ℂ)
    (hg : IsLoxodromic (g : Matrix (Fin 2) (Fin 2) ℂ)) (hh : IsLoxodromic (h : Matrix (Fin 2) (Fin 2) ℂ))
    (hc : (comm (g : Matrix (Fin 2) (Fin 2) ℂ) h).trace ≠ 2) :
    ∀ A : Subgroup (Matrix.SpecialLinearGroup (Fin 2) ℂ),
      A ≤ Subgroup.closure {g, h} → A.FiniteIndex' (Subgroup.closure {g, h}) →
      ¬ (∀ a ∈ A, ∀ b ∈ A, a * b = b * a) := by
  sorry
  -- NOTE: `FiniteIndex'` is a placeholder for "A has finite index in the closure"; to be replaced by Mathlib's
  -- `(A.subgroupOf (Subgroup.closure {g, h})).FiniteIndex` once the exact API is checked against the compiler.

/-! ### L7 (TS route). `±(unipotent ≠ I)` has exactly one eigenline: if `u = ±(I + N)` with `N ≠ 0`, `N² = 0`,
then any two eigenvectors of `u` are parallel. Plan: eigenvectors of `u` are the kernel of `N`, which is
one-dimensional since `N ≠ 0` and `N² = 0` in dimension 2. -/
theorem L7_unipotent_one_eigenline (N : Matrix (Fin 2) (Fin 2) ℂ) (hN : N ≠ 0) (hN2 : N * N = 0)
    (v w : Fin 2 → ℂ) (hv : IsEigvec (1 + N) v) (hw : IsEigvec (1 + N) w) :
    ∃ c : ℂ, w = c • v := by
  sorry

end ZiglinCert
