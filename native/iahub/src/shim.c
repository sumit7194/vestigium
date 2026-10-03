/* Thin C shim over FLINT/Arb 3.6.0 for the iahub native core (PREREG_iahub_v2.md).
 * Opaque handles only: Rust never assumes FLINT struct layouts. Every function is a direct call into Arb;
 * rigour lives entirely in Arb's ball arithmetic. Rounding: upper bounds round UP, lower bounds round DOWN. */
#include <stdlib.h>
#include <string.h>
#include <flint/flint.h>
#include <flint/fmpq.h>
#include <flint/arb.h>
#include <flint/acb.h>
#include <flint/acb_poly.h>

typedef struct { acb_t v; } ball_t;
typedef struct { acb_poly_t p; } ser_t;

/* ---------------- scalar balls ---------------- */
ball_t *ib_new(void) { ball_t *b = malloc(sizeof(ball_t)); acb_init(b->v); return b; }
void ib_free(ball_t *b) { acb_clear(b->v); free(b); }
void ib_set(ball_t *r, const ball_t *a) { acb_set(r->v, a->v); }
void ib_set_si(ball_t *r, long re, long im) { acb_set_si_si(r->v, re, im); }
/* exact rational "p/q" (or integer) as a real ball */
int ib_set_rational(ball_t *r, const char *s, long prec) {
    fmpq_t q; fmpq_init(q);
    int bad = fmpq_set_str(q, s, 10);
    if (!bad) acb_set_fmpq(r->v, q, prec);
    fmpq_clear(q);
    return bad;
}
/* exact dyadic complex point from two doubles */
void ib_set_d_d(ball_t *r, double re, double im) { acb_set_d_d(r->v, re, im); }
/* box: [re +- rad] + [im +- rad] i (a superset of the disk of radius rad) */
void ib_set_box(ball_t *r, double re, double im, double rad) {
    arb_t x, y; arb_init(x); arb_init(y);
    arb_set_d(x, re); arb_set_d(y, im);
    { arf_t e; arf_init(e); arf_set_d(e, rad); arb_add_error_arf(x, e); arb_add_error_arf(y, e); arf_clear(e); }
    acb_set_arb_arb(r->v, x, y);
    arb_clear(x); arb_clear(y);
}
void ib_add(ball_t *r, const ball_t *a, const ball_t *b, long prec) { acb_add(r->v, a->v, b->v, prec); }
void ib_sub(ball_t *r, const ball_t *a, const ball_t *b, long prec) { acb_sub(r->v, a->v, b->v, prec); }
void ib_mul(ball_t *r, const ball_t *a, const ball_t *b, long prec) { acb_mul(r->v, a->v, b->v, prec); }
void ib_div(ball_t *r, const ball_t *a, const ball_t *b, long prec) { acb_div(r->v, a->v, b->v, prec); }
void ib_neg(ball_t *r, const ball_t *a) { acb_neg(r->v, a->v); }
void ib_inv(ball_t *r, const ball_t *a, long prec) { acb_inv(r->v, a->v, prec); }
void ib_exp(ball_t *r, const ball_t *a, long prec) { acb_exp(r->v, a->v, prec); }
void ib_mul_si(ball_t *r, const ball_t *a, long c, long prec) { acb_mul_si(r->v, a->v, c, prec); }
void ib_div_si(ball_t *r, const ball_t *a, long c, long prec) { acb_div_si(r->v, a->v, c, prec); }
int ib_is_finite(const ball_t *a) { return acb_is_finite(a->v); }
/* rigorous double upper bound of |a| (rounded up); +inf if not finite */
double ib_abs_upper(const ball_t *a, long prec) {
    if (!acb_is_finite(a->v)) return 1.0/0.0;
    arb_t m; arf_t u; arb_init(m); arf_init(u);
    acb_abs(m, a->v, prec); arb_get_ubound_arf(u, m, prec);
    double d = arf_get_d(u, ARF_RND_UP);
    arb_clear(m); arf_clear(u); return d;
}
/* rigorous double lower bound of |a| (rounded down; 0 if the ball contains 0) */
double ib_abs_lower(const ball_t *a, long prec) {
    if (!acb_is_finite(a->v)) return 0.0;
    arb_t m; arf_t l; arb_init(m); arf_init(l);
    acb_abs(m, a->v, prec); arb_get_lbound_arf(l, m, prec);
    double d = arf_get_d(l, ARF_RND_DOWN);
    if (d < 0) d = 0;
    arb_clear(m); arf_clear(l); return d;
}
/* add a rigorous error radius e >= 0 to both real and imaginary parts */
void ib_add_error(ball_t *r, double e) {
    arf_t x; arf_init(x); arf_set_d(x, e); acb_add_error_arf(r->v, x); arf_clear(x);
}
/* "certainly" predicates on the real/imag parts */
int ib_re_gt(const ball_t *a, double c) { arb_t t; arb_init(t); arb_set_d(t, c); int r = arb_gt(acb_realref(a->v), t); arb_clear(t); return r; }
int ib_re_lt(const ball_t *a, double c) { arb_t t; arb_init(t); arb_set_d(t, c); int r = arb_lt(acb_realref(a->v), t); arb_clear(t); return r; }
int ib_im_ne0(const ball_t *a) { return arb_is_nonzero(acb_imagref(a->v)); }
int ib_contains_zero(const ball_t *a) { return acb_contains_zero(a->v); }
/* string out: "re_str|im_str" with Arb's [mid +/- rad]; caller frees with ib_free_str */
char *ib_get_str(const ball_t *a, long digits) {
    char *re = arb_get_str(acb_realref(a->v), digits, 0);
    char *im = arb_get_str(acb_imagref(a->v), digits, 0);
    size_t n = strlen(re) + strlen(im) + 2;
    char *s = malloc(n);
    strcpy(s, re); strcat(s, "|"); strcat(s, im);
    flint_free(re); flint_free(im);
    return s;
}
void ib_free_str(char *s) { free(s); }
/* parse back an Arb ball string pair (exact round trip of what ib_get_str wrote) */
int ib_set_str(ball_t *r, const char *re, const char *im, long prec) {
    arb_t x, y; arb_init(x); arb_init(y);
    int e1 = arb_set_str(x, re, prec), e2 = arb_set_str(y, im, prec);
    acb_set_arb_arb(r->v, x, y);
    arb_clear(x); arb_clear(y);
    return e1 || e2;
}

/* ---------------- truncated power series (length n) ---------------- */
ser_t *is_new(void) { ser_t *s = malloc(sizeof(ser_t)); acb_poly_init(s->p); return s; }
void is_free(ser_t *s) { acb_poly_clear(s->p); free(s); }
void is_set(ser_t *r, const ser_t *a) { acb_poly_set(r->p, a->p); }
/* constant series c */
void is_set_ball(ser_t *r, const ball_t *c) { acb_poly_set_acb(r->p, c->v); }
/* the variable z0 + t */
void is_set_var(ser_t *r, const ball_t *z0) { acb_poly_zero(r->p); acb_poly_set_coeff_acb(r->p, 0, z0->v); acb_poly_set_coeff_si(r->p, 1, 1); }
void is_add(ser_t *r, const ser_t *a, const ser_t *b, long n, long prec) { acb_poly_add(r->p, a->p, b->p, prec); acb_poly_truncate(r->p, n); }
void is_sub(ser_t *r, const ser_t *a, const ser_t *b, long n, long prec) { acb_poly_sub(r->p, a->p, b->p, prec); acb_poly_truncate(r->p, n); }
void is_mul(ser_t *r, const ser_t *a, const ser_t *b, long n, long prec) { acb_poly_mullow(r->p, a->p, b->p, n, prec); }
void is_scal(ser_t *r, const ser_t *a, const ball_t *c, long prec) { acb_poly_scalar_mul(r->p, a->p, c->v, prec); }
void is_neg(ser_t *r, const ser_t *a) { acb_poly_neg(r->p, a->p); }
void is_inv(ser_t *r, const ser_t *a, long n, long prec) { acb_poly_inv_series(r->p, a->p, n, prec); }
void is_div(ser_t *r, const ser_t *a, const ser_t *b, long n, long prec) { acb_poly_div_series(r->p, a->p, b->p, n, prec); }
void is_exp(ser_t *r, const ser_t *a, long n, long prec) { acb_poly_exp_series(r->p, a->p, n, prec); }
void is_get_coeff(ball_t *c, const ser_t *a, long k) { acb_poly_get_coeff_acb(c->v, a->p, k); }
long is_length(const ser_t *a) { return acb_poly_length(a->p); }
