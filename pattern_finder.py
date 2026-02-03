import random
import numpy as np

ROWS, COLS = 3, 11
COLORS = ["A", "B", "C", "D", "E"]

# Step 1: balanced counts (31 total)
counts = [7, 7, 7, 6, 6]
color_pool = []
for color, count in zip(COLORS, counts):
    color_pool.extend([color] * count)

def count_adjacent_conflicts(grid):
    conflicts = 0
    for r in range(ROWS):
        for c in range(COLS):
            if r + 1 < ROWS and grid[r, c] == grid[r + 1, c]:
                conflicts += 1
            if c + 1 < COLS and grid[r, c] == grid[r, c + 1]:
                conflicts += 1
    return conflicts

best_grid = None
best_conflicts = float("inf")

# Step 2–5: try many random layouts
for _ in range(20_000):
    random.shuffle(color_pool)
    grid = np.array(color_pool).reshape(ROWS, COLS)
    conflicts = count_adjacent_conflicts(grid)

    if conflicts < best_conflicts:
        best_conflicts = conflicts
        best_grid = grid

    if conflicts == 0:
        break

print("Adjacent conflicts:", best_conflicts)
print(best_grid)