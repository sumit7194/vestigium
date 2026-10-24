# B15b gate log

- 2026-10-24: **The MNFlow reference task SCHEDULING changed** (the Bridge agreed). Grinding tasks are predicted by
  kerr_rs's kerr_state_at to tmax (grind_prediction.json, a4fec7f).
  - Non-grinders run on "fast" workers; grinders run on a dedicated "grind" worker.
  - **The compiled map was used ONLY to ORDER the tasks. It never supplies or alters a reference value.** A
    misclassified task runs where it lands, under the same memory cap.
  - Memory cap: 8 GB per worker. A worker that hits it is stopped and NOT retried; that becomes a gate question for
    the user, never decided inside the run.
  - Parallel grinding (2 at once) only if the measured RSS slope data shows their combined peak stays ≤ 10 GB.
    Otherwise it stays serial.
  - The 3 workers in flight (w0, w1, w2) each finish their current (grinding) task first; then the supervisor hands
    their slots over.
