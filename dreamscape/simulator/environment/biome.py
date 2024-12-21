import random

class Biome:
    def __init__(self, biome_type):
        self.biome_type = biome_type

        # Define biome-specific data
        self.biome_data = {
            "forest": {
                "grass": {"color": (34, 177, 76), "type": "Standard"},
                "trees": {"color": (0, 100, 0), "type": "Difficult"},
                "water": {"color": (0, 120, 255), "type": "Difficult"},
            },
            "cave": {
                "floor": {"color": (50, 50, 50), "type": "Standard"},
                "wall": {"color": (100, 100, 100), "type": "Difficult"},
                "pit": {"color": (20, 20, 20), "type": "Death"},
            },
            # Add other biomes here...
        }

    def generate_biome(self, rows, cols):
        """
        Generate the biome-specific map grid.
        """
        if self.biome_type == "forest":
            return self.generate_forest(rows, cols)
        elif self.biome_type == "cave":
            return self.generate_cave(rows, cols)
        # Add more biome methods here...
        else:
            raise ValueError(f"Biome type '{self.biome_type}' is not supported.")

    def generate_forest(self, rows, cols):
        """
        Generate a forest biome.
        """
        map_data = [["grass" for _ in range(cols)] for _ in range(rows)]
        self.add_water(map_data)
        self.add_tree_clusters(map_data)
        return map_data

    def generate_cave(self, rows, cols):
        """
        Generate a cave biome.
        """
        map_data = [["floor" for _ in range(cols)] for _ in range(rows)]
        self.add_pits(map_data)
        self.add_walls(map_data)
        return map_data

    def add_water(self, map_data):
        """
        Add connected water tiles to a forest biome.
        """
        rows, cols = len(map_data), len(map_data[0])
        start_x, start_y = random.randint(0, cols - 1), random.randint(0, rows - 1)
        steps = random.randint(rows * cols // 10, rows * cols // 5)
        x, y = start_x, start_y
        for _ in range(steps):
            map_data[y][x] = "water"
            direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            x = max(0, min(cols - 1, x + direction[0]))
            y = max(0, min(rows - 1, y + direction[1]))

    def add_tree_clusters(self, map_data):
        """
        Add tree clusters to a forest biome.
        """
        rows, cols = len(map_data), len(map_data[0])
        num_clusters = random.randint(5, 10)
        for _ in range(num_clusters):
            cluster_x = random.randint(0, cols - 1)
            cluster_y = random.randint(0, rows - 1)
            cluster_size = random.randint(5, 15)
            for _ in range(cluster_size):
                x = max(0, min(cols - 1, cluster_x + random.randint(-2, 2)))
                y = max(0, min(rows - 1, cluster_y + random.randint(-2, 2)))
                if map_data[y][x] != "water":
                    map_data[y][x] = "trees"

    def add_pits(self, map_data):
        """
        Add pits to a cave biome.
        """
        rows, cols = len(map_data), len(map_data[0])
        for _ in range(random.randint(5, 10)):
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            map_data[y][x] = "pit"

    def add_walls(self, map_data):
        """
        Add walls to a cave biome.
        """
        rows, cols = len(map_data), len(map_data[0])
        for _ in range(random.randint(20, 30)):
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            map_data[y][x] = "wall"

    def get_tile_color(self, tile_name):
        """
        Get the color for a specific tile type.
        """
        return self.biome_data[self.biome_type][tile_name]["color"]
    
    def get_tile_type(self, tile_name):
        """
        Get the terrain type for a specific tile in the current biome.
        """
        return self.biome_data[self.biome_type][tile_name]["type"]