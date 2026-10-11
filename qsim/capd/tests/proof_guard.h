// proof_guard.h -- include LAST in every proof-bearing translation unit (CAPD trust rule 1, bridge 2026-10-11).
// Layer 1: after CAPD's headers are in, POISON every non-MPFR-interval CAPD type name, so proof code that names one
// fails to compile. Allowed in proof code: MpInterval and the MpI* types (MpIMap, MpIVector, MpIMatrix,
// MpIOdeSolver, MpICnOdeSolver, MpITimeMap, MpIPoincareMap, MpICnPoincareMap, MpICoordinateSection,
// MpIAffineSection, MpINonlinearSection, ...).
// Layer 2 (in check_proof_object.sh): nm of the proof object file must show no capd template instantiated on
// double, long double or a double interval -- that catches indirect use that name-poisoning cannot see.
#pragma once
#include "capd/mpcapdlib.h"
// double-interval types (I*, interval, DInterval), plain double and long-double types (D*, LD*), and non-interval
// multiprecision types (Mp* without I):
#pragma GCC poison interval DInterval IMap IVector IMatrix IOdeSolver ICnOdeSolver ITimeMap ICnTimeMap
#pragma GCC poison IPoincareMap ICnPoincareMap ICoordinateSection IAffineSection INonlinearSection IFunction
#pragma GCC poison DMap DVector DMatrix DOdeSolver DCnOdeSolver DTimeMap DCnTimeMap DPoincareMap DCnPoincareMap
#pragma GCC poison DCoordinateSection DAffineSection DNonlinearSection DFunction
#pragma GCC poison LDMap LDVector LDMatrix LDOdeSolver LDCnOdeSolver LDTimeMap LDPoincareMap LDFunction
#pragma GCC poison MpMap MpVector MpMatrix MpOdeSolver MpCnOdeSolver MpTimeMap MpCnTimeMap MpPoincareMap
#pragma GCC poison MpCnPoincareMap MpCoordinateSection MpAffineSection MpNonlinearSection MpFunction
// double-interval SET typedefs are unprefixed in namespace capd (their MPFR versions are MpC0Rect2Set etc.):
#pragma GCC poison C0Set C0Intv2Set C0Pped2Set C0Rect2Set C0TripletonSet C0PpedSet C0RectSet C0HORect2Set
#pragma GCC poison C0HOTripletonSet C1Set C1RectSet C1PpedSet C1Rect2Set C1Pped2Set C11Rect2Set C1HORect2Set
#pragma GCC poison C1HOPped2Set C2Set C2Rect2Set CnSet CnRect2Set
