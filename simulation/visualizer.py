# Pygame visualizer — run standalone for animated sim view
# pip install pygame
# python simulation/visualizer.py

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from simulation.environment import run_simulation
from simulation.park_map    import ZONES, HUB_POSITION, PARK_WIDTH, PARK_HEIGHT

SCALE  = 4
W      = PARK_WIDTH  * SCALE
H      = PARK_HEIGHT * SCALE

ZONE_COLORS = {
    "grass":  (46, 160, 67),
    "garden": (63, 185, 80),
    "paved":  (139, 148, 158),
    "water":  (88, 166, 255),
}

def run_visualizer():
    if not PYGAME_AVAILABLE:
        print("pygame not installed. Run: pip install pygame")
        return

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("🌿 Swarm Park Guardian")
    clock  = pygame.time.Clock()
    log    = run_simulation(300)
    font   = pygame.font.SysFont("monospace", 10)

    for frame in log:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((13, 17, 23))

        for zone in ZONES:
            color = ZONE_COLORS.get(zone["type"], (50, 50, 50))
            pygame.draw.rect(screen, color,
                             (zone["x"]*SCALE, zone["y"]*SCALE,
                              zone["width"]*SCALE, zone["height"]*SCALE), 0)
            pygame.draw.rect(screen, (48, 54, 61),
                             (zone["x"]*SCALE, zone["y"]*SCALE,
                              zone["width"]*SCALE, zone["height"]*SCALE), 1)
            label = font.render(zone["name"], True, (255,255,255))
            screen.blit(label, (zone["x"]*SCALE+4, zone["y"]*SCALE+4))

        # Hub
        hx, hy = HUB_POSITION[0]*SCALE, HUB_POSITION[1]*SCALE
        pygame.draw.polygon(screen, (188,140,255),
                            [(hx, hy-10),(hx+8,hy+6),(hx-8,hy+6)])

        # Drones
        role_colors = {
            "scout": (255,215,0), "cleaner": (240,136,62),
            "trimmer": (63,185,80), "waterer": (88,166,255), "patrol": (248,81,73)
        }
        for d in frame["drones"]:
            px = int(d["position"][0] * SCALE)
            py = int(d["position"][1] * SCALE)
            color = role_colors.get(d["role"], (200,200,200))
            pygame.draw.circle(screen, color, (px, py), 6)
            lbl = font.render(f"D{d['id']}", True, (255,255,255))
            screen.blit(lbl, (px+7, py-5))

        info = font.render(
            f"Tick: {frame['tick']}  Done: {frame['done']}  Queue: {frame['queue']}",
            True, (255,255,255)
        )
        screen.blit(info, (10, H-20))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    run_visualizer()
