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

# Main game loop
running = True
while running:
    draw_grid()
    pygame.display.flip()
    if game_over():
        print("Game Over! Final Score:", score)
        running = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            moved = False
            if event.key == pygame.K_LEFT:
                moved = move_left()
            elif event.key == pygame.K_RIGHT:
                moved = move_right()
            elif event.key == pygame.K_UP:
                moved = move_down()
            elif event.key == pygame.K_DOWN:
                moved = move_up()
            if moved:
                add_new_tile()

pygame.quit()
sys.exit()