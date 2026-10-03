import Mathlib
open Matrix

def IsEigvec (g : Matrix (Fin 2) (Fin 2) ℂ) (v : Fin 2 → ℂ) : Prop :=
  v ≠ 0 ∧ ∃ μ : ℂ, g.mulVec v = μ • v

/-- An eigenvector of `1 + N` with `N² = 0` lies in `ker N`. -/
lemma eig_of_unipotent_ker (N : Matrix (Fin 2) (Fin 2) ℂ) (hN2 : N * N = 0) (v : Fin 2 → ℂ)
    (hv : IsEigvec (1 + N) v) : N.mulVec v = 0 := by
  obtain ⟨hv0, μ, hμ⟩ := hv
  have h1 : N.mulVec v = (μ - 1) • v := by
    rw [Matrix.add_mulVec, Matrix.one_mulVec] at hμ
    rw [sub_smul, one_smul, ← hμ]; abel
  have h2 : N.mulVec (N.mulVec v) = 0 := by
    rw [Matrix.mulVec_mulVec, hN2, Matrix.zero_mulVec]
  rw [h1, Matrix.mulVec_smul, h1, smul_smul] at h2
  rcases smul_eq_zero.mp h2 with h | h
  · have : μ - 1 = 0 := mul_self_eq_zero.mp h
    rw [h1, this, zero_smul]
  · exact absurd h hv0

theorem L7_unipotent_one_eigenline (N : Matrix (Fin 2) (Fin 2) ℂ) (hN : N ≠ 0) (hN2 : N * N = 0)
    (v w : Fin 2 → ℂ) (hv : IsEigvec (1 + N) v) (hw : IsEigvec (1 + N) w) :
    ∃ c : ℂ, w = c • v := by
  have kv := eig_of_unipotent_ker N hN2 v hv
  have kw := eig_of_unipotent_ker N hN2 w hw
  have hv0 := hv.1
  -- a nonzero entry gives a nonzero row (a, b) annihilating both v and w
  obtain ⟨i, j, hij⟩ : ∃ i j, N i j ≠ 0 := by
    by_contra hcon
    push Not at hcon
    exact hN (Matrix.ext hcon)
  have rv : N i 0 * v 0 + N i 1 * v 1 = 0 := by
    have := congrFun kv i
    simpa [Matrix.mulVec, dotProduct, Fin.sum_univ_two] using this
  have rw' : N i 0 * w 0 + N i 1 * w 1 = 0 := by
    have := congrFun kw i
    simpa [Matrix.mulVec, dotProduct, Fin.sum_univ_two] using this
  -- the 2x2 determinant of (v, w) vanishes
  have hdet : v 0 * w 1 - v 1 * w 0 = 0 := by
    have ha : N i 0 * (v 0 * w 1 - v 1 * w 0) = 0 := by linear_combination w 1 * rv - v 1 * rw'
    have hb : N i 1 * (v 0 * w 1 - v 1 * w 0) = 0 := by linear_combination -(w 0) * rv + v 0 * rw'
    fin_cases j
    · exact (mul_eq_zero.mp ha).resolve_left hij
    · exact (mul_eq_zero.mp hb).resolve_left hij
  by_cases h0 : v 0 = 0
  · have h1 : v 1 ≠ 0 := by
      intro h1; apply hv0; ext k; fin_cases k
      · exact h0
      · exact h1
    have hw0 : w 0 = 0 := by
      have : v 1 * w 0 = 0 := by rw [h0] at hdet; linear_combination -hdet
      exact (mul_eq_zero.mp this).resolve_left h1
    refine ⟨w 1 / v 1, ?_⟩
    ext k; fin_cases k
    · show w 0 = w 1 / v 1 * v 0
      rw [h0, hw0, mul_zero]
    · show w 1 = w 1 / v 1 * v 1
      field_simp
  · refine ⟨w 0 / v 0, ?_⟩
    ext k; fin_cases k
    · show w 0 = w 0 / v 0 * v 0
      field_simp
    · show w 1 = w 0 / v 0 * v 1
      field_simp
      linear_combination hdet
