#!/bin/zsh
# Lean 4 + Mathlib setup (v2: resumable toolchain download), disk guard: stop if free < 4 GB (per user).
set -u
D=/Users/sumit/Github/quantum/lean
LOG=$D/setup_lean.log
TC=v4.35.0-rc3
URL=https://releases.lean-lang.org/lean4/$TC/lean-${TC#v}-darwin_aarch64.tar.zst
ARCH=$D/dl/lean-${TC#v}-darwin_aarch64.tar.zst
TCDIR=$HOME/.elan/toolchains/leanprover--lean4---$TC
free_gb() { df -g / | tail -1 | awk '{print $4}'; }
mkdir -p $D/dl
echo "start v2 $(date) free=$(free_gb) GB" >> $LOG
guard() { while kill -0 $1 2>/dev/null; do
  if [ "$(free_gb)" -lt 4 ]; then echo "DISK GUARD: free=$(free_gb) GB < 4 GB -- killing pid $1 $(date)" >> $LOG; pkill -P $1; kill $1; exit 2; fi
  sleep 5; done; }
# 1. toolchain, resumable, retried until complete
if [ ! -x $TCDIR/bin/lean ]; then
  for attempt in $(seq 1 200); do
    curl -L -C - --speed-time 120 --speed-limit 1 -s -o $ARCH $URL &   # no internal --retry (it restarts from 0); the outer loop resumes with -C -
    CP=$!; guard $CP; wait $CP; RC=$?
    SZ=$(stat -f %z $ARCH 2>/dev/null || echo 0)
    echo "toolchain attempt $attempt rc=$RC size=$SZ $(date)" >> $LOG
    [ "$SZ" -ge 571824435 ] && break
    sleep 10
  done
  mkdir -p $D/dl/unpack && tar -xf $ARCH -C $D/dl/unpack >> $LOG 2>&1 || { echo "TOOLCHAIN UNPACK FAILED" >> $LOG; exit 3; }
  SRC=$(ls -d $D/dl/unpack/lean-* | head -1)
  [ -x $SRC/bin/lean ] || { echo "TOOLCHAIN BINARY MISSING" >> $LOG; exit 3; }
  rm -rf $TCDIR; mv $SRC $TCDIR
  echo "toolchain installed: $($TCDIR/bin/lean --version) $(date) free=$(free_gb) GB" >> $LOG
fi
# 2. Mathlib project, cache (lake's own downloader; retried), test build
cd $D
( set -e
  [ -d ZiglinCert ] || lake +leanprover/lean4:$TC new ZiglinCert math >> $LOG 2>&1
  echo "project created $(date) free=$(df -g / | tail -1 | awk '{print $4}') GB" >> $LOG
  cd ZiglinCert
  for i in 1 2 3 4 5 6; do lake exe cache get >> $LOG 2>&1 && break; echo "cache get retry $i $(date)" >> $LOG; sleep 30; done
  echo "cache fetched $(date) free=$(df -g / | tail -1 | awk '{print $4}') GB" >> $LOG
  lake build >> $LOG 2>&1
  echo "BUILD_DONE $(date)" >> $LOG
) &
W=$!; guard $W; wait $W; RC=$?
echo "END rc=$RC $(date) free=$(free_gb) GB" >> $LOG
