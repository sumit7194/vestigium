import numpy as np
import matplotlib.pyplot as plt

def weierstrass(y, a=0.6, b=2.5, n_terms=10, k=5.0):
    val = np.zeros_like(y)
    for n in range(n_terms):
        val += (a**n) * np.cos((b**n) * k * y)
    val = val - np.min(val)
    val = val / np.max(val)
    return val

def run_simulation_2d(detector_type='standing'):
    # Grid parameters
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

    # Initial state: localized in x, narrow in y to force rapid transverse spreading
    x0 = -50.0
    y0 = 0.0
    p0_x = 6.0   # Prevent aliasing
    p0_y = 0.0
    sigma_x = 3.0
    sigma_y = 1.0  # Narrower in y -> huge transverse spreading!
    
    # Normalized Gaussian wave packet in 2D
    norm = 1.0 / (np.sqrt(np.pi * sigma_x * sigma_y))
    psi = norm * np.exp(-0.5 * (((X - x0)/sigma_x)**2 + ((Y - y0)/sigma_y)**2)) * np.exp(1j * (p0_x * X + p0_y * Y))

    # Detector wall setup
    x_det_base = 20.0
    
    if detector_type == 'standing':
        # Standing wave surface profile (high frequency)
        k_surf = 1.5
        surface_profile = x_det_base + 4.0 * np.sin(k_surf * y)
    else:
        # Fractal surface profile
        fractal = weierstrass(y, a=0.6, b=2.5, n_terms=8, k=1.0)
        surface_profile = x_det_base + 6.0 * (fractal - 0.5)

    # Potential is 0 in vacuum, and very high (100.0) inside the wall
    V = np.zeros_like(X)
    wall_mask = X >= surface_profile
    V[wall_mask] = 100.0

    # Time evolution parameters
    dt = 0.002
    t_mid = 5.5
    t_collapse = 11.0
    t_end = 13.0
    
    steps_to_mid = int(t_mid / dt)
    steps_to_collapse = int((t_collapse - t_mid) / dt)
    steps_post_collapse = int((t_end - t_collapse) / dt)

    # Split-step Fourier operators
    exp_V_half = np.exp(-0.5j * V * dt)
    exp_K = np.exp(-0.5j * (KX**2 + KY**2) * dt)

    stages = {}
    stages['t0'] = psi.copy()

    # Step to t_mid
    for _ in range(steps_to_mid):
        psi = psi * exp_V_half
        psi_k = np.fft.fft2(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft2(psi_k)
        psi = psi * exp_V_half
    stages['t_mid'] = psi.copy()

    # Step to t_collapse
    for _ in range(steps_to_collapse):
        psi = psi * exp_V_half
        psi_k = np.fft.fft2(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft2(psi_k)
        psi = psi * exp_V_half
    stages['t_pre'] = psi.copy()

    # Stochastic collapse at the surface
    prob_density = np.abs(psi)**2
    prob_in_wall = prob_density * wall_mask
    prob_sum = np.sum(prob_in_wall)
    
    if prob_sum > 0:
        pdf = prob_in_wall.flatten() / prob_sum
        indices = np.arange(Nx * Ny)
        choice_idx = np.random.choice(indices, p=pdf)
        ix, iy = np.unravel_index(choice_idx, (Nx, Ny))
        x_c, y_c = X[ix, iy], Y[ix, iy]
    else:
        x_c, y_c = x_det_base + 1.0, 0.0

    # Project to microscopic state
    sigma_det = 1.0
    norm_collapsed = 1.0 / (np.sqrt(np.pi * (sigma_det**2)))
    psi = norm_collapsed * np.exp(-0.5 * (((X - x_c)/sigma_det)**2 + ((Y - y_c)/sigma_det)**2)) * np.exp(1j * p0_x * X)
    stages['t_post'] = psi.copy()

    # Evolve to t_end
    for _ in range(steps_post_collapse):
        psi = psi * exp_V_half
        psi_k = np.fft.fft2(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft2(psi_k)
        psi = psi * exp_V_half
    stages['t_end'] = psi.copy()

    # Save each stage as a separate high-resolution image
    keys = ['t0', 't_mid', 't_pre', 't_post', 't_end']
    titles = [
        "Stage 1: Initial Wave (t=0.0)",
        "Stage 2: Transverse Spreading (t=5.5)",
        "Stage 3: Overlap at Wall (t=11.0, Pre-Collapse)",
        "Stage 4: Stochastic Collapse (t=11.0, Post-Collapse)",
        "Stage 5: Post-Collapse Dispersion (t=13.0)"
    ]
    
    for i, key in enumerate(keys):
        plt.figure(figsize=(8, 6.5))
        curr_psi = stages[key]
        
        # Plot Re(psi)
        plt.imshow(np.real(curr_psi).T, extent=[-Lx/2, Lx/2, -Ly/2, Ly/2], 
                   origin='lower', cmap='RdBu', aspect='equal', vmin=-0.15, vmax=0.15)
        
        # Draw the solid detector wall boundary
        plt.plot(surface_profile, y, 'k-', lw=1.5, label='Wall Surface')
        plt.fill_betweenx(y, surface_profile, Lx/2, color='gray', alpha=0.3)
        
        # Label the detection point
        if i >= 3:
            plt.plot(x_c, y_c, 'g*', markersize=12, markeredgecolor='black', markeredgewidth=1.5, label='Detection Point')
            plt.annotate("Detection Site", xy=(x_c, y_c), xytext=(x_c - 45, y_c + 6),
                        arrowprops=dict(facecolor='black', arrowstyle='->'),
                        fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.8))
            
        detector_title = "High-Frequency Grating" if detector_type == 'standing' else "Fractal Surface"
        plt.title(f"{titles[i]}\n({detector_title})", fontsize=12, fontweight='bold')
        plt.xlim(-70, 70)
        plt.ylim(-60, 60)
        plt.ylabel('Transverse Position $y$')
        plt.xlabel('Propagation Position $x$')
        plt.tight_layout()
        
        filename = f"2d_{detector_type}_stage_{i+1}.png"
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"Saved {filename}")

if __name__ == '__main__':
    run_simulation_2d('standing')
    run_simulation_2d('fractal')
