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
        self.add_pond(map_data)
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

    def add_pond(self, map_data):
        """
        Add connected water tiles to a forest biome, scaled dynamically with map size, with 30% more water.
        """
        rows, cols = len(map_data), len(map_data[0])
        total_tiles = rows * cols

        # Scale the number of steps for water generation with the map size
        base_min_steps = max(10, total_tiles // 50)  # At least 10 steps for smaller maps
        base_max_steps = max(20, total_tiles // 20)  # Larger maps have more water
        min_steps = int(base_min_steps * 1.5)  # Increase steps by 30%
        max_steps = int(base_max_steps * 1.5)  # Increase steps by 30%

        steps = random.randint(min_steps, max_steps)  # Total number of steps for water generation

        # Start the water generation at a random position
        start_x, start_y = random.randint(0, cols - 1), random.randint(0, rows - 1)
        x, y = start_x, start_y

        for _ in range(steps):
            map_data[y][x] = "water"
            # Randomly choose a direction for water to spread
            direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Up, right, down, left
            x = max(0, min(cols - 1, x + direction[0]))
            y = max(0, min(rows - 1, y + direction[1]))

    def add_tree_clusters(self, map_data):
        """
        Add tree clusters to a forest biome, scaled dynamically with map size, with 30% more density.
        """
        rows, cols = len(map_data), len(map_data[0])
        total_tiles = rows * cols

        # Scale the number of clusters and their sizes with the map size
        base_num_clusters = random.randint(total_tiles // 50, total_tiles // 25)  # 1-2% of tiles as cluster centers
        num_clusters = int(base_num_clusters * 1.7)  # Increase clusters by 30%

        min_cluster_size = max(5, total_tiles // 200)  # At least 3 tiles per cluster
        max_cluster_size = max(15, total_tiles // 50)  # At least 10 tiles for larger clusters

        for _ in range(num_clusters):
            cluster_x = random.randint(0, cols - 1)
            cluster_y = random.randint(0, rows - 1)
            cluster_size = random.randint(min_cluster_size, max_cluster_size)

            for _ in range(cluster_size):
                x = max(0, min(cols - 1, cluster_x + random.randint(-2, 2)))
                y = max(0, min(rows - 1, cluster_y + random.randint(-2, 2)))
                if map_data[y][x] != "water":  # Avoid placing trees in water
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