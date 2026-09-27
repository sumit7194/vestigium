"""
Resource watchdog for the Morales-Ramis tool -- added 2026-09-24 after a controls
run of mine grew to a 10 GB footprint on the shared machine (swap 3.1/4.1 GB)
with no guard at all. RSS showed 0.8 GB because most of it was compressed or
swapped, so RSS is NOT a usable signal: this polls the kernel's physical
FOOTPRINT (macOS `footprint`, ~10 ms per call).

run_guarded(cmd) runs cmd as a child process, polls its footprint every `poll`
seconds, and kills it if it exceeds mem_limit_mb or time_limit_s. The caller
must record a killed job as INCONCLUSIVE (resource limit) -- never as a verdict.
"""
import re
import subprocess
import time

_UNITS = {"B": 1/2**20, "KB": 1/1024, "MB": 1.0, "GB": 1024.0}


def footprint_mb(pid):
    try:
        out = subprocess.run(["footprint", str(pid)], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return None
    m = re.search(r"Footprint:\s*([\d.]+)\s*(B|KB|MB|GB)", out)
    return float(m.group(1))*_UNITS[m.group(2)] if m else None


def swap_free_mb():
    """Free swap in MB, or None when unknown OR when no swap exists yet. macOS creates swap
    files on demand, so total = 0 after a reboot on an idle box; the old rule read free = 0
    there and killed every run (2026-09-27, same bug deepstrain fixed)."""
    try:
        out = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True, timeout=5).stdout
        tot = re.search(r"total\s*=\s*([\d.]+)M", out)
        m = re.search(r"free\s*=\s*([\d.]+)M", out)
        if not m or not tot or float(tot.group(1)) <= 0:
            return None
        return float(m.group(1))
    except Exception:
        return None


def mem_free_pct():
    """System-wide memory free percentage from macOS `memory_pressure -Q` (None if unavailable)."""
    try:
        out = subprocess.run(["memory_pressure", "-Q"], capture_output=True, text=True, timeout=10).stdout
        m = re.search(r"free percentage:\s*(\d+)%", out)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def disk_free_gb(path="/"):
    import shutil
    return shutil.disk_usage(path).free/1e9


# Box-level guards (bridge, 2026-09-24): kill the child if the SHARED machine is in
# trouble, regardless of the child's own size.
SWAP_FREE_MIN_MB = 512          # applied only when swap exists (total > 0)
MEM_FREE_MIN_PCT = 10           # system-wide memory free % (memory_pressure): the real trigger
DISK_FREE_MIN_GB = 5.0


def run_guarded(cmd, mem_limit_mb=4096, time_limit_s=900, poll=1.0, cwd=None, log=None):
    t0 = time.time()
    peak = 0.0
    import contextlib
    with (open(log, "w") if log else contextlib.nullcontext(None)) as fh:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=fh if log else subprocess.DEVNULL,
                                stderr=subprocess.STDOUT)
        status = "ok"
        while proc.poll() is None:
            time.sleep(poll)
            fp = footprint_mb(proc.pid)
            if fp is not None:
                peak = max(peak, fp)
                if fp > mem_limit_mb:
                    status = "mem_limit"
            if time.time() - t0 > time_limit_s:
                status = "time_limit"
            sw = swap_free_mb()
            if sw is not None and sw < SWAP_FREE_MIN_MB:
                status = "box_swap_guard"
            mp = mem_free_pct()
            if mp is not None and mp < MEM_FREE_MIN_PCT:
                status = "box_memory_pressure_guard"
            if disk_free_gb() < DISK_FREE_MIN_GB:
                status = "box_disk_guard"
            if status != "ok":
                proc.kill()
                proc.wait()
                break
        rc = proc.returncode
    if status == "ok" and rc != 0:
        status = "error"
    return dict(status=status, returncode=rc, peak_mb=round(peak, 1), seconds=round(time.time() - t0, 1))
