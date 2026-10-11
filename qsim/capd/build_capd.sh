#!/bin/zsh
# Reproducible, load-gated, detached CAPD build (plan from the bridge, 2026-10-11).
#  * starts from the PINNED tarball (sha256 checked), NO source patch (official -DCAPD_INTERVAL_TYPE=NATIVE);
#  * every step's exit status is checked: the first failure stops the script with "STEP <name> FAILED rc=<n>"
#    (fixes the earlier bug where a later step's status was printed as BUILD EXIT 0);
#  * gate: load < 8 and free+inactive >= 3 GB; -j2.
setopt pipefail
HERE=${0:A:h}
TARBALL=$HOME/opt/CAPD-2f06098.tar.gz
SHA=9998574057400c7a75f483ba3f3cdb14f8824b28fb62eceacdec5327eda7d909
SRC=$HOME/opt/capd-src-2f06098
PREFIX=$HOME/opt/capd-2f06098-install
step() { local name=$1; shift; echo "=== STEP $name: $*"; "$@"; local rc=$?; if [ $rc -ne 0 ]; then echo "STEP $name FAILED rc=$rc $(date)"; exit $rc; fi; echo "=== STEP $name ok"; }
gate() {
  local load=$(sysctl -n vm.loadavg | awk '{print $2}')
  local fi=$(vm_stat | awk '/Pages free/ {f=$3} /Pages inactive/ {i=$3} END {gsub("\\.","",f); gsub("\\.","",i); print (f+i)*16384/1e9}')
  awk -v l=$load -v m=$fi 'BEGIN {exit !(l < 8 && m >= 3)}'
}
step sha256 sh -c "echo '$SHA  $TARBALL' | shasum -a 256 -c -"
rm -rf $SRC && mkdir -p $SRC
step extract tar xzf $TARBALL -C $SRC --strip-components 1
until gate; do sleep 120; done
echo "gate open $(date)"
mkdir -p $SRC/build && cd $SRC/build
step configure cmake .. -DCMAKE_PREFIX_PATH=/opt/homebrew -DCMAKE_CXX_FLAGS=-I/opt/homebrew/include -DCMAKE_C_FLAGS=-I/opt/homebrew/include -DCMAKE_EXE_LINKER_FLAGS=-L/opt/homebrew/lib -DCMAKE_SHARED_LINKER_FLAGS=-L/opt/homebrew/lib -DCAPD_INTERVAL_TYPE=NATIVE -DCAPD_ENABLE_MULTIPRECISION=ON -DCAPD_BUILD_EXAMPLES=ON -DCAPD_BUILD_TESTS=ON -DCMAKE_INSTALL_PREFIX=$PREFIX
step build /usr/bin/time -l make -j2
step install make install
echo "=== STEP ctest (all results logged; failures do not stop the script, they are the report)"
ctest --output-on-failure -j2 > $HERE/ctest_full.log 2>&1; echo "ctest rc=$?"
tail -40 $HERE/ctest_full.log
du -sh $SRC/build $PREFIX
echo "BUILD SCRIPT DONE $(date)"
