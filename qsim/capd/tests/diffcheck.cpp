// CAPD trust rule 3: differential check of CAPD MpInterval (MPFR) against Arb (driver: qsim/capd/diffcheck.py).
// Built under the proof guard (guard_build.sh), so the arithmetic tested is the one proof code gets, and sin/cos go
// through the fail-closed range guard capd_proof::checked_sin/checked_cos. "log" is CAPD's raw log (to characterise
// it); "clog" is the guarded capd_proof::checked_log (a control: must throw unless the box is > 0).
// Usage: diffcheck PREC < ops.  Each input line: "id op lo hi [lo2 hi2]", endpoints as exact MPFR hex ("0x1fp-3").
// Each output line: "id OK lo hi" (CAPD's enclosure endpoints, exact, %Ra), "id THROW <message>", or
// "id BADINPUT <why>" (an operand was not exactly representable at PREC: the driver treats that as its own bug).
// Hard per-call timeout: SIGALRM after 10 s prints "id TIMEOUT" and exits 3; the driver restarts after that line.
#include "capd/mpcapdlib.h"
// the RAW CAPD log, captured before the guard poisons the name: this harness characterises CAPD itself
static capd::MpInterval raw_log(const capd::MpInterval& x) { return log(x); }
#include "proof_guard.h"
#include <cstdio>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

static char g_id[64] = "?";
extern "C" void on_alarm(int) {
  char buf[96];
  int n = std::snprintf(buf, sizeof buf, "%s TIMEOUT\n", g_id);
  ssize_t r = ::write(1, buf, n); (void)r;
  std::_Exit(3);
}

// exact access to an MpReal's mpfr value (protected member, read through a pointer-to-member of a derived class)
struct RepAccess : capd::multiPrec::MpReal { static constexpr auto rep = &RepAccess::mpfr_rep; };
static mpfr_srcptr rep(const capd::multiPrec::MpReal& r) { return r.*RepAccess::rep; }
static mpfr_ptr rep_mut(capd::multiPrec::MpReal& r) { return r.*RepAccess::rep; }

static bool parse_exact(const std::string& s, mpfr_prec_t prec, capd::multiPrec::MpReal& out, std::string& why) {
  mpfr_t t; mpfr_init2(t, prec);
  char* end = nullptr;
  int tern = mpfr_strtofr(t, s.c_str(), &end, 16, MPFR_RNDN);
  bool ok = end && *end == '\0' && tern == 0 && mpfr_number_p(t);
  if (!ok) why = "not exactly representable / unparsable: " + s;
  // (CAPD declares MpReal(mpfr_t, ...) but does not define it, so set the value through the representation;
  //  the default constructor initialises at the default precision, which main() set to prec)
  else if (mpfr_get_prec(rep(out)) != prec || mpfr_set(rep_mut(out), t, MPFR_RNDN) != 0 || mpfr_cmp(rep(out), t) != 0) {
    why = "copy into MpReal not exact: " + s; ok = false;
  }
  mpfr_clear(t);
  return ok;
}

static std::string hexof(const capd::multiPrec::MpReal& r) {
  char* s = nullptr;
  mpfr_asprintf(&s, "%Ra", rep(r));
  std::string o(s); mpfr_free_str(s); return o;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: diffcheck PREC\n"); return 2; }
  const mpfr_prec_t prec = std::atol(argv[1]);
  capd::MpFloat::setDefaultPrecision(prec);
  std::signal(SIGALRM, on_alarm);
  std::string line;
  while (std::getline(std::cin, line)) {
    std::istringstream in(line);
    std::string id, op, a, b, c, d;
    in >> id >> op >> a >> b;
    std::strncpy(g_id, id.c_str(), sizeof g_id - 1);
    const bool binary = (op == "add" || op == "sub" || op == "mul" || op == "div");
    if (binary) in >> c >> d;
    capd::multiPrec::MpReal al, ah, bl, bh; std::string why;
    if (!parse_exact(a, prec, al, why) || !parse_exact(b, prec, ah, why) ||
        (binary && (!parse_exact(c, prec, bl, why) || !parse_exact(d, prec, bh, why)))) {
      std::cout << id << " BADINPUT " << why << std::endl; continue;
    }
    ::alarm(10);
    try {
      capd::MpInterval x(al, ah), r;
      if (binary) {
        capd::MpInterval y(bl, bh);
        if (op == "add") r = x + y; else if (op == "sub") r = x - y;
        else if (op == "mul") r = x * y; else r = x / y;
      } else if (op == "sqrt") r = sqrt(x);
      else if (op == "exp") r = exp(x);
      else if (op == "log") r = raw_log(x);
      else if (op == "clog") r = capd_proof::checked_log(x);
      else if (op == "sin") r = capd_proof::checked_sin(x);
      else if (op == "cos") r = capd_proof::checked_cos(x);
      else { ::alarm(0); std::cout << id << " BADINPUT unknown op " << op << std::endl; continue; }
      ::alarm(0);
      std::cout << id << " OK " << hexof(r.leftBound()) << " " << hexof(r.rightBound()) << std::endl;
    } catch (std::exception& e) {
      ::alarm(0);
      std::string m(e.what());
      for (char& ch : m) if (ch == '\n') ch = ' ';
      std::cout << id << " THROW " << m << std::endl;
    }
  }
  return 0;
}
