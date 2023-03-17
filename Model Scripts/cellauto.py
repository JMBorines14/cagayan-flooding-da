import copy
from tkinter import *
from tkinter import ttk
import time

class CACell:
    """A CACell instance definition"""
    def __init__(self, x: float, y: float, ground_height: float, water_depth: float):
        """Initializes a CACell object"""
        self._x: float = round(x, 4)
        self._y: float = round(y, 4)
        self._ground_height: float = round(ground_height, 3)
        self._water_depth: float = round(water_depth, 3)
    
    def print(self):
        """Prints the statistics of a CACell object"""
        print("[{}, {}]".format(self._ground_height, self._water_depth), end = " ")

    def update_waterdepth(self, add_value: float):
        """Updates the water depth of a CACell object"""
        self._water_depth = round(self._water_depth + add_value, 4)
    
    def get_cell_height(self):
        """Gets the height (ground height + water depth) of a CACell object"""
        return self._ground_height + self._water_depth
    
    def get_depth(self):
        """Gets the water depth of a CACell object"""
        return self._water_depth

def is_equal(cell, neighbors):
    for i in neighbors:
        if cell.get_cell_height() != neighbors[i].get_cell_height():
            return False
    
    return True

def check_surroundings(cell, neighbors):
    equ = [1 if neighbors[i].get_cell_height() == cell.get_cell_height() else 0 for i in neighbors]
    lthan = [1 if neighbors[i].get_cell_height() > cell.get_cell_height() else 0 for i in neighbors]

    to_return = [equ[i] ^ lthan[i] for i in range(len(neighbors))]
    return sum(to_return) == len(neighbors) and sum(lthan) != len(neighbors)

def update_grid(grid, flood_map):
    new_grid = copy.deepcopy(grid)
    new_floodmap = copy.deepcopy(flood_map)

    def update_floodmap(new_floodmap, flood_neighbors):
        if "north" in flood_neighbors:
            new_floodmap[i-1][j] = flood_neighbors["north"]
        if "south" in flood_neighbors:
            new_floodmap[i+1][j] = flood_neighbors["south"]
        if "east" in flood_neighbors:
            new_floodmap[i][j+1] = flood_neighbors["east"]
        if "west" in flood_neighbors:
            new_floodmap[i][j-1] = flood_neighbors["west"]

    for i in range(len(grid)):
        for j in range(len(grid)):
            central = grid[i][j]
            neighbor_directory = dict()
            flood_neighbors = dict()

            if (i - 1) >= 0:
                neighbor_directory["north"] = grid[i-1][j]
                flood_neighbors["north"] = flood_map[i-1][j]
            if (i + 1) < len(grid):
                neighbor_directory["south"] = grid[i+1][j]
                flood_neighbors["south"] = flood_map[i+1][j]
            if (j + 1) < len(grid[i]):
                neighbor_directory["east"] = grid[i][j+1]
                flood_neighbors["east"] = flood_map[i][j+1]
            if (j - 1) >= 0:
                neighbor_directory["west"] = grid[i][j-1]
                flood_neighbors["west"] = flood_map[i][j-1]
            
            if flood_map[i][j] == 0:
                continue
            elif central.get_cell_height() < min([neighbor_directory[i].get_cell_height() for i in neighbor_directory]):
                min_height = min([neighbor_directory[i].get_cell_height() for i in neighbor_directory])
                new_water_depth = min(min_height - central.get_cell_height(), flood_map[i][j])
                
                new_grid[i][j].update_waterdepth(new_water_depth)
                new_floodmap[i][j] = round(max(flood_map[i][j] - new_water_depth, 0),4)
            elif is_equal(central, neighbor_directory):
                equal_amount = round(flood_map[i][j] / (1 + len(neighbor_directory)), 4)
                new_floodmap[i][j] = equal_amount

                for k in flood_neighbors:
                    flood_neighbors[k] += equal_amount
                
                update_floodmap(new_floodmap, flood_neighbors)
            elif check_surroundings(central, neighbor_directory):
                equ = [[i, 1] if neighbor_directory[i].get_cell_height() == central.get_cell_height() else [i, 0] for i in neighbor_directory]

                remaining_ev = max(flood_map[i][j] - 1, 0)
                new_grid[i][j].update_waterdepth(0.3)
                new_floodmap[i][j] = round(remaining_ev, 4)

                divis = round((remaining_ev/sum([k[1] for k in equ])), 4)

                for k in equ:
                    flood_neighbors[k[0]] += round(k[1] * divis, 4)
                
                update_floodmap(new_floodmap, flood_neighbors)
            else:
                a, b = 1, 1
                hf = a * (flood_map[i][j] ** b)
                d = [[i, max(0, central.get_cell_height() + hf - neighbor_directory[i].get_cell_height())] for i in neighbor_directory]
                sum_w = sum([j[1] for j in d])
                weights = {k[0]: (k[1]/sum_w) for k in d}

                new_floodmap[i][j] = 0

                for item in d:
                    flood_neighbors[item[0]] += round(flood_map[i][j] * weights[item[0]], 4)
                
                update_floodmap(new_floodmap, flood_neighbors)
    
    return new_grid, new_floodmap

def show_map(canvas, grid, flood_map):
    canvas.delete("all")
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            normalized_color = 255 if grid[i][j].get_depth() > 1.6000 else round(grid[i][j].get_depth() * 159.375)
            r = normalized_color * 2 if normalized_color < 128 else 255
            g = 255 if normalized_color < 128 else 255 - (normalized_color - 128) * 2
            canvas.create_rectangle(j * 50, i * 50, (j + 1) * 50, (i + 1) * 50, fill = rgb(r,g,0), outline = rgb(r,g,0))
            canvas.create_text(j * 50 + 25, i * 50 + 25, text = grid[i][j].get_depth())
        print(flood_map[i])
    canvas.update()
    print("======")
    time.sleep(1)

def simulation(canvas, steps, grid, flood_map):
    show_map(canvas, grid, flood_map)
    
    for _ in range(steps):
        #call function to update the flood map before calling to update the grid
        grid, flood_map = update_grid(grid, flood_map)
        show_map(canvas, grid, flood_map)

def rgb(r, g, b):
    return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0") for c in (r, g ,b)])

win = Tk()
win.geometry("520x520")
win.title("Flood Modelling")

gradient = Canvas(win, width = 500, height = 500)
gradient.pack()

dummy_start_x = 100.00
dummy_start_y = 150.00

heights = [[9.8, 9.2, 8.3, 4.5, 3.2, 3.3, 4.0, 4.5, 4.3, 4.0],
           [9.5, 9.4, 8.2, 9.0, 9.9, 9.5, 5.6, 5.6, 3.2, 4.9],
           [9.3, 8.3, 8.0, 3.4, 9.8, 9.7, 6.7, 5.9, 3.8, 4.9],
           [7.8, 8.5, 7.6, 9.3, 9.6, 6.5, 6.4, 6.2, 5.6, 6.0],
           [8.1, 8.6, 9.3, 9.3, 9.5, 6.3, 6.0, 8.0, 6.0, 7.8],
           [6.5, 9.0, 9.5, 4.5, 9.3, 5.6, 8.4, 8.3, 8.3, 8.1],
           [9.2, 5.6, 7.8, 9.6, 8.6, 5.5, 9.4, 9.0, 9.6, 7.8],
           [9.3, 9.0, 5.6, 8.3, 8.4, 9.4, 9.4, 9.4, 9.2, 7.8],
           [6.7, 7.5, 6.7, 6.7, 8.1, 9.4, 9.4, 9.0, 9.4, 7.8],
           [6.8, 8.9, 6.0, 6.7, 7.5, 9.3, 9.5, 9.4, 9.3, 8.0]]

ob_oriented_cells = [[0 for _ in range(10)] for _ in range(10)]

for i in range(10):
    for j in range(10):
        ob_oriented_cells[i][j] = CACell(dummy_start_x, dummy_start_y, heights[i][j], 0)
        dummy_start_y += 1.20
    dummy_start_x += 1.50

flood_map = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0.78, 0, 0],
             [0, 0, 0, 4.7, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0.4, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1.2, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

simulation(gradient, 4, ob_oriented_cells, flood_map)

win.mainloop()