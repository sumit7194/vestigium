// GUARD CONTROL (must be REFUSED): a CAPD Map formula containing log (CAPD log returns NaN below 0).
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
int main(){ capd::MpFloat::setDefaultPrecision(128); capd::MpIMap m("var:x;fun:log(x);"); return 0; }
