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
