/-
  ZiglinCert.Boxes — Lean-verified certificate ARITHMETIC (PREREG_lean_certificate_arithmetic.md, 344400c).

  Exact rational boxes for 2×2 complex matrices, interval operations with soundness proofs, and a Boolean
  `check` deciding the division-free certificate criteria. `cert_sound`: if `check BG BH = true`, then EVERY pair
  of matrices G ∈ BG, H ∈ BH is invertible and satisfies the conclusion of `L6_gl2`.

  Criteria (bridge-endorsed, division-free):
    (I)  for each of G, H, with w = tr²·conj(det):  w.im ≠ 0  ∨  w.re < 0  ∨  w.re > 4|det|²
         (each disjunct forces det ≠ 0; together ⇔ tr²/det ∉ [0,4])                     — `crit1_math`
    (II) tr(G·H·adj G·adj H) − 2·det G·det H ≠ 0   (⇔ tr[G,H] ≠ 2 when both dets ≠ 0)  — `crit2_math`
  Decided by the kernel (`decide +kernel`); no `native_decide`, no `sorry`.
-/
import ZiglinCert.Certificate
open Matrix Complex

/-! ### Rational intervals -/

structure QI where
  lo : ℚ
  hi : ℚ

namespace QI

def mem (I : QI) (x : ℝ) : Prop := ((I.lo : ℚ) : ℝ) ≤ x ∧ x ≤ ((I.hi : ℚ) : ℝ)

def pt (c : ℚ) : QI := ⟨c, c⟩
def add (A B : QI) : QI := ⟨A.lo + B.lo, A.hi + B.hi⟩
def neg (A : QI) : QI := ⟨-A.hi, -A.lo⟩
def sub (A B : QI) : QI := add A (neg B)
def mul (A B : QI) : QI :=
  ⟨min (min (A.lo * B.lo) (A.lo * B.hi)) (min (A.hi * B.lo) (A.hi * B.hi)),
   max (max (A.lo * B.lo) (A.lo * B.hi)) (max (A.hi * B.lo) (A.hi * B.hi))⟩

/-- the interval certainly excludes 0 -/
def excl0 (I : QI) : Bool := decide (0 < I.lo) || decide (I.hi < 0)

theorem mem_pt (c : ℚ) : (pt c).mem (c : ℝ) := ⟨le_rfl, le_rfl⟩

theorem mem_add {A B : QI} {x y : ℝ} (hx : A.mem x) (hy : B.mem y) : (add A B).mem (x + y) := by
  obtain ⟨h1, h2⟩ := hx; obtain ⟨h3, h4⟩ := hy
  simp only [mem, add, Rat.cast_add]; constructor <;> linarith

theorem mem_neg {A : QI} {x : ℝ} (hx : A.mem x) : (neg A).mem (-x) := by
  obtain ⟨h1, h2⟩ := hx
  simp only [mem, neg, Rat.cast_neg]; constructor <;> linarith

theorem mem_sub {A B : QI} {x y : ℝ} (hx : A.mem x) (hy : B.mem y) : (sub A B).mem (x - y) := by
  rw [sub_eq_add_neg]; exact mem_add hx (mem_neg hy)

/-- one variable: x ∈ [a,b] ⇒ x·y lies between a·y and b·y -/
theorem lin1 {a b x : ℝ} (y : ℝ) (h1 : a ≤ x) (h2 : x ≤ b) :
    min (a * y) (b * y) ≤ x * y ∧ x * y ≤ max (a * y) (b * y) := by
  rcases le_total 0 y with hy | hy
  · exact ⟨min_le_of_left_le (mul_le_mul_of_nonneg_right h1 hy),
           le_max_of_le_right (mul_le_mul_of_nonneg_right h2 hy)⟩
  · exact ⟨min_le_of_right_le (mul_le_mul_of_nonpos_right h2 hy),
           le_max_of_le_left (mul_le_mul_of_nonpos_right h1 hy)⟩

theorem bil {a b c d x y : ℝ} (h1 : a ≤ x) (h2 : x ≤ b) (h3 : c ≤ y) (h4 : y ≤ d) :
    min (min (a * c) (a * d)) (min (b * c) (b * d)) ≤ x * y ∧
    x * y ≤ max (max (a * c) (a * d)) (max (b * c) (b * d)) := by
  obtain ⟨hxl, hxu⟩ := lin1 y h1 h2
  obtain ⟨hal, hau⟩ := lin1 a h3 h4
  obtain ⟨hbl, hbu⟩ := lin1 b h3 h4
  rw [mul_comm c a, mul_comm d a] at hal hau
  rw [mul_comm c b, mul_comm d b] at hbl hbu
  rw [mul_comm y a] at hal hau
  rw [mul_comm y b] at hbl hbu
  constructor
  · refine le_trans ?_ hxl
    refine le_min ?_ ?_
    · exact le_trans (min_le_left _ _) hal
    · exact le_trans (min_le_right _ _) hbl
  · refine le_trans hxu ?_
    refine max_le ?_ ?_
    · exact le_trans hau (le_max_left _ _)
    · exact le_trans hbu (le_max_right _ _)

theorem mem_mul {A B : QI} {x y : ℝ} (hx : A.mem x) (hy : B.mem y) : (mul A B).mem (x * y) := by
  obtain ⟨h1, h2⟩ := hx; obtain ⟨h3, h4⟩ := hy
  obtain ⟨l, u⟩ := bil h1 h2 h3 h4
  simp only [mem, mul, Rat.cast_min, Rat.cast_max, Rat.cast_mul]
  exact ⟨l, u⟩

theorem excl0_sound {I : QI} {x : ℝ} (hx : I.mem x) (h : I.excl0 = true) : x ≠ 0 := by
  obtain ⟨h1, h2⟩ := hx
  simp only [excl0, Bool.or_eq_true, decide_eq_true_eq] at h
  rcases h with h | h
  · have : (0 : ℝ) < (I.lo : ℝ) := by exact_mod_cast h
    exact ne_of_gt (lt_of_lt_of_le this h1)
  · have : (I.hi : ℝ) < 0 := by exact_mod_cast h
    exact ne_of_lt (lt_of_le_of_lt h2 this)

end QI

/-! ### Complex boxes -/

structure CI where
  re : QI
  im : QI

namespace CI

def mem (B : CI) (z : ℂ) : Prop := B.re.mem z.re ∧ B.im.mem z.im
def pt (c : ℚ) : CI := ⟨QI.pt c, QI.pt 0⟩
def add (A B : CI) : CI := ⟨A.re.add B.re, A.im.add B.im⟩
def neg (A : CI) : CI := ⟨A.re.neg, A.im.neg⟩
def sub (A B : CI) : CI := ⟨A.re.sub B.re, A.im.sub B.im⟩
def mul (A B : CI) : CI := ⟨(A.re.mul B.re).sub (A.im.mul B.im), (A.re.mul B.im).add (A.im.mul B.re)⟩
def conj (A : CI) : CI := ⟨A.re, A.im.neg⟩

theorem mem_pt (c : ℚ) : (pt c).mem (c : ℂ) := by
  refine ⟨?_, ?_⟩
  · simp only [pt, Complex.ratCast_re]; exact QI.mem_pt c
  · simp only [pt, Complex.ratCast_im]; simpa using QI.mem_pt 0

theorem mem_add {A B : CI} {z w : ℂ} (hz : A.mem z) (hw : B.mem w) : (add A B).mem (z + w) := by
  refine ⟨?_, ?_⟩
  · simp only [add, Complex.add_re]; exact QI.mem_add hz.1 hw.1
  · simp only [add, Complex.add_im]; exact QI.mem_add hz.2 hw.2

theorem mem_neg {A : CI} {z : ℂ} (hz : A.mem z) : (neg A).mem (-z) := by
  refine ⟨?_, ?_⟩
  · simp only [neg, Complex.neg_re]; exact QI.mem_neg hz.1
  · simp only [neg, Complex.neg_im]; exact QI.mem_neg hz.2

theorem mem_sub {A B : CI} {z w : ℂ} (hz : A.mem z) (hw : B.mem w) : (sub A B).mem (z - w) := by
  refine ⟨?_, ?_⟩
  · simp only [sub, Complex.sub_re]; exact QI.mem_sub hz.1 hw.1
  · simp only [sub, Complex.sub_im]; exact QI.mem_sub hz.2 hw.2

theorem mem_mul {A B : CI} {z w : ℂ} (hz : A.mem z) (hw : B.mem w) : (mul A B).mem (z * w) := by
  refine ⟨?_, ?_⟩
  · simp only [mul, Complex.mul_re]; exact QI.mem_sub (QI.mem_mul hz.1 hw.1) (QI.mem_mul hz.2 hw.2)
  · simp only [mul, Complex.mul_im]; exact QI.mem_add (QI.mem_mul hz.1 hw.2) (QI.mem_mul hz.2 hw.1)

theorem mem_conj {A : CI} {z : ℂ} (hz : A.mem z) : (conj A).mem ((starRingEnd ℂ) z) := by
  refine ⟨?_, ?_⟩
  · simp only [conj, Complex.conj_re]; exact hz.1
  · simp only [conj, Complex.conj_im]; exact QI.mem_neg hz.2

end CI

/-! ### 2×2 matrix boxes -/

abbrev MB := Fin 2 → Fin 2 → CI

namespace MB

def mem (B : MB) (G : M2) : Prop := ∀ i j, (B i j).mem (G i j)
def mul (A B : MB) : MB := fun i j => ((A i 0).mul (B 0 j)).add ((A i 1).mul (B 1 j))
def adj (B : MB) : MB := ![![B 1 1, (B 0 1).neg], ![(B 1 0).neg, B 0 0]]
def tr (B : MB) : CI := (B 0 0).add (B 1 1)
def det (B : MB) : CI := ((B 0 0).mul (B 1 1)).sub ((B 0 1).mul (B 1 0))

theorem mem_mul {A B : MB} {G H : M2} (hG : A.mem G) (hH : B.mem H) : (mul A B).mem (G * H) := by
  intro i j
  rw [Matrix.mul_apply, Fin.sum_univ_two]
  exact CI.mem_add (CI.mem_mul (hG i 0) (hH 0 j)) (CI.mem_mul (hG i 1) (hH 1 j))

theorem mem_adj {B : MB} {G : M2} (hG : B.mem G) : (adj B).mem G.adjugate := by
  intro i j
  rw [Matrix.adjugate_fin_two]
  fin_cases i <;> fin_cases j
  · simpa [adj] using hG 1 1
  · simpa [adj] using CI.mem_neg (hG 0 1)
  · simpa [adj] using CI.mem_neg (hG 1 0)
  · simpa [adj] using hG 0 0

theorem mem_tr {B : MB} {G : M2} (hG : B.mem G) : (tr B).mem G.trace := by
  rw [Matrix.trace_fin_two]; exact CI.mem_add (hG 0 0) (hG 1 1)

theorem mem_det {B : MB} {G : M2} (hG : B.mem G) : (det B).mem G.det := by
  rw [Matrix.det_fin_two]
  exact CI.mem_sub (CI.mem_mul (hG 0 0) (hG 1 1)) (CI.mem_mul (hG 0 1) (hG 1 0))

end MB

/-! ### The two criteria: mathematics -/

/-- (I): with w = z·conj d, each disjunct forces d ≠ 0, and together they exclude z/d ∈ [0,4]. -/
theorem crit1_math (z d : ℂ)
    (h : (z * (starRingEnd ℂ) d).im ≠ 0 ∨ (z * (starRingEnd ℂ) d).re < 0 ∨
         4 * (d.re * d.re + d.im * d.im) < (z * (starRingEnd ℂ) d).re) :
    d ≠ 0 ∧ ¬ InRealSegment (z / d) 0 4 := by
  have hwre : (z * (starRingEnd ℂ) d).re = z.re * d.re + z.im * d.im := by
    simp [Complex.mul_re, Complex.conj_re, Complex.conj_im]
  have hwim : (z * (starRingEnd ℂ) d).im = z.im * d.re - z.re * d.im := by
    simp [Complex.mul_im, Complex.conj_re, Complex.conj_im]; ring
  rw [hwre, hwim] at h
  have hd : d ≠ 0 := by
    rintro rfl
    simp at h
  refine ⟨hd, ?_⟩
  have hns : 0 < Complex.normSq d := Complex.normSq_pos.mpr hd
  have hns' : Complex.normSq d = d.re * d.re + d.im * d.im := Complex.normSq_apply d
  rintro ⟨him, hre0, hre4⟩
  rw [Complex.div_im] at him
  rw [Complex.div_re] at hre0 hre4
  rw [hns'] at him hre0 hre4 hns
  have key_im : z.im * d.re - z.re * d.im = 0 := by
    have : (z.im * d.re - z.re * d.im) / (d.re * d.re + d.im * d.im) = 0 := by
      rw [sub_div]; linarith [him]
    rcases div_eq_zero_iff.mp this with h0 | h0
    · exact h0
    · exact absurd h0 (ne_of_gt hns)
  have key_re0 : 0 ≤ z.re * d.re + z.im * d.im := by
    have : 0 ≤ (z.re * d.re + z.im * d.im) / (d.re * d.re + d.im * d.im) := by
      rw [add_div]; linarith [hre0]
    exact (div_nonneg_iff.mp this).elim (fun h => h.1) (fun h => absurd h.2 (not_le.mpr hns))
  have key_re4 : z.re * d.re + z.im * d.im ≤ 4 * (d.re * d.re + d.im * d.im) := by
    have : (z.re * d.re + z.im * d.im) / (d.re * d.re + d.im * d.im) ≤ 4 := by
      rw [add_div]; linarith [hre4]
    rwa [div_le_iff₀ hns] at this
  rcases h with h | h | h
  · exact h key_im
  · linarith
  · linarith

/-- (II): with both determinants nonzero, the division-free form gives tr[G,H] ≠ 2. -/
theorem crit2_math (G H : M2) (hG : G.det ≠ 0) (hH : H.det ≠ 0)
    (h : (G * H * G.adjugate * H.adjugate).trace - 2 * (G.det * H.det) ≠ 0) :
    (G * H * G⁻¹ * H⁻¹).trace ≠ 2 := by
  rw [Matrix.inv_def, Matrix.inv_def, Ring.inverse_eq_inv']
  rw [Matrix.mul_smul, Matrix.mul_smul, Matrix.smul_mul, Matrix.trace_smul, Matrix.trace_smul, smul_eq_mul,
    smul_eq_mul]
  intro h2
  apply h
  have hGH : G.det * H.det ≠ 0 := mul_ne_zero hG hH
  field_simp at h2
  linear_combination h2

/-! ### Boolean check and soundness -/

def crit1 (B : MB) : Bool :=
  let t := MB.tr B
  let D := MB.det B
  let W := (t.mul t).mul D.conj
  let N := (D.re.mul D.re).add (D.im.mul D.im)
  W.im.excl0 || decide (W.re.hi < 0) || decide (4 * N.hi < W.re.lo)

def crit2 (BG BH : MB) : Bool :=
  let K := (MB.tr (((BG.mul BH).mul (MB.adj BG)).mul (MB.adj BH))).sub
    ((CI.pt 2).mul ((MB.det BG).mul (MB.det BH)))
  K.re.excl0 || K.im.excl0

def check (BG BH : MB) : Bool := crit1 BG && crit1 BH && crit2 BG BH

theorem crit1_sound {B : MB} {G : M2} (hG : B.mem G) (h : crit1 B = true) :
    G.det ≠ 0 ∧ ¬ InRealSegment (G.trace ^ 2 / G.det) 0 4 := by
  have ht := MB.mem_tr hG
  have hD := MB.mem_det hG
  have hW : ((MB.tr B).mul (MB.tr B) |>.mul (MB.det B).conj).mem
      (G.trace * G.trace * (starRingEnd ℂ) G.det) := CI.mem_mul (CI.mem_mul ht ht) (CI.mem_conj hD)
  have hN : (((MB.det B).re.mul (MB.det B).re).add ((MB.det B).im.mul (MB.det B).im)).mem
      (G.det.re * G.det.re + G.det.im * G.det.im) := QI.mem_add (QI.mem_mul hD.1 hD.1) (QI.mem_mul hD.2 hD.2)
  rw [sq]
  apply crit1_math
  simp only [crit1, Bool.or_eq_true, decide_eq_true_eq] at h
  rcases h with (h | h) | h
  · exact Or.inl (QI.excl0_sound hW.2 h)
  · refine Or.inr (Or.inl ?_)
    have : (((((MB.tr B).mul (MB.tr B)).mul (MB.det B).conj).re.hi : ℚ) : ℝ) < 0 := by exact_mod_cast h
    exact lt_of_le_of_lt hW.1.2 this
  · refine Or.inr (Or.inr ?_)
    have : (4 : ℝ) * ((((MB.det B).re.mul (MB.det B).re).add ((MB.det B).im.mul (MB.det B).im)).hi : ℝ) <
        (((((MB.tr B).mul (MB.tr B)).mul (MB.det B).conj).re.lo : ℚ) : ℝ) := by exact_mod_cast h
    nlinarith [hN.2, hW.1.1]

theorem crit2_sound {BG BH : MB} {G H : M2} (hG : BG.mem G) (hH : BH.mem H) (h : crit2 BG BH = true) :
    (G * H * G.adjugate * H.adjugate).trace - 2 * (G.det * H.det) ≠ 0 := by
  have hK := CI.mem_sub (MB.mem_tr (MB.mem_mul (MB.mem_mul (MB.mem_mul hG hH) (MB.mem_adj hG)) (MB.mem_adj hH)))
    (CI.mem_mul (by simpa using CI.mem_pt 2) (CI.mem_mul (MB.mem_det hG) (MB.mem_det hH)))
  simp only [crit2, Bool.or_eq_true] at h
  intro h0
  rw [h0] at hK
  rcases h with h | h
  · exact QI.excl0_sound hK.1 h (by simp)
  · exact QI.excl0_sound hK.2 h (by simp)

/-- **Soundness.** If the kernel-decidable `check` holds, every pair of matrices in the boxes is invertible and
satisfies the conclusion of `L6_gl2`: for every `k ≥ 1`, no finite-relative-index subgroup of `⟨G^k, H^k⟩` is
abelian. -/
theorem cert_sound (BG BH : MB) (hc : check BG BH = true) (G H : M2) (hG : BG.mem G) (hH : BH.mem H) :
    ∃ UG UH : (Matrix (Fin 2) (Fin 2) ℂ)ˣ, (UG : M2) = G ∧ (UH : M2) = H ∧
      ∀ k : ℕ, 0 < k → ∀ A : Subgroup (Matrix (Fin 2) (Fin 2) ℂ)ˣ,
        A.relIndex (Subgroup.closure {UG ^ k, UH ^ k}) ≠ 0 → ¬ (∀ a ∈ A, ∀ b ∈ A, a * b = b * a) := by
  simp only [check, Bool.and_eq_true] at hc
  obtain ⟨⟨h1G, h1H⟩, h2⟩ := hc
  obtain ⟨hdG, hsG⟩ := crit1_sound hG h1G
  obtain ⟨hdH, hsH⟩ := crit1_sound hH h1H
  have hc2 := crit2_math G H hdG hdH (crit2_sound hG hH h2)
  have uG : IsUnit G := (Matrix.isUnit_iff_isUnit_det G).mpr (isUnit_iff_ne_zero.mpr hdG)
  have uH : IsUnit H := (Matrix.isUnit_iff_isUnit_det H).mpr (isUnit_iff_ne_zero.mpr hdH)
  refine ⟨uG.unit, uH.unit, uG.unit_spec, uH.unit_spec, ?_⟩
  intro k hk A hA
  exact L6_gl2 uG.unit uH.unit (by rwa [uG.unit_spec]) (by rwa [uH.unit_spec])
    (by rwa [uG.unit_spec, uH.unit_spec]) k hk A hA

/-- The statement a certificate establishes, for boxes `BG`, `BH`. -/
def CertConclusion (BG BH : MB) : Prop :=
  ∀ G H : M2, BG.mem G → BH.mem H →
    ∃ UG UH : (Matrix (Fin 2) (Fin 2) ℂ)ˣ, (UG : M2) = G ∧ (UH : M2) = H ∧
      ∀ k : ℕ, 0 < k → ∀ A : Subgroup (Matrix (Fin 2) (Fin 2) ℂ)ˣ,
        A.relIndex (Subgroup.closure {UG ^ k, UH ^ k}) ≠ 0 → ¬ (∀ a ∈ A, ∀ b ∈ A, a * b = b * a)

theorem cert_of_check (BG BH : MB) (hc : check BG BH = true) : CertConclusion BG BH :=
  fun G H hG hH => cert_sound BG BH hc G H hG hH
