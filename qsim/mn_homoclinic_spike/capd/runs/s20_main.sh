#!/bin/zsh
# S2-0 as registered (A6/A10), beta = 3/100, step tolerance 1e-24 (step control only; same for every S2 run)
cd ${0:A:h}/..
./s2_capd_t ret 3/100 2.784144616590076 0.000000000000011702780548662953 1/10000000 100 128 20 s20a_conebox_fp_hw1e-7 24
./s2_capd_t ret 3/100 3.186461813406459 0.3551903450071813 1/100000000000000 375 128 20 s20b_long_return_hw1e-14 24
echo DONE
