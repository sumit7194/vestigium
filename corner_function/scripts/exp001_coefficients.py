"""
EXP-001, part 2: decompose the collapse order by order in the smooth-limit expansion,
and normalise the interacting-theory data. Sources named per line.

a(theta) = sum_{p>=1} sigma^{(p-1)} (theta-pi)^{2p}     [BWK PRB 93,045131 eq. I.4 notation]
Holographic Einstein exact ratios sigma^{(p)}/C_T, p=0..5   [BWK eq. V.6]
Free complex boson and Dirac fermion sigma^{(p)}, alpha=1   [Helmes et al PRB 94,125142 Tables 3,4; sigma, sigma' exact]
C_T: complex boson = Dirac = 3/(16 pi^2)                      [Osborn-Petkou, as quoted in Helmes et al Sec. II]
kappa: complex boson 0.0794, Dirac 0.0722                     [Casini-Huerta-Leitao NPB 814 (2009) Table 1]
ECG: sigma=(1-3mu)sigma_E, sigma'=(1-33mu/4)sigma_E', kappa=(1-123mu/20)kappa_E, C_T=(1-3mu)C_T^E  [BCV JHEP04(2021)145 eqs 295-297]
"""
from math import pi, gamma, sqrt
CT = 3/(16*pi**2)
holo = [pi**2/24, 5/192, 37/(1536*pi**2), 195/(8192*pi**4), 3133/(131072*pi**6), 25233/(1048576*pi**8)]
boson = [1/128, (20+3*pi**2)/(9216*pi**2), 5.34655497e-5, 5.40160621e-6, 5.45758486e-7, 5.51156763e-8, 5.57181927e-9, 5.63580458e-10]
fermi = [1/128, (16+3*pi**2)/(9216*pi**2), 4.8129970e-5, 4.8552317e-6, 4.9173353e-7, 4.9777097e-8, 5.0411447e-9]
kap_b, kap_f = 0.0794, 0.0722
kapE_over_CT = pi**2*gamma(0.75)**4/6
print("order p | holo sigma^(p)/C_T | boson/C_T  (dev%) | fermion/C_T (dev%) | asymptote 2kappa/pi^(2p+3)/C_T: boson, fermion, holo")
for p in range(6):
    hb = boson[p]/CT; hf = fermi[p]/CT; hh = holo[p]
    ab = 2*kap_b/pi**(2*p+3)/CT; af = 2*kap_f/pi**(2*p+3)/CT; ah = 2*kapE_over_CT/pi**(2*p+3)
    print(f"{p:7d} | {hh:16.6e} | {hb:10.6e} ({(hb/hh-1)*100:+6.2f}) | {hf:10.6e} ({(hf/hh-1)*100:+6.2f}) | {ab:.4e} {af:.4e} {ah:.4e}")
print("\nratio sigma^(p) / [2 kappa / pi^(2p+3)] (should -> 1 if radius of convergence is pi):")
for p in range(6):
    print(f"  p={p}: boson {boson[p]/(2*kap_b/pi**(2*p+3)):.4f}  fermion {fermi[p]/(2*kap_f/pi**(2*p+3)):.4f}  holo {holo[p]/(2*kapE_over_CT/pi**(2*p+3)):.4f}")

print("\n---- ECG at the t4 = +4 and t4 = -4 limits (BCV 2021: mu=+0.00312 <-> t4=+4, mu=-0.00322 <-> t4=-4) ----")
for mu, t4 in [(0.00312, +4), (-0.00322, -4)]:
    k = kapE_over_CT*(1-123*mu/20)/(1-3*mu)
    s1 = (5/192)*(1-33*mu/4)/(1-3*mu)
    s2 = holo[2]*(1-2673*mu/296)/(1-3*mu)
    print(f"mu={mu:+.5f} (t4={t4:+d}): kappa/C_T={k:.4f} ({(k/kapE_over_CT-1)*100:+.2f}% vs Einstein) ; sigma'/C_T={s1:.6f} ({(s1/(5/192)-1)*100:+.2f}%) ; sigma''/C_T={s2:.4e} ({(s2/holo[2]-1)*100:+.2f}%)")
print(f"free scalar (t4=+4): kappa/C_T={kap_b/CT:.4f} ({(kap_b/CT/kapE_over_CT-1)*100:+.2f}%), sigma'/C_T={boson[1]/CT:.6f} ({(boson[1]/CT/(5/192)-1)*100:+.2f}%)")
print(f"free fermion (t4=-4): kappa/C_T={kap_f/CT:.4f} ({(kap_f/CT/kapE_over_CT-1)*100:+.2f}%), sigma'/C_T={fermi[1]/CT:.6f} ({(fermi[1]/CT/(5/192)-1)*100:+.2f}%)")

print("\n---- Interacting O(N) at theta=pi/2, von Neumann (n=1) ----")
# C_T/(N C_T^free) from Kos-Poland-Simmons-Duffin JHEP 1406:091 Table 3: N=1 0.946600(+22-15), N=2 0.94365(+13-10), N=3 0.94418(+43-36)
CTs = 3/(32*pi**2)
cN = {1:0.946600, 2:0.94365, 3:0.94418}
# a(pi/2)/C_T as quoted: BMW PRL Table 1: Ising 1.36(14), XY 1.3(1), Heis 1.3(1); BWK Table 1: all three 1.3(1)
for N, r, dr in [(1,1.36,0.14),(2,1.3,0.1),(3,1.3,0.1)]:
    CTN = N*cN[N]*CTs
    print(f"O({N}): C_T={CTN:.6f}  quoted a1(pi/2)/C_T={r}({dr}) -> implied a1(pi/2)={r*CTN:.5f} +- {dr*CTN:.5f} ; vs N x free real scalar a1(pi/2)={N*0.01183:.5f} ; bound {1.1402*CTN:.5f}")
print("holographic 1.2220, fermion 1.2259, real scalar 1.2454, bound 1.1402 (all exact/4-digit)")

print("\n---- Renyi n=2 at theta=pi/2 (NOT part of the n=1 collapse; sigma_2/C_T is not universal) ----")
# Ngai et al 2025 (2512.00382): Ising 4 corners s=0.020(1); Gaussian 4 corners s=0.02567 exact (0.025(1) QMC)
# Liao et al PRB 110,235111 (2024): O(3) square 4 corners s=0.080(3); honeycomb/square ratio 1.17(5) vs free boson 1.3231
a2_ising, da2 = 0.020/4, 0.001/4
a2_free = 0.02567/4
a2_O3, da3 = 0.080/4, 0.003/4
print(f"Ising  a2(pi/2)={a2_ising:.5f}({da2:.5f}) /C_T = {a2_ising/(cN[1]*CTs):.3f} +- {da2/(cN[1]*CTs):.3f}")
print(f"free real scalar a2(pi/2)={a2_free:.5f} /C_T = {a2_free/CTs:.3f}   (BMW Table 1 quotes 0.674 for the free scalar)")
print(f"O(3)   a2(pi/2)={a2_O3:.5f}({da3:.5f}) /C_T = {a2_O3/(3*cN[3]*CTs):.3f} +- {da3/(3*cN[3]*CTs):.3f}   vs 3 free scalars a2={3*a2_free:.5f}")
print(f"old NLCE (BMW Table 1) a2/C_T: Ising 0.62(6), O(2) 0.62(6), O(3) 0.61(6)")
