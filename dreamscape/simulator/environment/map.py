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

    # Initialize the map and biome
    biome = Biome(biome_input)
    game_map = GenerateMap(rows, cols, GRID_SIZE, font, COLORS, biome)

    # Instructions
    print("Instructions:")
    print("- Type a square (e.g., B3) to query it.")
    print("- Type 'NEXT' to regenerate the map.")
    print("- Close the Pygame window to exit.")

    running = True
    user_input = ""  # Store typed input for querying

    while running:
        screen.fill((0, 0, 0))  # Clear the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle typing input for queries
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter key to submit input
                    if user_input.upper() == "NEXT":
                        print("Regenerating map...")
                        game_map = GenerateMap(rows, cols, GRID_SIZE, font, COLORS, biome)
                    else:
                        query_result = game_map.query_terrain(user_input.upper())
                        print(query_result)
                    user_input = ""  # Reset input after processing
                elif event.key == pygame.K_BACKSPACE:  # Backspace to delete
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode.upper()  # Add typed character

            # Handle map interaction events (panning, zooming)
            game_map.handle_events(event)

        # Update the game map (camera)
        game_map.update()

        # Draw the map
        game_map.draw_grid(screen)

        # Display current input on the screen
        input_label = font.render(f"Input: {user_input}", True, COLORS["label"])
        screen.blit(input_label, (10, screen.get_height() - 30))

        # Refresh the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
