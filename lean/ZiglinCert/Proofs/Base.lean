import Mathlib
open Matrix

abbrev M2 := Matrix (Fin 2) (Fin 2) ℂ

def IsEigvec (g : M2) (v : Fin 2 → ℂ) : Prop := v ≠ 0 ∧ ∃ μ : ℂ, g.mulVec v = μ • v

/-- 2×2: `det (A - μ•1) = μ² - tr A · μ + det A`. -/
lemma det_sub_smul_one (A : M2) (μ : ℂ) : (A - μ • (1 : M2)).det = μ ^ 2 - A.trace * μ + A.det := by
  simp [Matrix.det_fin_two, Matrix.trace_fin_two]
  ring

/-- A root of the characteristic polynomial has an eigenvector. -/
lemma exists_eigvec_of_root (A : M2) (μ : ℂ) (h : μ ^ 2 - A.trace * μ + A.det = 0) :
    ∃ v : Fin 2 → ℂ, v ≠ 0 ∧ A.mulVec v = μ • v := by
  have hd : (A - μ • (1 : M2)).det = 0 := by rw [det_sub_smul_one, h]
  obtain ⟨v, hv0, hv⟩ := Matrix.exists_mulVec_eq_zero_iff.mpr hd
  refine ⟨v, hv0, ?_⟩
  rw [Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec, sub_eq_zero] at hv
  exact hv

/-- L1 (direction used): a common eigenvector of `g, h ∈ SL(2)` forces `tr (g h g⁻¹ h⁻¹) = 2`. -/
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
  -- g⁻¹ v = α⁻¹ v and h⁻¹ v = β⁻¹ v
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
  -- 1 is a root of the characteristic polynomial: det (c - 1) = 0
  have hsing : (c - (1 : ℂ) • (1 : M2)).det = 0 := by
    apply Matrix.exists_mulVec_eq_zero_iff.mp
    exact ⟨v, hv0, by rw [Matrix.sub_mulVec, one_smul, Matrix.one_mulVec, hcv, sub_self]⟩
  rw [det_sub_smul_one, hcdet] at hsing
  linear_combination -hsing
