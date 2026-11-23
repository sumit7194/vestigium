/- crit2-only controls (Bridge Lean faithfulness read, 2026-11-23, item 3). Written by hand (Claude Opus 5.5).
   The registered controls fail through crit1 (the Kerr pairs, poison_seg) or through `check` as a whole
   (poison_comm). These lemmas make criterion (II) fire ON ITS OWN: crit1 passes for both boxes, and crit2 alone
   rejects a commuting pair. Separate file: Controls.lean and `check` are unchanged. -/
import ZiglinCert.Certs.Controls

namespace Certs.Controls2

open Certs.Controls

/-- the real box passes criterion (I) -/
theorem crit1_G : crit1 G = true := by decide +kernel

/-- crit2 alone rejects G against itself (commutator = 1, so the trace is 2) -/
theorem crit2_only_self : crit1 G = true ∧ crit2 G G = false := by decide +kernel

/-- a non-identical commuting pair: G against the box product G·G. crit1 passes for both, and crit2 alone rejects. -/
theorem crit2_only_square : crit1 G = true ∧ crit1 (MB.mul G G) = true ∧ crit2 G (MB.mul G G) = false := by
  decide +kernel

#print axioms crit2_only_square

end Certs.Controls2
