import numpy as np

def pso_path(start: tuple, end: tuple, obstacles: list, n_particles=30, iterations=50):
    """
    Particle Swarm Optimization path from start to end avoiding obstacles.
    Returns list of waypoints.
    """
    start = np.array(start, dtype=float)
    end   = np.array(end,   dtype=float)

    particles  = [start + (end - start) * t for t in np.linspace(0, 1, 5)]
    velocities = [np.random.uniform(-1, 1, 2) for _ in particles]
    best_path  = particles[:]

    def cost(path):
        total = sum(np.linalg.norm(path[i+1] - path[i]) for i in range(len(path)-1))
        for pt in path:
            for obs in obstacles:
                obs = np.array(obs)
                if np.linalg.norm(pt - obs) < 5:
                    total += 100
        return total

    global_best = best_path[:]

    for _ in range(iterations):
        for i in range(1, len(particles) - 1):
            r1, r2 = np.random.rand(), np.random.rand()
            velocities[i] = (0.5 * velocities[i]
                             + 1.5 * r1 * (best_path[i] - particles[i])
                             + 1.5 * r2 * (global_best[i] - particles[i]))
            particles[i] += velocities[i]
            if cost(particles) < cost(global_best):
                global_best = particles[:]

    return [pt.tolist() for pt in global_best]
