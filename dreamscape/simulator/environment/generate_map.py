import pygame
import string


class GenerateMap:
    def __init__(self, rows, cols, grid_size, font, colors, biome):
        self.rows = rows
        self.cols = cols
        self.grid_size = grid_size
        self.font = font
        self.colors = colors
        self.biome = biome

        # Camera and zoom settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0

        # Generate initial map grid
        self.map_data = [[None for _ in range(cols)] for _ in range(rows)]
        self.generate_biome()

    def generate_biome(self):
        """
        Populate the map with biome-specific tiles using the Biome class and define spawn zones.
        """
        base_map = self.biome.generate_biome(self.rows, self.cols)
        self.map_data = [
            [
                {
                    "name": f"{self.get_row_label(row)}{col + 1}",
                    "type": base_map[row][col],
                    "color": self.biome.get_tile_color(base_map[row][col]),
                    "properties": self.biome.get_tile_type(base_map[row][col]),
                }
                for col in range(self.cols)
            ]
            for row in range(self.rows)
        ]

        # Determine and apply spawn zones
        self.apply_spawn_zones()

    def get_row_label(self, row):
        """
        Generate row labels (e.g., A-Z, AA-ZZ) for rows beyond the alphabet limit.
        """
        letters = string.ascii_uppercase
        if row < 26:
            return letters[row]
        else:
            label = ""
            while row >= 0:
                label = letters[row % 26] + label
                row = row // 26 - 1
            return label

    def apply_spawn_zones(self):
        """
        Define spawn zones on the longest side of the map.
        """
        if self.rows >= self.cols:  # Vertical dominance
            good_spawn = range(0, 2)  # Top 2 rows
            bad_spawn = range(self.rows - 2, self.rows)  # Bottom 2 rows

            for row in good_spawn:
                for col in range(self.cols):
                    self.map_data[row][col]["properties"] = "good_spawn"

            for row in bad_spawn:
                for col in range(self.cols):
                    self.map_data[row][col]["properties"] = "bad_spawn"
        else:  # Horizontal dominance
            good_spawn = range(0, 2)  # Left 2 columns
            bad_spawn = range(self.cols - 2, self.cols)  # Right 2 columns

            for row in range(self.rows):
                for col in good_spawn:
                    self.map_data[row][col]["properties"] = "good_spawn"

                for col in bad_spawn:
                    self.map_data[row][col]["properties"] = "bad_spawn"

    def handle_events(self, event):
        """
        Handle zooming and panning events.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click to start dragging
            self.dragging = True
            self.drag_start = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # Stop dragging
            self.dragging = False

        if event.type == pygame.MOUSEWHEEL:  # Scroll wheel to zoom
            self.zoom += event.y * 0.1
            self.zoom = max(0.5, min(2.0, self.zoom))  # Clamp zoom level

    def update(self):
        """
        Update camera position when dragging.
        """
        if hasattr(self, "dragging") and self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx, dy = mouse_x - self.drag_start[0], mouse_y - self.drag_start[1]
            self.camera_x -= dx
            self.camera_y -= dy
            self.drag_start = (mouse_x, mouse_y)

    def draw_grid(self, screen):
        """
        Draw the grid and tiles on the screen.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate position and size
                x = col * self.grid_size * self.zoom - self.camera_x
                y = row * self.grid_size * self.zoom - self.camera_y
                size = self.grid_size * self.zoom

                # Skip drawing tiles outside the visible screen
                if x + size < 0 or y + size < 0 or x > screen.get_width() or y > screen.get_height():
                    continue

                # Extract tile type and get its color
                tile = self.map_data[row][col]
                tile_type = tile["type"]  # Extract the "type" field
                tile_color = self.biome.get_tile_color(tile_type)

                # Draw tile
                pygame.draw.rect(screen, tile_color, (x, y, size, size))

                # Draw grid lines
                pygame.draw.rect(screen, self.colors["grid"], (x, y, size, size), 1)

        # Draw labels
        for row in range(self.rows):
            label = self.font.render(self.get_row_label(row), True, self.colors["label"])
            screen.blit(label, (5, row * self.grid_size * self.zoom - self.camera_y + 10))
        for col in range(self.cols):
            label = self.font.render(str(col + 1), True, self.colors["label"])
            screen.blit(label, (col * self.grid_size * self.zoom - self.camera_x + 10, 5))

    def query_terrain(self, cell):
        """
        Query the terrain type of a cell (e.g., "B3").
        """
        try:
            col = int(cell[1:]) - 1  # Convert column (e.g., "3" -> 2)
            row = self.get_row_index(cell[0].upper())  # Convert row (e.g., "B" -> 1)
            tile = self.map_data[row][col]  # Get the tile dictionary
            return f"{tile['name']}: {tile['type']} ({tile['properties']})"
        except (IndexError, ValueError):
            return f"{cell}: Invalid cell"

    def get_row_index(self, label):
        """
        Convert a row label (e.g., "A", "AA") back to its numeric index.
        """
        letters = string.ascii_uppercase
        index = 0
        for char in label:
            index = index * 26 + letters.index(char) + 1
        return index - 1
