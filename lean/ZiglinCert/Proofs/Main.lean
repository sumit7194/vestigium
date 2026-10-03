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

/-- L1 (direction used): a common eigenvector of `g, h` with `det = 1` forces `tr (g h g⁻¹ h⁻¹) = 2`. -/
theorem L1_common_eigvec_comm_trace (g h : M2) (hg : g.det = 1) (hh : h.det = 1) (v : Fin 2 → ℂ)
    (hv : IsEigvec g v) (hw : IsEigvec h v) : (g * h * g⁻¹ * h⁻¹).trace = 2 := by
  obtain ⟨hv0, α, hα⟩ := hv
  obtain ⟨-, β, hβ⟩ := hw
  have hgu : IsUnit g.det := by rw [hg]; exact isUnit_one
  have hhu : IsUnit h.det := by rw [hh]; exact isUnit_one
  have hα0 : α ≠ 0 := by
    intro h0; rw [h0, zero_smul] at hα
    exact hv0 ((Matrix.mulVec_injective_iff_isUnit.mpr ((Matrix.isUnit_iff_isUnit_det g).mpr hgu)) (by rw [hα, Matrix.mulVec_zero]))
  have hβ0 : β ≠ 0 := by
    intro h0; rw [h0, zero_smul] at hβ
    exact hv0 ((Matrix.mulVec_injective_iff_isUnit.mpr ((Matrix.isUnit_iff_isUnit_det h).mpr hhu)) (by rw [hβ, Matrix.mulVec_zero]))
  have hgi : g⁻¹.mulVec v = α⁻¹ • v := by
    have : g⁻¹.mulVec (g.mulVec v) = v := by
      rw [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul g hgu, Matrix.one_mulVec]
    rw [hα, Matrix.mulVec_smul] at this
    calc g⁻¹.mulVec v = α⁻¹ • (α • g⁻¹.mulVec v) := by rw [smul_smul, inv_mul_cancel₀ hα0, one_smul]
      _ = α⁻¹ • v := by rw [this]
  have hhi : h⁻¹.mulVec v = β⁻¹ • v := by
    have : h⁻¹.mulVec (h.mulVec v) = v := by
      rw [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul h hhu, Matrix.one_mulVec]
    rw [hβ, Matrix.mulVec_smul] at this
    calc h⁻¹.mulVec v = β⁻¹ • (β • h⁻¹.mulVec v) := by rw [smul_smul, inv_mul_cancel₀ hβ0, one_smul]
      _ = β⁻¹ • v := by rw [this]
  set c := g * h * g⁻¹ * h⁻¹ with hc
  have hcv : c.mulVec v = v := by
    simp only [hc, ← Matrix.mulVec_mulVec, hhi, Matrix.mulVec_smul, hgi, hβ, hα, smul_smul]
    rw [show β⁻¹ * (α⁻¹ * (β * α)) = 1 by field_simp, one_smul]
  have hcdet : c.det = 1 := by
    simp only [hc, Matrix.det_mul, Matrix.det_nonsing_inv, hg, hh]; norm_num
  have hsing : (c - (1 : ℂ) • (1 : M2)).det = 0 := by
    apply Matrix.exists_mulVec_eq_zero_iff.mp
    exact ⟨v, hv0, by rw [Matrix.sub_mulVec, one_smul, Matrix.one_mulVec, hcv, sub_self]⟩
  rw [det_sub_smul_one, hcdet] at hsing
  linear_combination -hsing

lemma pow_mulVec_eig (A : M2) (v : Fin 2 → ℂ) (μ : ℂ) (h : A.mulVec v = μ • v) (n : ℕ) :
    (A ^ n).mulVec v = μ ^ n • v := by
  induction n with
  | zero => simp
  | succ n ih => rw [pow_succ, ← Matrix.mulVec_mulVec, h, Matrix.mulVec_smul, ih, smul_smul, pow_succ, mul_comm]

/-- For a loxodromic eigenvalue, distinct powers stay distinct: `μ^n ≠ μ⁻¹^n` for `n ≥ 1`. -/
lemma pow_ne_inv_pow (μ : ℂ) (hμ0 : μ ≠ 0) (hn1 : ‖μ‖ ≠ 1) (n : ℕ) (hn : 0 < n) : μ ^ n ≠ μ⁻¹ ^ n := by
  intro he
  have hsq : μ ^ n * μ ^ n = 1 := by
    nth_rewrite 2 [he]; rw [← mul_pow, mul_inv_cancel₀ hμ0, one_pow]
  have hnorm : ‖μ‖ ^ (n + n) = 1 := by rw [pow_add, ← norm_pow, ← norm_mul, hsq, norm_one]
  exact hn1 ((pow_eq_one_iff_of_nonneg (norm_nonneg μ) (by omega)).mp hnorm)

/-- **L6.** Loxodromic `g, h ∈ SL(2, ℂ)` with `tr[g, h] ≠ 2`: for every `k ≥ 1`, no finite-index subgroup of
`⟨g^k, h^k⟩` is abelian. (`k = 2` is the lift to the phase curve; `k = 1` the x-plane group.) -/
theorem L6_not_virtually_abelian (g h : Matrix.SpecialLinearGroup (Fin 2) ℂ)
    (hg : IsLoxodromic (g : M2)) (hh : IsLoxodromic (h : M2))
    (hc : ((g : M2) * h * (g : M2)⁻¹ * (h : M2)⁻¹).trace ≠ 2) (k : ℕ) (hk : 0 < k)
    (A : Subgroup (Matrix.SpecialLinearGroup (Fin 2) ℂ))
    (hA : A.relIndex (Subgroup.closure {g ^ k, h ^ k}) ≠ 0) :
    ¬ (∀ a ∈ A, ∀ b ∈ A, a * b = b * a) := by
  intro hcomm
  obtain ⟨m, hm0, -, hgm⟩ := Subgroup.exists_pow_mem_of_relIndex_ne_zero hA
    (Subgroup.subset_closure (Set.mem_insert _ _))
  obtain ⟨n, hn0, -, hhn⟩ := Subgroup.exists_pow_mem_of_relIndex_ne_zero hA
    (Subgroup.subset_closure (Set.mem_insert_of_mem _ (Set.mem_singleton _)))
  have hGH := hcomm _ (Subgroup.mem_inf.mp hgm).1 _ (Subgroup.mem_inf.mp hhn).1
  -- as matrices
  have hdetg : (g : M2).det = 1 := g.2
  have hdeth : (h : M2).det = 1 := h.2
  have hGHm : ((g : M2) ^ (k * m)) * ((h : M2) ^ (k * n)) = ((h : M2) ^ (k * n)) * ((g : M2) ^ (k * m)) := by
    have := congrArg (fun x : Matrix.SpecialLinearGroup (Fin 2) ℂ => (x : M2)) hGH
    simpa [Matrix.SpecialLinearGroup.coe_mul, Matrix.SpecialLinearGroup.coe_pow, pow_mul] using this
  obtain ⟨μ, u₁, u₂, hμ0, hμ1, hu₁, hu₂, e₁, e₂, hd⟩ := lox_eigenbasis (g : M2) hdetg hg
  obtain ⟨ν, w₁, w₂, hν0, hν1, hw₁, hw₂, f₁, f₂, hd'⟩ := lox_eigenbasis (h : M2) hdeth hh
  have hkm : 0 < k * m := Nat.mul_pos hk hm0
  have hkn : 0 < k * n := Nat.mul_pos hk hn0
  have hHdet : IsUnit ((h : M2) ^ (k * n)).det := by rw [Matrix.det_pow, hdeth, one_pow]; exact isUnit_one
  -- u₁ is an eigenvector of h^(kn)
  obtain ⟨-, c, hc'⟩ := commute_eigvec ((g : M2) ^ (k * m)) ((h : M2) ^ (k * n)) hGHm hHdet u₁ u₂
    (μ ^ (k * m)) (μ⁻¹ ^ (k * m)) (pow_ne_inv_pow μ hμ0 hμ1 _ hkm) hd hu₁
    (pow_mulVec_eig _ _ _ e₁ _) (pow_mulVec_eig _ _ _ e₂ _)
  -- hence u₁ lies along w₁ or w₂, so it is an eigenvector of h
  have hu_h : IsEigvec (h : M2) u₁ := by
    rcases eig_in_basis ((h : M2) ^ (k * n)) w₁ w₂ u₁ (ν ^ (k * n)) (ν⁻¹ ^ (k * n)) c
        (pow_ne_inv_pow ν hν0 hν1 _ hkn) hd' (pow_mulVec_eig _ _ _ f₁ _) (pow_mulVec_eig _ _ _ f₂ _) hc'
      with ⟨d, hdw⟩ | ⟨d, hdw⟩
    · exact ⟨hu₁, ν, by rw [hdw, Matrix.mulVec_smul, f₁, smul_comm]⟩
    · exact ⟨hu₁, ν⁻¹, by rw [hdw, Matrix.mulVec_smul, f₂, smul_comm]⟩
  exact hc (L1_common_eigvec_comm_trace (g : M2) (h : M2) hdetg hdeth u₁ ⟨hu₁, μ, e₁⟩ hu_h)

#print axioms L6_not_virtually_abelian
#print axioms L1_common_eigvec_comm_trace
