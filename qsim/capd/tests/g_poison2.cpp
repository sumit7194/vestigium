#include "proof_guard.h"
int main(){ capd::MpFloat::setDefaultPrecision(128); capd::MpIMap f("var:x;fun:-x;"); capd::MpIVector u(1); capd::C0Rect2Set s(u); }
