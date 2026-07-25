import numpy as np
import matplotlib.pyplot as plt

def weierstrass(x, a=0.6, b=2.5, n_terms=10, k=5.0):
    val = np.zeros_like(x)
    for n in range(n_terms):
        val += (a**n) * np.cos((b**n) * k * x)
    val = val - np.min(val)
    val = val / np.max(val)
    return val

def run_simulation(detector_type='standing'):
    # Grid parameters
    N = 8192
    L = 200.0
    x = np.linspace(-L/2, L/2, N)
    dx = x[1] - x[0]
    k_vec = 2 * np.pi * np.fft.fftfreq(N, d=dx)

    # Initial state (very narrow Gaussian)
    x0 = -60.0
    p0 = 12.0
    sigma_init = 0.5
    norm = 1.0 / (np.pi**0.25 * np.sqrt(sigma_init))
    psi = norm * np.exp(-0.5 * ((x - x0) / sigma_init)**2) * np.exp(1j * p0 * x)

    # Detector boundary and potential
    x_det = 20.0
    V = np.zeros_like(x)
    detector_mask = x >= x_det
    
    if detector_type == 'standing':
        # Tightly knit standing wave (particles)
        k_det = 40.0
        # Make the standing wave potential
        V[detector_mask] = 40.0 * (np.sin(k_det * x[detector_mask])**2)
    else:
        # Fluctuating fractal wave
        fractal = weierstrass(x, a=0.7, b=2.5, n_terms=10, k=15.0)
        V[detector_mask] = 40.0 * fractal[detector_mask]

    # Time evolution parameters
    dt = 0.001
    t_collapse = 6.5
    t_end = 8.0
    
    steps_to_collapse = int(t_collapse / dt)
    steps_post_collapse = int((t_end - t_collapse) / dt)

    # Operators
    exp_V_half = np.exp(-0.5j * V * dt)
    exp_K = np.exp(-0.5j * (k_vec**2) * dt)

    # We will record states at 5 key stages
    # Stage 0: Initial
    # Stage 1: Spreading (t = 3.2)
    # Stage 2: Pre-collapse (t = 6.5, before collapse)
    # Stage 3: Collapse (t = 6.5, after projection)
    # Stage 4: Post-collapse spreading (t = 8.0)
    stages = {}
    stages['t0'] = (psi.copy(), 0.0)

    # Evolve to t = 3.2
    for _ in range(int(3.2 / dt)):
        psi = psi * exp_V_half
        psi_k = np.fft.fft(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft(psi_k)
        psi = psi * exp_V_half
    stages['t_mid'] = (psi.copy(), 3.2)

    # Evolve to t = 6.5 (pre-collapse)
    for _ in range(int((t_collapse - 3.2) / dt)):
        psi = psi * exp_V_half
        psi_k = np.fft.fft(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft(psi_k)
        psi = psi * exp_V_half
    stages['t_pre'] = (psi.copy(), t_collapse)

    # Perform Stochastic Collapse
    # 1. Compute probability density in the detector region
    prob_in_detector = np.abs(psi[detector_mask])**2
    prob_sum = np.sum(prob_in_detector)
    
    if prob_sum > 0:
        # Sample detection position based on probability density in detector
        pdf = prob_in_detector / prob_sum
        x_choices = x[detector_mask]
        x_collapse = np.random.choice(x_choices, p=pdf)
    else:
        # Fallback if wave hasn't reached it (should not happen with our parameters)
        x_collapse = x_det + 10.0

    # 2. Project wave function onto a narrow collapsed state
    sigma_det = 0.6  # Size of detector particle localization
    norm_collapsed = 1.0 / (np.pi**0.25 * np.sqrt(sigma_det))
    psi = norm_collapsed * np.exp(-0.5 * ((x - x_collapse) / sigma_det)**2) * np.exp(1j * p0 * x)
    stages['t_post'] = (psi.copy(), t_collapse)

    # Evolve to t = 8.0
    for _ in range(steps_post_collapse):
        psi = psi * exp_V_half
        psi_k = np.fft.fft(psi)
        psi_k = psi_k * exp_K
        psi = np.fft.ifft(psi_k)
        psi = psi * exp_V_half
    stages['t_end'] = (psi.copy(), t_end)

    # Generate a beautiful 5-panel layout
    fig, axes = plt.subplots(5, 1, figsize=(11, 12), sharex=True)
    
    keys = ['t0', 't_mid', 't_pre', 't_post', 't_end']
    labels = [
        "Stage 1: Initial Localized Wave Packet ($t=0.0$)",
        "Stage 2: Free Spreading in Space ($t=3.2$) - Envelope Widens, Wave Oscillates",
        "Stage 3: Overlap with Detector Boundary ($t=6.5$) - Pre-Collapse state",
        "Stage 4: Stochastic Wave Function Collapse ($t=6.5$) - Instantly Localized at $x_c = {:.2f}$".format(x_collapse),
        "Stage 5: Post-Collapse Dispersion ($t={:.1f}$) - Spreading resumes from detection site".format(t_end)
    ]
    
    for i, key in enumerate(keys):
        ax = axes[i]
        curr_psi, curr_t = stages[key]
        density = np.abs(curr_psi)**2
        real_part = np.real(curr_psi)
        
        # Shade the probability density envelope
        ax.fill_between(x, density, color='#1f77b4', alpha=0.3, label='Probability Envelope $|\psi|^2$')
        
        # Plot the real part of the wave (the phase wiggles)
        ax.plot(x, real_part, color='#1f77b4', lw=1.2, label='Schrödinger Wave $Re(\psi)$')
        
        # Plot the detector background
        if detector_type == 'standing':
            # Draw the standing wave grating at the bottom of the axis
            ax.plot(x[detector_mask], V[detector_mask] / 80.0, color='red', alpha=0.4, lw=0.8, label='Detector particles (Standing Wave)')
        else:
            # Draw the fluctuating fractal boundary
            ax.plot(x[detector_mask], V[detector_mask] / 80.0, color='purple', alpha=0.4, lw=0.8, label='Detector particles (Fractal)')
            
        ax.axvline(x_det, color='black', linestyle='--', alpha=0.5, label='Detector Boundary')
        
        ax.set_xlim(-90, 80)
        ax.set_ylim(-1.5, 1.5)
        ax.set_ylabel('Amplitude')
        ax.set_title(labels[i], fontsize=10, pad=5)
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)
            
    axes[-1].set_xlabel('Position $x$')
    
    detector_title = "Standing Wave Grating" if detector_type == 'standing' else "Fluctuating Fractal Wall"
    fig.suptitle(f"Quantum Measurement Simulation: Spreading & Collapse ({detector_title})", fontsize=13, weight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    filename = f"{detector_type}_collapse.png"
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved {filename}")

if __name__ == '__main__':
    run_simulation('standing')
    run_simulation('fractal')
