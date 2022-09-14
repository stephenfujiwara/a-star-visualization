from queue import PriorityQueue
import pygame

# set display
WIDTH = 500
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Visualization")

# colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0 , 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 244, 208)

class Tile:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.total_rows = total_rows

        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        # node gets colored red if already encountered, check if red
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == BLUE

    def is_end(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE
    
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = BLUE

    def make_end(self):
        self.color =BLUE

    def make_path(self):
        self.color = BLUE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # if not on border and tile below is not barrier
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # if not on border and tile above is not barrier
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # if not on border and tile to right is not barrier
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # if not on border and tile to left is not barrier
        if self.row > 0 and not grid[self.row][self.col].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
        #print(self.neighbors)


def make_grid(rows, width):
    grid = []
    tile_width = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            tile = Tile(i, j, tile_width, rows)
            grid[i].append(tile)

    return grid
    

def draw_grid(win, rows, width):
    tile_width = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, start_pos=(0, i * tile_width), end_pos=(width, i * tile_width))
        for j in range(rows):
            pygame.draw.line(win, GREY, start_pos=(j * tile_width, 0), end_pos=(j * tile_width, width))
            
            
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for tile in row:
            tile.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()


def heuristic(p1, p2):
    # manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2 - x1) + abs(y2 - y1)


def construct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def astar(draw, grid, start, end):
    ix = 0
    # queue that is ordered where item with smallest value is at the front.
    open_set = PriorityQueue()
    open_set.put((0, ix, start))
    came_from = {}
    # set g scores for each tile to Inf
    g_score = {tile: float("inf") for row in grid for tile in row}
    g_score[start] = 0
    f_score = {tile: float("inf") for row in grid for tile in row}
    # set f score of start node to heuristic
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    # use hash to check if node is in queue
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            construct_path(came_from, end, draw)
            end.make_end()
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    ix += 1
                    open_set.put((f_score[neighbor], ix, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        
        draw()

        if current != start:
            current.make_closed()

    return False


def get_clicked_position(pos, rows, width):
    tile_width = width // rows
    y, x = pos

    col = x // tile_width
    row = y // tile_width

    return row, col


def main(win, width):
    ROWS = 30
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # if left mouse button pressed
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                tile = grid[row][col]
                # if we don't have a start tile
                if not start and tile != end:
                    start = tile
                    start.make_start()
                # if we don't have an end tile
                elif not end and tile != start:
                    end = tile
                    end.make_end()
                # if we have both a start and end tile
                elif tile != start and tile != end:
                    tile.make_barrier()

            # if right mouse button pressed
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                tile = grid[row][col]
                tile.reset()
                if tile == start:
                    start = None
                if tile == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                # if hit spacebar
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for tile in row:
                            tile.update_neighbors(grid)
                    astar(lambda: draw(win, grid, ROWS, width), grid, start, end)
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

if __name__ == '__main__':
   main(WIN, WIDTH)
