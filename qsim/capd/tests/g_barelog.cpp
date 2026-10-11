// GUARD CONTROL (must NOT COMPILE): bare log is poisoned; proof code must call capd_proof::checked_log.
#include "capd/mpcapdlib.h"
#include "proof_guard.h"
int main(){ capd::MpInterval x(2); auto y = log(x); return 0; }
