import unittest

from src.ai_algos.MapHandler import MapHandler
from src.ai_algos.BFS import BFS
from models.rover import Rover
from .testBuilder import build_grid

"""
To run from the root (from the ~/COMP361-Project directory) : python3 -m unittest tests.ai.bfsTests
"""

class BFSAlgorithmTests(unittest.TestCase):

    def setUp(self) -> None:
        self.rover_low  = Rover(max_incline=0)   # cannot climb
        self.rover_high = Rover(max_incline=30)  # up to 30 °

    def testGoToHorizontal(self):
        grid = build_grid(1, 3)  # 1 × 3 row
        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2)])

    def testGoToVertical(self):
        grid = build_grid(3, 1)  # 3 × 1 column
        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(2, 0), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (1, 0), (2, 0)])

    def testDiagonalMovement(self):
        grid = build_grid(2, 2)  # diagonals enabled
        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(1, 1), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (1, 1)])

    def testVisitAllSingleTarget(self):
        grid = build_grid(1, 2)
        m = MapHandler(grid)
        bfs = BFS()
        start  = m.getLocationAt(0, 0)
        target = m.getLocationAt(0, 1)
        path   = bfs.visitAll(start, [target], self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1)])

    def testVisitAllMultipleTargets(self):
        grid = build_grid(1, 4)
        m = MapHandler(grid)
        bfs = BFS()
        start   = m.getLocationAt(0, 0)
        targets = [m.getLocationAt(0, y) for y in (1, 2, 3)]
        path    = bfs.visitAll(start, targets, self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2), (0, 3)])

    def testShortestPath(self):
        grid = build_grid(3, 3, diagonals=False)
        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(2, 2), self.rover_low, m)
        self.assertEqual(len(path), 5)
        self.assertEqual((path[-1].x, path[-1].y), (2, 2))

    def testComplexGraphPathfinding(self):
        grid = build_grid(2, 3, diagonals=False)
        # Block cell (0,1)
        grid[0][1][3] = (-1,) * 8
        # Remove E edge from (0,0) to avoid blocked cell
        w = list(grid[0][0][3]); w[2] = -1; grid[0][0][3] = tuple(w)

        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_low, m)
        self.assertTrue(path, "BFS failed to find detour")
        self.assertTrue(all((loc.x, loc.y) != (0, 1) for loc in path))
        self.assertEqual((path[-1].x, path[-1].y), (0, 2))

    def testNoPath(self):
        grid = build_grid(1, 2, diagonals=False)
        # Break the only connection
        w = list(grid[0][0][3]); w[2] = -1; grid[0][0][3] = tuple(w)
        w = list(grid[0][1][3]); w[6] = -1; grid[0][1][3] = tuple(w)

        m = MapHandler(grid)
        bfs = BFS()
        path = bfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 1), self.rover_low, m)
        self.assertEqual(path, [])


if __name__ == "__main__":
    unittest.main()
