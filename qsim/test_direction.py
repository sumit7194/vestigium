import numpy as np

def test():
    Nx = 512
    Lx = 160.0
    x = np.linspace(-Lx/2, Lx/2, Nx)
    dx = x[1] - x[0]
    
    p0 = 6.0  # Below Nyquist limit of ~10.05
    x0 = -50.0
    sigma = 3.0
    psi = np.exp(-0.5 * ((x - x0)/sigma)**2) * np.exp(1j * p0 * x)
    
    k = 2 * np.pi * np.fft.fftfreq(Nx, d=dx)
    psi_k = np.fft.fft(psi)
    
    peak_idx = np.argmax(np.abs(psi_k))
    print(f"Nyquist limit: {np.pi/dx:.2f}")
    print(f"Peak wavenumber in FFT: k = {k[peak_idx]:.2f}")
    
    # Evolve
    dt = 0.002
    t_end = 5.0
    exp_K = np.exp(-0.5j * (k**2) * dt)
    for _ in range(int(t_end / dt)):
        psi_k = np.fft.fft(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft(psi_k)
        
    print(f"Position at t={t_end}: x = {x[np.argmax(np.abs(psi)**2)]:.2f}")

if __name__ == '__main__':
    test()
