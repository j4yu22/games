import pygame
from generate_map import GenerateMap
from biome import Biome
import threading

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 40
COLORS = {
    "grid": (0, 0, 0),  # Black grid lines
    "label": (255, 255, 255)  # White for labels
}

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Biome Map Generator")
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

def main():
    # Prompt user for map size and biome
    size_input = input("Select map size (small, medium, large): ").strip().lower()
    size_ranges = {"small": (10, 15), "medium": (20, 25), "large": (30, 35)}
    if size_input not in size_ranges:
        print("Invalid size. Defaulting to small.")
        size_input = "small"
    rows, cols = size_ranges[size_input]

    biome_input = input("Select biome (forest, cave, desert, tundra, salt_flat, marsh, canyon): ").strip().lower()
    valid_biomes = ["forest", "cave", "desert", "tundra", "salt_flat", "marsh", "canyon"]
    if biome_input not in valid_biomes:
        print("Invalid biome. Defaulting to forest.")
        biome_input = "forest"

    # Generate map and biome
    biome = Biome(biome_input)
    game_map = GenerateMap(rows, cols, GRID_SIZE, font, COLORS, biome)

    def query_loop():
        """
        Separate thread for querying squares from the console.
        """
        while True:
            cell = input("Enter a square to query (e.g., B3): ").strip()
            if cell.lower() == "exit":
                print("Exiting query loop.")
                break
            result = game_map.query_terrain(cell)
            print(result)

    # Start query loop in a separate thread
    query_thread = threading.Thread(target=query_loop, daemon=True)
    query_thread.start()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle zoom and pan events
            game_map.handle_events(event)

        # Update map logic (e.g., panning)
        game_map.update()

        # Draw map
        screen.fill((0, 0, 0))  # Clear screen
        game_map.draw_grid(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
if __name__ == "__main__":
    main()
