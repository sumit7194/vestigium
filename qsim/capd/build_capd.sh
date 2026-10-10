#!/bin/zsh
# Load-gated, detached CAPD build (load < 8 and free+inactive >= 3 GB, as the bridge asked). -j2.
SRC=$HOME/opt/CAPD-6.0.0; PREFIX=$HOME/opt/capd-6.0.0-install
gate() {
  local load=$(sysctl -n vm.loadavg | awk '{print $2}')
  local fi=$(vm_stat | awk '/Pages free/ {f=$3} /Pages inactive/ {i=$3} END {gsub("\\.","",f); gsub("\\.","",i); print (f+i)*16384/1e9}')
  awk -v l=$load -v m=$fi 'BEGIN {exit !(l < 8 && m >= 3)}'
}
until gate; do sleep 120; done
echo "gate open $(date)"
mkdir -p $SRC/build && cd $SRC/build
cmake .. -DCAPD_ENABLE_MULTIPRECISION=ON -DCAPD_BUILD_EXAMPLES=ON -DCMAKE_INSTALL_PREFIX=$PREFIX 2>&1 | tail -25
/usr/bin/time -l make -j2 2>&1 | tail -40
make install 2>&1 | tail -5
echo "BUILD EXIT $? $(date)"
du -sh $SRC/build $PREFIX
