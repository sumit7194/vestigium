# G3 worker memory growth: the finding (2026-11-18)

## What was observed
- Task #21 in grind0 is G1_00_P: P with jac (a 20-dim state), tmax 2000, tol 1e-12.
- Its footprint grows linearly from a fresh start:
  - 46 MB/min overnight;
  - 61 MB/min at 14:03–14:32;
  - 62 MB/min in a plain standalone run (121 → 339 MB in 4 min).
- The integration crawls near t ≈ 1550.36: under tracemalloc, t advanced only ~3e-4 in 4 min.

## The cause
- scipy's solve_ivp keeps every accepted step (sol.t and sol.y) when t_eval is None.
- tracemalloc puts the growth in scipy's rk.py:66 and ivp.py.
- It is not a leak in our code. Neither MNFlow nor the worker keeps anything.

## The test
- **The same run with t_eval=[] (g1noteval.py):** the footprint stays flat at 89 MB for 3 min.
- **Bit-identity (teval_eq.py):** 8 completed tasks run both ways (P with jac ×5, Pinv ×3) give identical values, against each other and against the jsonl. solve_ivp status and the events are identical too.
  - The step history doesn't affect the result: MNFlow uses only t_events and y_events.
  - t_eval changes no step choice.
- **The final-t log field:**
  - The worker's log field sol.t[-1] would be lost with t_eval=[].
  - It is replaced by the largest t at which the event function was evaluated. solve_ivp evaluates the event at every accepted step's end, and root-finding stays inside accepted steps, so this is the last accepted t.
  - It agrees on all 8 tasks.
  - Not exercised: a status −1 case. None of the 8 was one.

## The proposal (NOT applied; for the Bridge)
- In b15b_mnflow_worker.py's solve_ivp wrapper, pass t_eval=[] and wrap the event function to record max t.
- MNFlow's code stays untouched.

## Applied (2026-11-18, the Bridge approved)
- b15b_mnflow_worker.py now has the t_eval=[] fix and the max-t event wrapper.
- B15B_DEFER=G1_00_P runs that task last.
- **Caveat, kept:** the status −1 path is untested for the new logged t. Any status −1 row goes to the Bridge before its logged t is trusted.
- Rows written before this change (20 in grind0, all the others) log sol.t[-1]. Rows written after it log the max event-evaluation t.

## Status −1 path: tested (2026-11-18 16:14–16:18, Opus 5.5, Quantum-personal session)
- Why it mattered: 19 of grind0's 20 rows are solve_ivp status −1 (all written before the fix), as are 2/142 in fast0,
  6/8 in w1, 18/62 in w2, 1/17 in w3. So the untested path is the common one for the remaining grind tasks.
- Test: `teval_eq.py` (unchanged) on six status −1 tasks: G4_o7_k006_Pinv, G4_o5_k003_Pinv, G4_o7_k003_Pinv,
  G4_o4_k001_Pinv, G1_02_Pinv and the P task G4_o1_k003_P_tol1e-11; nice 10, 3.5 min. Output: `status_m1_check.txt`.
- Result: ALL IDENTICAL. In all six, the values are bit-identical (old run, t_eval=[] run, jsonl), status and events
  are identical, and the logged final t is identical (sol.t[-1] == max event-evaluation t, e.g. 303699.70880973886).
- Limits: six tasks, five of them Pinv; G-type P tasks with jac (the grind0 kind) are not in the set, because
  each takes 1.5–3.4 h.

## CORRECTION (2026-11-19, Opus 5.5, session "Quantum")
- "Task #21 in grind0 is G1_00_P" was WRONG. I checked done-ness against grind0.jsonl only. The worker checks against ALL
  mnflow_*.jsonl, and G1_00_P was already done in mnflow_w0.jsonl from October.
- The task that actually grew memory on 17–18 Nov was **G3_044_P**. It was grind0's row 21, finished under the fix in
  11,978 s.
- The diagnosis is unaffected:
  - the standalone profile of G1_00_P shows the same mechanism (scipy keeps the step history);
  - the fix is bit-identical on 8 + 6 tasks;
  - the worker has stayed flat at ~89 MB on the real tasks since 18 Nov.
- `B15B_DEFER=G1_00_P` has been a NO-OP. The task is done, so the worker never scheduled it. The deferral is dropped from
  future launches.
