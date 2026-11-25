"""Disk-floor policy shared by b15d_run.guard_loop and erep_guard.py. Sumit's standing rule (relayed by the Bridge,
2026-11-25): NO hard caps that end a job. Disk pressure PAUSES the guarded job's own verified PIDs, alerts, and resumes
automatically on recovery. It NEVER kills, at any disk level.
  free < 3 GB, not paused  -> "pause"  (SIGSTOP)
  paused and free > 4 GB   -> "resume" (SIGCONT)
  otherwise                -> None
  free < 2 GB              -> critical(): the guard logs an ALERT line (the watchers relay it to the Bridge at once)
TEST HOOK ONLY: if DISK_FAKE_GB_FILE is set, free_gb() reads an integer from that file instead of the real free space
(planted values for the tests); production guards never set it."""
import os, shutil

PAUSE_BELOW, RESUME_ABOVE, CRITICAL_BELOW = 3, 4, 2


def free_gb():
    f = os.environ.get("DISK_FAKE_GB_FILE")
    if f:
        try: return int(open(f).read().strip())
        except (OSError, ValueError): pass
    return int(shutil.disk_usage("/").free // 2 ** 30)       # whole GB available, as df -g's Avail column


def disk_action(dk, paused):
    if dk < PAUSE_BELOW and not paused: return "pause"
    if paused and dk > RESUME_ABOVE: return "resume"
    return None


def critical(dk):
    return dk < CRITICAL_BELOW
