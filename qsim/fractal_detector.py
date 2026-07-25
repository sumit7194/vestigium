import numpy as np
import matplotlib.pyplot as plt
import os

def weierstrass_fractal(x, a=0.5, b=2.0, n_terms=10, k=1.0):
    val = np.zeros_like(x)
    for n in range(n_terms):
        val += (a**n) * np.cos((b**n) * k * x)
    val = val - np.min(val)
    val = val / np.max(val)
    return val

def simulate_fractal_scattering():
    N = 16384 
    L = 300.0
    x = np.linspace(-L/2, L/2, N)
    dx = x[1] - x[0]
    k_vec = 2 * np.pi * np.fft.fftfreq(N, d=dx)

    x0 = -80.0
    p0 = 20.0
    sigma = 0.5 # Extremely narrow -> massive spread
    
    norm = 1.0 / (np.pi**0.25 * np.sqrt(sigma))
    psi = norm * np.exp(-0.5 * ((x - x0) / sigma)**2) * np.exp(1j * p0 * x)
    
    V_center = 40.0
    V_width = 25.0
    A = 50.0
    
    envelope = np.exp(- ((x - V_center) / V_width)**6)
    # High frequency fluctuating fractal boundary
    fractal_pattern = weierstrass_fractal(x, a=0.7, b=2.5, n_terms=12, k=15.0)
    V = A * fractal_pattern * envelope

    dt = 0.001 
    t_total = 8.0
    steps = int(t_total / dt)
    frames = 150
    steps_per_frame = steps // frames
    
    exp_V_half = np.exp(-0.5j * V * dt)
    exp_K = np.exp(-0.5j * (k_vec**2) * dt)
    
    psi_history = []
    snapshots = [0, 30, 80, 149]
    snapshot_names = ['fractal_initial.png', 'fractal_stage1.png', 'fractal_stage2.png', 'fractal_stage3.png']
    
    for frame in range(frames):
        psi_history.append(np.abs(psi)**2)
        
        if frame in snapshots:
            idx = snapshots.index(frame)
            plt.figure(figsize=(10, 4))
            plt.plot(x, V, 'r-', alpha=0.5, label='Fluctuating Fractal Wall $V(x)$')
            plt.plot(x, np.abs(psi)**2 * 15, 'b-', label='Spreading Wave Density $|\psi|^2$ (scaled)')
            plt.xlim(-100, 100)
            plt.ylim(0, A + 5)
            plt.xlabel('Position $x$')
            plt.ylabel('Energy / Probability Density')
            if frame == 0:
                plt.title('Initial State: Localized Particle & Fractal Detector Wall')
            else:
                plt.title(f'Wave Spreading and Interference (Stage {idx})')
            plt.legend(loc='upper right')
            plt.tight_layout()
            plt.savefig(snapshot_names[idx], dpi=150)
            plt.close()
            print(f"Saved {snapshot_names[idx]}")

        for _ in range(steps_per_frame):
            psi = psi * exp_V_half
            psi_k = np.fft.fft(psi)
            psi_k = psi_k * exp_K
            psi = np.fft.ifft(psi_k)
            psi = psi * exp_V_half

    psi_history = np.array(psi_history)
    
    plt.figure(figsize=(10, 6))
    extent = [x[0], x[-1], t_total, 0]
    plt.imshow(psi_history, aspect='auto', extent=extent, cmap='magma', 
                    origin='upper', vmax=np.max(psi_history)*0.1)
    plt.xlim(-100, 100)
    plt.xlabel('Position $x$')
    plt.ylabel('Time $t$')
    plt.title('Spreading Wave Colliding with Fractal Wall (Space-Time Heatmap)')
    plt.colorbar(label='Probability Density $|\psi(x,t)|^2$')
    plt.tight_layout()
    plt.savefig('fractal_scattering_heatmap.png', dpi=150)
    print("Saved fractal_scattering_heatmap.png")

if __name__ == '__main__':
    simulate_fractal_scattering()
