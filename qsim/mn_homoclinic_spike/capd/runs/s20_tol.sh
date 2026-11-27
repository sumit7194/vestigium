#!/bin/zsh
cd ${0:A:h}/..
./s2_capd_t ret 0 2.75 0 1/10000000000 100 128 20 kerr_fp_hw1e-10_tol24 24
./s2_capd_t ret 0 2.75 0 1/100000000000000 100 128 20 kerr_fp_hw1e-14_tol24 24
echo DONE
