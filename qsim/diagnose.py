import numpy as np

def diagnose():
    Nx = 512
    Ny = 512
    Lx = 160.0
    Ly = 160.0
    x = np.linspace(-Lx/2, Lx/2, Nx)
    y = np.linspace(-Ly/2, Ly/2, Ny)
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    X, Y = np.meshgrid(x, y, indexing='ij')

    k_x = 2 * np.pi * np.fft.fftfreq(Nx, d=dx)
    k_y = 2 * np.pi * np.fft.fftfreq(Ny, d=dy)
    KX, KY = np.meshgrid(k_x, k_y, indexing='ij')

    x0 = -50.0
    y0 = 0.0
    p0_x = 12.0
    p0_y = 0.0
    sigma_x = 3.0
    sigma_y = 1.0
    
    norm = 1.0 / (np.sqrt(np.pi * sigma_x * sigma_y))
    psi = norm * np.exp(-0.5 * (((X - x0)/sigma_x)**2 + ((Y - y0)/sigma_y)**2)) * np.exp(1j * (p0_x * X + p0_y * Y))

    x_det_base = 20.0
    k_surf = 1.5
    surface_profile = x_det_base + 4.0 * np.sin(k_surf * y)
    V = np.zeros_like(X)
    wall_mask = X >= surface_profile
    V[wall_mask] = 100.0

    dt = 0.002
    exp_V_half = np.exp(-0.5j * V * dt)
    exp_K = np.exp(-0.5j * (KX**2 + KY**2) * dt)

    def print_max(t_val, psi_val):
        density = np.abs(psi_val)**2
        idx = np.argmax(density)
        ix, iy = np.unravel_index(idx, density.shape)
        print(f"t={t_val:.1f}: Max density at x={X[ix, iy]:.2f}, y={Y[ix, iy]:.2f}, max_val={density[ix, iy]:.4f}")

    print_max(0.0, psi)

    # Step to t = 2.5
    for _ in range(int(2.5 / dt)):
        psi = psi * exp_V_half
        psi_k = np.fft.fft2(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft2(psi_k)
        psi = psi * exp_V_half
    print_max(2.5, psi)

    # Step to t = 5.5
    for _ in range(int((5.5 - 2.5) / dt)):
        psi = psi * exp_V_half
        psi_k = np.fft.fft2(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft2(psi_k)
        psi = psi * exp_V_half
    print_max(5.5, psi)

if __name__ == '__main__':
    diagnose()
