import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen size
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('2048')

# Colors
BACKGROUND_COLOR = (187, 173, 160)
GRID_COLOR = (205, 193, 180)
EMPTY_TILE_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}
TEXT_COLOR = (119, 110, 101)
FONT = pygame.font.Font(None, 50)

# Initialize game variables
grid = [[0] * 4 for _ in range(4)]
score = 0

# Helper functions
def add_new_tile():
    empty_tiles = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
    if empty_tiles:
        r, c = random.choice(empty_tiles)
        grid[r][c] = 2 if random.random() < 0.9 else 4

def draw_grid():
    screen.fill(BACKGROUND_COLOR)
    for r in range(4):
        for c in range(4):
            tile_value = grid[r][c]
            tile_color = TILE_COLORS.get(tile_value, EMPTY_TILE_COLOR)
            pygame.draw.rect(screen, tile_color, pygame.Rect(c * 100, r * 100, 100, 100))
            if tile_value != 0:
                text = FONT.render(str(tile_value), True, TEXT_COLOR)
                text_rect = text.get_rect(center=(c * 100 + 50, r * 100 + 50))
                screen.blit(text, text_rect)

def merge_left():
    global score
    for r in range(4):
        row = [tile for tile in grid[r] if tile != 0]
        merged_row = []
        skip = False
        for i in range(len(row)):
            if skip:
                skip = False
                continue
            if i + 1 < len(row) and row[i] == row[i + 1]:
                merged_row.append(row[i] * 2)
                score += row[i] * 2
                skip = True
            else:
                merged_row.append(row[i])
        merged_row.extend([0] * (4 - len(merged_row)))
        grid[r] = merged_row

def rotate_grid():
    global grid
    grid = [list(row) for row in zip(*grid[::-1])]

def move_left():
    old_grid = [row[:] for row in grid]
    merge_left()
    return old_grid != grid

def move_right():
    rotate_grid()
    rotate_grid()
    moved = move_left()
    rotate_grid()
    rotate_grid()
    return moved

def move_up():
    rotate_grid()
    moved = move_left()
    rotate_grid()
    rotate_grid()
    rotate_grid()
    return moved

def move_down():
    rotate_grid()
    rotate_grid()
    rotate_grid()
    moved = move_left()
    rotate_grid()
    return moved

def game_over():
    if any(0 in row for row in grid):
        return False
    for r in range(4):
        for c in range(4):
            if c + 1 < 4 and grid[r][c] == grid[r][c + 1]:
                return False
            if r + 1 < 4 and grid[r][c] == grid[r + 1][c]:
                return False
    return True

# Initialize the game
add_new_tile()
add_new_tile()

class SmartAI:
    def __init__(self, game_grid):
        self.grid = game_grid

    def next_move(self):
        original_quality = self.grid_quality(self.grid)
        results = self.plan_ahead(self.grid, 3, original_quality)
        best_result = self.choose_best_move(results, original_quality)
        return best_result['direction']

    def plan_ahead(self, grid, num_moves, original_quality):
        results = [None] * 4
        for d in range(4):
            test_grid = [row[:] for row in grid]
            moved = self.move_tiles(test_grid, d)
            if not moved:
                results[d] = None
                continue
            result = {
                'quality': -1,
                'probability': 1,
                'qualityLoss': 0,
                'direction': d
            }
            available_cells = self.available_cells(test_grid)
            for cell in available_cells:
                test_grid2 = [row[:] for row in test_grid]
                self.add_tile(test_grid2, cell, 2)
                if num_moves > 1:
                    sub_results = self.plan_ahead(test_grid2, num_moves - 1, original_quality)
                    tile_result = self.choose_best_move(sub_results, original_quality)
                else:
                    tile_quality = self.grid_quality(test_grid2)
                    tile_result = {
                        'quality': tile_quality,
                        'probability': 1,
                        'qualityLoss': max(original_quality - tile_quality, 0)
                    }
                if result['quality'] == -1 or tile_result['quality'] < result['quality']:
                    result['quality'] = tile_result['quality']
                    result['probability'] = tile_result['probability'] / len(available_cells)
                elif tile_result['quality'] == result['quality']:
                    result['probability'] += tile_result['probability'] / len(available_cells)
                result['qualityLoss'] += tile_result['qualityLoss'] / len(available_cells)
            results[d] = result
        return results

    def choose_best_move(self, results, original_quality):
        best_result = None
        for result in results:
            if not result:
                continue
            if not best_result or \
               result['qualityLoss'] < best_result['qualityLoss'] or \
               (result['qualityLoss'] == best_result['qualityLoss'] and result['quality'] > best_result['quality']) or \
               (result['qualityLoss'] == best_result['qualityLoss'] and result['quality'] == best_result['quality'] and result['probability'] < best_result['probability']):
                best_result = result
        if not best_result:
            best_result = {
                'quality': -1,
                'probability': 1,
                'qualityLoss': original_quality,
                'direction': 0
            }
        return best_result

    def grid_quality(self, grid):
        mono_score = 0
        traversals = self.build_traversals()
        prev_value = -1
        inc_score = 0
        dec_score = 0
        for x in traversals['x']:
            prev_value = -1
            inc_score = 0
            dec_score = 0
            for y in traversals['y']:
                tile_value = grid[y][x] if grid[y][x] else 0
                inc_score += tile_value
                if tile_value <= prev_value or prev_value == -1:
                    dec_score += tile_value
                    if tile_value < prev_value:
                        inc_score -= prev_value
                prev_value = tile_value
            mono_score += max(inc_score, dec_score)
        for y in traversals['y']:
            prev_value = -1
            inc_score = 0
            dec_score = 0
            for x in traversals['x']:
                tile_value = grid[y][x] if grid[y][x] else 0
                inc_score += tile_value
                if tile_value <= prev_value or prev_value == -1:
                    dec_score += tile_value
                    if tile_value < prev_value:
                        inc_score -= prev_value
                prev_value = tile_value
            mono_score += max(inc_score, dec_score)
        empty_score = len(self.available_cells(grid)) * 8
        score = mono_score + empty_score
        return score

    def build_traversals(self):
        return {
            'x': range(4),
            'y': range(4)
        }

    def available_cells(self, grid):
        return [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]

    def add_tile(self, grid, cell, value):
        grid[cell[0]][cell[1]] = value

    def move_tiles(self, grid, direction):
        rotated = 0
        if direction == 1:
            rotated = 2
        elif direction == 2:
            rotated = 3
        elif direction == 3:
            rotated = 1
        for _ in range(rotated):
            grid = [list(row) for row in zip(*grid[::-1])]
        moved = self.merge_left(grid)
        for _ in range(4 - rotated):
            grid = [list(row) for row in zip(*grid[::-1])]
        return moved

    def merge_left(self, grid):
        moved = False
        for r in range(4):
            row = [tile for tile in grid[r] if tile != 0]
            merged_row = []
            skip = False
            for i in range(len(row)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(row) and row[i] == row[i + 1]:
                    merged_row.append(row[i] * 2)
                    skip = True
                else:
                    merged_row.append(row[i])
            merged_row.extend([0] * (4 - len(merged_row)))
            if grid[r] != merged_row:
                moved = True
            grid[r] = merged_row
        return moved

# Main game loop
ai = SmartAI(grid)
running = True
while running:
    draw_grid()
    pygame.display.flip()
    if game_over():
        print("Game Over! Final Score:", score)
        running = False
    else:
        direction = ai.next_move()
        moved = False
        if direction == 0:
            moved = move_left()
        elif direction == 1:
            moved = move_right()
        elif direction == 2:
            moved = move_down()
        elif direction == 3:
            moved = move_up()
        if moved:
            add_new_tile()

pygame.quit()
sys.exit()
