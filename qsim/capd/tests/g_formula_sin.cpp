// GUARD CONTROL (must be REFUSED): a CAPD Map formula containing a trig/log function (args cannot be range-checked).
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
int main(){ capd::MpFloat::setDefaultPrecision(128); capd::MpIMap m("var:x;fun:sin(x);"); return 0; }
