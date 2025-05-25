# Author: Mathilde Peruzzo
# Author: Gordon Ng
import os
import time

from models.rover import Rover
from src.ai_algos.MapHandler import MapHandler
from src.ai_algos.BFS import BFS
from src.ai_algos.AStar import AStar
from src.util.dem_to_matrix import dem_to_matrix, get_window_for_path
from src.util.matrix_to_topo_map import matrix_to_topo_map
from src.util.matrix_to_maze_map import matrix_to_maze_map
from src.ai_algos.Location import Location
from src.ai_algos.heuristics import *
from src.ai_algos.distances import *

"""
To run (from project root): python3 -m tests.ai.aiWithMapTests
"""

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
tif_path = os.path.join(project_root, "Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif")

def build_map(tile_origin: tuple[int, int] = (5000, 4030), rows: int = 300, cols: int = 300) -> MapHandler:
    """Load a small section of the global Mars DEM and wrap it in *MapHandler*."""

    dem_matrix, _ = dem_to_matrix(tif_path, tile_origin, rows, cols)
    topo_map = matrix_to_maze_map(dem_matrix)
    return MapHandler(topo_map)

def printPath(path) :
    for loc in path :
        loc.printLoc()
        
def bfsOnMap() :
    mH = build_map()
    start = mH.getLocationAt(10, 10)
    goal = mH.getLocationAt(50, 80)

    bfs = BFS()

    rover1 = Rover(max_incline=30)
    t0 = time.time()
    path = bfs.goTo(start, goal, rover1, mapHandler=mH)
    print(f"BFS finished in {time.time() - t0:.3f}s - {len(path)} steps:")
    printPath(path)

def aStarOnMap() -> None:
    mH = build_map()
    start = mH.getLocationAt(10, 10)
    goal = mH.getLocationAt(50, 80)

    astar = AStar(euclidean_distance, [(1.0, euclidean_distance_h)])
    rover1 = Rover(max_incline=30)
    t0 = time.time()
    path = astar.goTo(start, goal, rover1, mapHandler=mH)
    print(f"A* finished in {time.time() - t0:.3f}s - {len(path)} steps:")
    printPath(path)

# def heuristicsOnMap() :
#     matrix, new_transform = dem_to_matrix(mapFilePath, (5000, 4030), 100, 100)
#     mH = MapHandler(matrix)
#     fromLoc = mH.getLocationAt(10, 10)
#     toLoc1 = mH.getLocationAt(10, 15)
#     toLoc2 = mH.getLocationAt(12, 9)
#     loc = mH.getLocationAt(10, 14)
#     rover = Rover(10, 1, 5, 10) # with 10 a different path
#     bfs = BFS()
#     path = bfs.goTo(fromLoc, toLoc1, rover, mH)
#     print(euclidean_distance_h(path, loc, toLoc2, rover, mH))

# def algosOnSameMap() :
#     matrix, new_transform = dem_to_matrix(mapFilePath, (5000, 4030), 2000, 2000)
#     mH = MapHandler(matrix)
#     print("Map loaded")

#     print("--------------------------------------------------------------------------")

#     fromLoc = mH.getLocationAt(10, 10)
#     toLoc1 = mH.getLocationAt(10, 1500)
#     toLoc2 = mH.getLocationAt(120, 9)
#     rover = Rover(8) # with 10 a different path
#     """

#     print("Running BFS")
#     bfs = BFS()
#     start_time = time.time()
#     bfs_path = bfs.visitAll(fromLoc, [toLoc1, toLoc2], rover, mH)
#     print("BFS time : ", time.time() - start_time)
#     printPath(bfs_path)

#     print("--------------------------------------------------------------------------")

#     print("Running DFS")
#     bfs = DFS()
#     start_time = time.time()
#     dfs_path = bfs.visitAll(fromLoc, [toLoc1, toLoc2], rover, mH)
#     print("DFS time : ", time.time() - start_time)
#     #printPath(dfs_path)

#     print("--------------------------------------------------------------------------")
#     """

#     print("Running aStar")
#     aStar = AStar([(1, euclidean_distance_h)])
#     start_time = time.time()
#     astar_path = aStar.visitAll(fromLoc, [toLoc1, toLoc2], rover, mH)
#     print("BFS time : ", time.time() - start_time)
#     printPath(astar_path)

if __name__ == "__main__":
    #algosOnSameMap()
    #heuristicsOnMap()
    aStarOnMap()
    bfsOnMap()