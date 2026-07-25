import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_standing_wave_scattering():
    # Grid parameters - much higher resolution for tightly knit wall
    N = 16384
    L = 300.0
    x = np.linspace(-L/2, L/2, N)
    dx = x[1] - x[0]
    k_vec = 2 * np.pi * np.fft.fftfreq(N, d=dx)

    # Wave packet parameters (Gaussian)
    x0 = -80.0
    p0 = 20.0 # High initial momentum
    sigma = 0.5 # Extremely narrow initial width -> causes rapid quantum spreading
    
    # Normalize the initial wave packet
    norm = 1.0 / (np.pi**0.25 * np.sqrt(sigma))
    psi = norm * np.exp(-0.5 * ((x - x0) / sigma)**2) * np.exp(1j * p0 * x)
    
    # Standing wave potential parameters (acting as the tightly-knit detector)
    V_center = 40.0
    V_width = 25.0
    A = 50.0 # Strong potential barrier amplitude
    k_standing = 60.0 # Extremely high spatial frequency (tight-knit particles)
    
    # Create the standing wave potential localized on the right
    envelope = np.exp(- ((x - V_center) / V_width)**6)
    V = A * (np.cos(k_standing * x)**2) * envelope

    # Time evolution parameters
    dt = 0.001
    t_total = 8.0
    steps = int(t_total / dt)
    frames = 150
    steps_per_frame = steps // frames
    
    # Split-step Fourier operators
    exp_V_half = np.exp(-0.5j * V * dt)
    exp_K = np.exp(-0.5j * (k_vec**2) * dt)
    
    psi_history = []
    
    snapshots = [0, 30, 80, 149]
    snapshot_names = ['standing_initial.png', 'standing_stage1.png', 'standing_stage2.png', 'standing_stage3.png']
    
    for frame in range(frames):
        psi_history.append(np.abs(psi)**2)
        
        if frame in snapshots:
            idx = snapshots.index(frame)
            plt.figure(figsize=(10, 4))
            plt.plot(x, V, 'r-', alpha=0.5, label='Entangled Wall Potential $V(x)$')
            # Scale psi for visibility on the same plot
            plt.plot(x, np.abs(psi)**2 * 15, 'b-', label='Spreading Wave Density $|\psi|^2$ (scaled)')
            plt.xlim(-100, 100)
            plt.ylim(0, A + 5)
            plt.xlabel('Position $x$')
            plt.ylabel('Energy / Probability Density')
            if frame == 0:
                plt.title('Initial State: Localized Particle & Tightly-Knit Detector Wall')
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
    
    # Space-Time Density plot
    plt.figure(figsize=(10, 6))
    extent = [x[0], x[-1], t_total, 0]
    plt.imshow(psi_history, aspect='auto', extent=extent, cmap='magma', 
                    origin='upper', vmax=np.max(psi_history)*0.1)
    plt.xlim(-100, 100)
    plt.xlabel('Position $x$')
    plt.ylabel('Time $t$')
    plt.title('Spreading Wave Colliding with Detector Wall (Space-Time Heatmap)')
    plt.colorbar(label='Probability Density $|\psi(x,t)|^2$')
    plt.tight_layout()
    plt.savefig('standing_wave_scattering_heatmap.png', dpi=150)
    print("Saved standing_wave_scattering_heatmap.png")

if __name__ == '__main__':
    simulate_standing_wave_scattering()
