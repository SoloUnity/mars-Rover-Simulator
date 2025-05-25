# Author: Matthew Spagnuolo
from src.util.dem_to_matrix import dem_to_matrix
from tqdm import tqdm
import math

MARS_DEM_RESOLUTION = 200  # meters between elevation points (calculated for the .tif file used using its source's information)

def matrix_to_topo_map(dem_matrix, progress_callback=None):
    """
    Converts a 2D matrix representing a DEM into a topographical map.

    This changes the given matrix by adding a new 8-tuple to each cell. Each tuple value contains either -1 or an angle tilt value (degrees) to 
    indicate if the top, top-right, right, bottom-right, bottom, bottom-left, left, or top-left cells (in this order, which is clockwise) can be accessed from the current cell,
    and if so, what tilt needs to be handled for traversal to said cell.

    Example:
    (-1, -1, 12, 43, 22, 22, 23, -1) means that, from the current cell, one can travel to any neighboring cell, except for any top neighbor (boundary on top). The other values 
    indicate the angle tilt between the current cell and the accessible neighboring cells.
    
    param: dem_matrix: 2D list representing the DEM with coordinates
    param: progress_callback: Optional function to call with (current_row, total_rows) for progress updates.
    return: 3D list representing the DEM with each cell being a list of indexes, coordinates, elevation, and an 8-tuple of angles
    """

    total_rows = len(dem_matrix)
    total_cols = len(dem_matrix[0])
    iterator = range(total_rows)
    if progress_callback is None:
        # Use tqdm if no callback is provided
        iterator = tqdm(iterator, desc="Generating Map", unit="row")

    for row in iterator:
        for col in range(total_cols):
            cell = dem_matrix[row][col]
            elevation = cell[2]
            neighbors = [-1] * 8 # initialize tuple with -1

            #define offsets for neighbors (row_offset, col_offset, index in tuple , diagonal flag)
            neighbor_offsets = [
                (-1,  0, 0, False),  #top
                (-1,  1, 1, True),   #top-right
                ( 0,  1, 2, False),  #right
                ( 1,  1, 3, True),   #bottom-right
                ( 1,  0, 4, False),  #bottom
                ( 1, -1, 5, True),   #bottom-left
                ( 0, -1, 6, False),  #left
                (-1, -1, 7, True)    #top-left
            ]


            for row_offset, col_offset, index, is_diagonal in neighbor_offsets:
                neighbor_row = row + row_offset
                neighbor_col = col + col_offset

                if 0 <= neighbor_row < total_rows and 0 <= neighbor_col < total_cols: #check if the neighbor is within bounds
                    neighbor_cell = dem_matrix[neighbor_row][neighbor_col]
                    neighbor_elevation = neighbor_cell[2]

                    #calculate tilt using elevation delta
                    elevation_delta = abs(neighbor_elevation - elevation)
                    distance = MARS_DEM_RESOLUTION * (math.sqrt(2) if is_diagonal else 1)
                    tilt_angle = math.degrees(math.atan(elevation_delta / distance))
                    neighbors[index] = int(tilt_angle)

            cell.append(tuple(neighbors))

        
        if progress_callback: # report progress if a callback is provided
            progress_callback(row + 1, total_rows)  # Report progress

    return dem_matrix

if __name__ == "__main__":
    tif_file = "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"
    dem_matrix, _ = dem_to_matrix(tif_file, start_point=(0, 0), max_rows=1000, max_cols=1000)
    print(matrix_to_topo_map(dem_matrix)[566][566])
