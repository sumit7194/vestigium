import Mathlib
open Matrix Complex

abbrev M2 := Matrix (Fin 2) (Fin 2) ℂ
def IsEigvec (g : M2) (v : Fin 2 → ℂ) : Prop := v ≠ 0 ∧ ∃ μ : ℂ, g.mulVec v = μ • v
def IsLoxodromic (g : M2) : Prop := ¬ (g.trace.im = 0 ∧ -2 ≤ g.trace.re ∧ g.trace.re ≤ 2)
/-- 2×2 determinant of two column vectors. -/
def D2 (u w : Fin 2 → ℂ) : ℂ := u 0 * w 1 - u 1 * w 0

lemma det_sub_smul_one (A : M2) (μ : ℂ) : (A - μ • (1 : M2)).det = μ ^ 2 - A.trace * μ + A.det := by
  simp [Matrix.det_fin_two, Matrix.trace_fin_two]; ring

lemma exists_eigvec_of_root (A : M2) (μ : ℂ) (h : μ ^ 2 - A.trace * μ + A.det = 0) :
    ∃ v : Fin 2 → ℂ, v ≠ 0 ∧ A.mulVec v = μ • v := by
  have hd : (A - μ • (1 : M2)).det = 0 := by rw [det_sub_smul_one, h]
  obtain ⟨v, hv0, hv⟩ := Matrix.exists_mulVec_eq_zero_iff.mpr hd
  refine ⟨v, hv0, ?_⟩
  rw [Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec, sub_eq_zero] at hv
  exact hv

/-- `D2 u w = 0` with `u ≠ 0` makes `w` a multiple of `u`. -/
lemma par_of_D2 (u w : Fin 2 → ℂ) (hu : u ≠ 0) (hd : D2 u w = 0) : ∃ c : ℂ, w = c • u := by
  unfold D2 at hd
  by_cases h0 : u 0 = 0
  · have h1 : u 1 ≠ 0 := by
      intro h1; apply hu; ext k; fin_cases k
      · exact h0
      · exact h1
    have hw0 : w 0 = 0 := by
      have : u 1 * w 0 = 0 := by rw [h0] at hd; linear_combination -hd
      exact (mul_eq_zero.mp this).resolve_left h1
    refine ⟨w 1 / u 1, ?_⟩
    ext k; fin_cases k
    · show w 0 = w 1 / u 1 * u 0
      rw [h0, hw0, mul_zero]
    · show w 1 = w 1 / u 1 * u 1
      field_simp
  · refine ⟨w 0 / u 0, ?_⟩
    ext k; fin_cases k
    · show w 0 = w 0 / u 0 * u 0
      field_simp
    · show w 1 = w 0 / u 0 * u 1
      field_simp
      linear_combination hd

/-- Independence: `a u + b w = 0` with `D2 u w ≠ 0` forces `a = b = 0`. -/
lemma indep_of_D2 (u w : Fin 2 → ℂ) (hd : D2 u w ≠ 0) (a b : ℂ) (h : a • u + b • w = 0) :
    a = 0 ∧ b = 0 := by
  have e0 : a * u 0 + b * w 0 = 0 := by simpa using congrFun h 0
  have e1 : a * u 1 + b * w 1 = 0 := by simpa using congrFun h 1
  unfold D2 at hd
  constructor
  · have : a * (u 0 * w 1 - u 1 * w 0) = 0 := by linear_combination w 1 * e0 - w 0 * e1
    exact (mul_eq_zero.mp this).resolve_right hd
  · have : b * (u 0 * w 1 - u 1 * w 0) = 0 := by linear_combination -(u 1) * e0 + u 0 * e1
    exact (mul_eq_zero.mp this).resolve_right hd

/-- A unit-modulus nonzero `μ` has `μ + μ⁻¹` in the real segment `[-2, 2]`. -/
lemma seg_of_norm_one (μ : ℂ) (h1 : ‖μ‖ = 1) :
    (μ + μ⁻¹).im = 0 ∧ -2 ≤ (μ + μ⁻¹).re ∧ (μ + μ⁻¹).re ≤ 2 := by
  have hn : Complex.normSq μ = 1 := by rw [Complex.normSq_eq_norm_sq, h1]; norm_num
  have hre := Complex.abs_re_le_norm μ
  rw [h1] at hre
  refine ⟨?_, ?_, ?_⟩
  · simp [Complex.inv_im, hn]
  · simp only [Complex.add_re, Complex.inv_re, hn, div_one]; linarith [(abs_le.mp hre).1]
  · simp only [Complex.add_re, Complex.inv_re, hn, div_one]; linarith [(abs_le.mp hre).2]

/-- A loxodromic element of SL(2, ℂ) has an eigenbasis `u₁, u₂` with eigenvalues `μ, μ⁻¹`, `‖μ‖ ≠ 1`. -/
theorem lox_eigenbasis (g : M2) (hg : g.det = 1) (hl : IsLoxodromic g) :
    ∃ μ : ℂ, ∃ u₁ u₂ : Fin 2 → ℂ, μ ≠ 0 ∧ ‖μ‖ ≠ 1 ∧ u₁ ≠ 0 ∧ u₂ ≠ 0 ∧
      g.mulVec u₁ = μ • u₁ ∧ g.mulVec u₂ = μ⁻¹ • u₂ ∧ D2 u₁ u₂ ≠ 0 := by
  obtain ⟨s, hs⟩ := IsAlgClosed.exists_pow_nat_eq (g.trace ^ 2 - 4) (by norm_num : 0 < 2)
  set μ := (g.trace + s) / 2 with hμ
  set ν := (g.trace - s) / 2 with hν
  have hμν : μ * ν = 1 := by rw [hμ, hν]; linear_combination (-1/4 : ℂ) * hs
  have hμ0 : μ ≠ 0 := left_ne_zero_of_mul_eq_one hμν
  have hνinv : ν = μ⁻¹ := eq_inv_of_mul_eq_one_right hμν
  have htr : g.trace = μ + μ⁻¹ := by rw [← hνinv, hμ, hν]; ring
  have hnorm : ‖μ‖ ≠ 1 := by
    intro h1; apply hl; rw [htr]; exact seg_of_norm_one μ h1
  have rμ : μ ^ 2 - g.trace * μ + g.det = 0 := by
    rw [hg, htr]; field_simp; ring
  have rν : μ⁻¹ ^ 2 - g.trace * μ⁻¹ + g.det = 0 := by
    rw [hg, htr]; field_simp; ring
  obtain ⟨u₁, hu₁, h₁⟩ := exists_eigvec_of_root g μ rμ
  obtain ⟨u₂, hu₂, h₂⟩ := exists_eigvec_of_root g μ⁻¹ rν
  refine ⟨μ, u₁, u₂, hμ0, hnorm, hu₁, hu₂, h₁, h₂, ?_⟩
  intro hd
  obtain ⟨c, hc⟩ := par_of_D2 u₁ u₂ hu₁ hd
  -- then u₂ is a μ-eigenvector as well as a μ⁻¹-eigenvector
  have : (μ - μ⁻¹) • u₂ = 0 := by
    have e : g.mulVec u₂ = μ • u₂ := by rw [hc, Matrix.mulVec_smul, h₁, smul_comm]
    rw [sub_smul, ← e, ← h₂, sub_self]
  rcases smul_eq_zero.mp this with h | h
  · have hsq : μ ^ 2 = 1 := by
      have : μ = μ⁻¹ := sub_eq_zero.mp h
      field_simp at this; linear_combination this
    apply hnorm
    have : ‖μ‖ ^ 2 = 1 := by rw [← norm_pow, hsq, norm_one]
    nlinarith [norm_nonneg μ, sq_nonneg (‖μ‖ - 1)]
  · exact hu₂ h

/-- In an eigenbasis with distinct eigenvalues, every eigenvector lies along a basis vector. -/
theorem eig_in_basis (a : M2) (u₁ u₂ v : Fin 2 → ℂ) (l₁ l₂ l : ℂ) (hne : l₁ ≠ l₂) (hd : D2 u₁ u₂ ≠ 0)
    (h₁ : a.mulVec u₁ = l₁ • u₁) (h₂ : a.mulVec u₂ = l₂ • u₂) (hv : a.mulVec v = l • v) :
    (∃ c : ℂ, v = c • u₁) ∨ (∃ c : ℂ, v = c • u₂) := by
  -- coordinates of v in the basis (Cramer)
  set c₁ := D2 v u₂ / D2 u₁ u₂
  set c₂ := D2 u₁ v / D2 u₁ u₂
  have hdec : v = c₁ • u₁ + c₂ • u₂ := by
    ext k
    have key : D2 u₁ u₂ * v k = D2 v u₂ * u₁ k + D2 u₁ v * u₂ k := by
      fin_cases k <;> simp [D2] <;> ring
    show v k = c₁ * u₁ k + c₂ * u₂ k
    simp only [c₁, c₂]
    field_simp
    linear_combination key
  have key : (c₁ * (l₁ - l)) • u₁ + (c₂ * (l₂ - l)) • u₂ = 0 := by
    have e := hv
    rw [hdec, Matrix.mulVec_add, Matrix.mulVec_smul, Matrix.mulVec_smul, h₁, h₂] at e
    linear_combination (norm := module) e
  obtain ⟨k1, k2⟩ := indep_of_D2 u₁ u₂ hd _ _ key
  by_cases hc1 : c₁ = 0
  · right; exact ⟨c₂, by rw [hdec, hc1, zero_smul, zero_add]⟩
  · have hl : l = l₁ := (sub_eq_zero.mp ((mul_eq_zero.mp k1).resolve_left hc1)).symm
    have hc2 : c₂ = 0 := by
      rcases mul_eq_zero.mp k2 with h | h
      · exact h
      · exfalso; apply hne; rw [hl] at h; exact (sub_eq_zero.mp h).symm
    left; exact ⟨c₁, by rw [hdec, hc2, zero_smul, add_zero]⟩

/-- If `b` commutes with `a` (eigenbasis, distinct eigenvalues) and `b` is invertible, then `u₁` is an
eigenvector of `b`. -/
theorem commute_eigvec (a b : M2) (hab : a * b = b * a) (hb : IsUnit b.det) (u₁ u₂ : Fin 2 → ℂ)
    (l₁ l₂ : ℂ) (hne : l₁ ≠ l₂) (hd : D2 u₁ u₂ ≠ 0) (hu₁ : u₁ ≠ 0)
    (h₁ : a.mulVec u₁ = l₁ • u₁) (h₂ : a.mulVec u₂ = l₂ • u₂) : IsEigvec b u₁ := by
  have hbu : b.mulVec u₁ ≠ 0 := by
    intro h0
    exact hu₁ ((Matrix.mulVec_injective_iff_isUnit.mpr ((Matrix.isUnit_iff_isUnit_det b).mpr hb))
      (by rw [h0, Matrix.mulVec_zero]))
  have hab' : a.mulVec (b.mulVec u₁) = l₁ • b.mulVec u₁ := by
    rw [Matrix.mulVec_mulVec, hab, ← Matrix.mulVec_mulVec, h₁, Matrix.mulVec_smul]
  rcases eig_in_basis a u₁ u₂ (b.mulVec u₁) l₁ l₂ l₁ hne hd h₁ h₂ hab' with ⟨c, hc⟩ | ⟨c, hc⟩
  · exact ⟨hu₁, c, hc⟩
  · exfalso
    have e2 : a.mulVec (b.mulVec u₁) = l₂ • b.mulVec u₁ := by
      rw [hc, Matrix.mulVec_smul, h₂, smul_comm]
    have : (l₁ - l₂) • b.mulVec u₁ = 0 := by rw [sub_smul, ← hab', ← e2, sub_self]
    rcases smul_eq_zero.mp this with h | h
    · exact hne (sub_eq_zero.mp h)
    · exact hbu h
