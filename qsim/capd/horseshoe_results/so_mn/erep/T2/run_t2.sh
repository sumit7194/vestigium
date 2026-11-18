#!/bin/zsh
# T2 (E_REP_PREREG.md): toys A-E and the E-relevant negative controls under SO_EREP=zsym and zg (ZG 256,128), checked
# by toys_so.py against the closed-form flows; plus box mode (flag unset) vs the saved so_gates outputs (numcmp).
T=/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests; O=${0:A:h}; G=$O/../../../so_gates; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
D=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results
cd $T
for X in A B C D E; do ./toys_so_erep $X 0.1 1 > $O/box_toy_$X.out 2>&1; echo "box toy $X vs saved so_gates/toy_$X.out: $(cmp -s $O/box_toy_$X.out $G/toy_$X.out && echo BYTE-IDENTICAL || echo DIFFERS)"; done
for M in zsym zg; do
  for X in A B C D E; do SO_EREP=$M ./toys_so_erep $X 0.1 1 > $O/${M}_toy_$X.out 2>&1; echo "== $M toy $X"; $PY $T/toys_so.py $O/${M}_toy_$X.out $X 0.1; grep "^# EREP final" $O/${M}_toy_$X.out; done
  for X in C D E; do SO_EREP=$M NEG_NOSPREAD=1 ./toys_so_erep $X 0.1 1 > $O/${M}_neg_nospread_$X.out 2>&1; echo "== $M negative nospread_$X"; $PY $T/toys_so.py $O/${M}_neg_nospread_$X.out $X 0.1; done
  SO_EREP=$M NEG_OFFDIAG=0.5 ./toys_so_erep D 0.1 1 > $O/${M}_neg_offdiag_D.out 2>&1; echo "== $M negative offdiag_D (0.5)"; $PY $T/toys_so.py $O/${M}_neg_offdiag_D.out D 0.1
  SO_EREP=$M NEG_OFFDIAG=2 ./toys_so_erep D 0.1 1 > $O/${M}_neg_offdiag2_D.out 2>&1; echo "== $M negative offdiag2_D (2)"; $PY $T/toys_so.py $O/${M}_neg_offdiag2_D.out D 0.1
  for X in B C D; do SO_EREP=$M NEG_REMSCALE=0 ./toys_so_erep $X 0.1 1 > $O/${M}_neg_rem_$X.out 2>&1; echo "== $M negative rem_$X"; $PY $T/toys_so.py $O/${M}_neg_rem_$X.out $X 0.1; done
done
echo "T2 DONE $(date)"
