# Author: Gordon Ng
import unittest

from src.ai_algos.MapHandler import MapHandler
from src.ai_algos.AStar import AStar
from models.rover import Rover
from src.ai_algos.heuristics import *
from .testBuilder import build_grid

"""
To run from the root (from the ~/COMP361-Project directory) : python3 -m unittest tests.ai.aStarTests
"""

class TestAStarAlgorithm(unittest.TestCase):
    def setUp(self):
        self.rover_low  = Rover(max_incline=0)
        self.rover_high = Rover(max_incline=30)

    # move east across a 1x3 flat row
    def testGoToHorizontal(self):
        grid = build_grid(1, 3)
        m = MapHandler(grid)
        astar = AStar()

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2)])

    # move south across a 3x1 flat column
    def testGoToVertical(self):
        grid = build_grid(3, 1)
        m = MapHandler(grid)
        astar = AStar()

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(2, 0), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (1, 0), (2, 0)])

    # move diagonally
    def testDiagonalMovement(self):
        grid = build_grid(2, 2)
        m = MapHandler(grid)
        astar = AStar()

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(1, 1), self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (1, 1)])

    # visitAll with a single target should be same as goTo
    def testVisitAllSingleTarget(self):
        grid = build_grid(1, 2)
        m = MapHandler(grid)
        astar = AStar()

        start   = m.getLocationAt(0, 0)
        target  = m.getLocationAt(0, 1)
        path_va = astar.visitAll(start, [target], self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path_va], [(0, 0), (0, 1)])

    def testVisitAllMultipleTargets(self):
        grid = build_grid(1, 4)
        m = MapHandler(grid)
        astar = AStar()

        start   = m.getLocationAt(0, 0)
        targets = [m.getLocationAt(0, y) for y in (1, 2, 3)]
        path    = astar.visitAll(start, targets, self.rover_low, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2), (0, 3)])

    # 3x3 grid, diagonals not allowed
    def testShortestPath(self):
        grid = build_grid(3, 3, diagonals=False)
        m = MapHandler(grid)
        astar = AStar()

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(2, 2), self.rover_low, m)
        self.assertEqual(len(path), 5)
        self.assertEqual((path[-1].x, path[-1].y), (2, 2))

    # 3x3 grid with a wall
    def testComplexGraphPathfinding(self):
        grid = build_grid(2, 3, diagonals=False)
        # Block cell (0,1) completely
        grid[0][1][3] = (-1,) * 8
        # Remove E edge from (0,0) and W from (0,2)
        w = list(grid[0][0][3]); w[2] = -1; grid[0][0][3] = tuple(w)
        w = list(grid[0][2][3]); w[6] = -1; grid[0][2][3] = tuple(w)

        m = MapHandler(grid)
        astar = AStar()

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_low, m)
        self.assertTrue(all(not (loc.x == 0 and loc.y == 1) for loc in path))
        self.assertEqual((path[-1].x, path[-1].y), (0, 2))

    def testNoPath(self):
        """If all connections are blocked, A* must return an empty list."""
        grid = build_grid(1, 2, diagonals=False)
        # Sever the only edge between the two cells
        w = list(grid[0][0][3]); w[2] = -1; grid[0][0][3] = tuple(w)
        w = list(grid[0][1][3]); w[6] = -1; grid[0][1][3] = tuple(w)

        m = MapHandler(grid)
        astar = AStar()
        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 1), self.rover_low, m)
        self.assertEqual(path, [])

    def testAltitudeChangePrioritization(self):
        """A steep 45° middle segment should be avoided in favour of a flat detour."""
        grid = build_grid(2, 3)
        # Middle cell (0,1) only reachable via 45° from its neighbours
        w = list(grid[0][0][3]); w[2] = 45; grid[0][0][3] = tuple(w)  # start→middle
        w = list(grid[0][1][3]); w[6] = 45; grid[0][1][3] = tuple(w)  # middle→start

        m = MapHandler(grid)
        astar = AStar()
        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_low, m)
        self.assertTrue(all(not (loc.x == 0 and loc.y == 1) for loc in path))

    def testMultipleHeuristics(self):
        grid = build_grid(1, 3)
        m = MapHandler(grid)
        astar = AStar([(0.6, manhattan_distance_h), (0.4, euclidean_distance_h)])

        path = astar.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.rover_high, m)
        self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2)])


if __name__ == "__main__":
    unittest.main()