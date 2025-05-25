# Author: Gordon Ng
# Class deprecated

# import unittest

# from src.ai_algos.MapHandler import MapHandler
# from src.ai_algos.DFS import DFS
# from src.ai_algos.Rover import Rover
# from src.ai_algos.heuristics import manhattan_distance

# """
# To run from the root (from the ~/COMP361-Project directory) : python3 -m unittest tests.ai.dfsTests
# """

# class DFSAlgorithmTests(unittest.TestCase):
#     def setUp(self):
#         self.roverHigh = Rover(30)
#         self.roverLow  = Rover(0)

#     def testGoToHorizontal(self):
#         m = MapHandler(_build_grid(1, 2))
#         dfs = DFS()
#         path = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 1), self.roverLow, m)
#         self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1)])

#     def testGoToVertical(self):
#         m = MapHandler(_build_grid(1, 4))
#         dfs = DFS()
#         path = dfs.goTo(m.getLocationAt(0, 1), m.getLocationAt(0, 3), self.roverLow, m)
#         self.assertEqual([(p.x, p.y) for p in path], [(0, 1), (0, 2), (0, 3)])

#     def testDiagonalMovement(self):
#         m = MapHandler(_build_grid(2, 2))
#         dfs = DFS()
#         path = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(1, 1), self.roverLow, m)
#         self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (1, 1)])

#     def testVisitAllSingleTarget(self):
#         m  = MapHandler(_build_grid(1, 2))
#         dfs  = DFS()
#         start = m.getLocationAt(0, 0)
#         target = m.getLocationAt(0, 1)
#         path = dfs.visitAll(start, [target], self.roverLow, m)
#         self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1)])

#     def testVisitAllMultipleTargets(self):
#         m = MapHandler(_build_grid(1, 4))
#         dfs = DFS()
#         start = m.getLocationAt(0, 0)
#         targets = [m.getLocationAt(0, y) for y in (1, 2, 3)]
#         path = dfs.visitAll(start, targets, self.roverLow, m)
#         self.assertEqual([(p.x, p.y) for p in path], [(0, 0), (0, 1), (0, 2), (0, 3)])

#     def testShortestPath(self):
#         """Flat 3x3 grid without diagonals - Manhattan-shortest path length is 5."""
#         m = MapHandler(_build_grid(3, 3, diagonals=False))
#         dfs = DFS()
#         path  = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(2, 2), self.roverLow, m)
#         self.assertEqual(len(path), 5)
#         self.assertEqual((path[0].x, path[0].y), (0, 0))
#         self.assertEqual((path[-1].x, path[-1].y), (2, 2))

#     def testComplexGraphPathfinding(self):
#         """A wall blocks the direct route; algorithm must detour around."""
#         mapData = _build_grid(2, 3, diagonals=False)
#         # Block cell (0,1) completely
#         mapData[0][1][3] = (0,) * 8
#         # Remove E access from (0,0) and W from (0,2)
#         w = list(mapData[0][0][3]); w[2] = 0; mapData[0][0][3] = tuple(w)
#         w = list(mapData[0][2][3]); w[6] = 0; mapData[0][2][3] = tuple(w)

#         m  = MapHandler(mapData)
#         dfs = DFS()
#         path = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.roverLow, m)
#         self.assertTrue(all((loc.x, loc.y) != (0, 1) for loc in path))
#         self.assertEqual((path[-1].x, path[-1].y), (0, 2))

#     def testNoPath(self):
#         """Start and goal separated by an impenetrable wall."""
#         grid = _build_grid(1, 2, diagonals=False)
#         # Sever the only horizontal link
#         w = list(grid[0][0][3]); w[2] = 0; grid[0][0][3] = tuple(w)
#         w = list(grid[0][1][3]); w[6] = 0; grid[0][1][3] = tuple(w)

#         m = MapHandler(grid)
#         dfs = DFS()
#         path = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 1), self.roverLow, m)
#         self.assertEqual(path, [])

#     def testAltitudeChangePrioritization(self):
#         """Algorithm should avoid steep uphill when a slightly longer flat route exists."""
#         alt = [[0, 10, 0],
#                [0,  0, 0]]
#         m = MapHandler(_build_grid(2, 3, alt=alt))
#         dfs = DFS()
#         path  = dfs.goTo(m.getLocationAt(0, 0), m.getLocationAt(0, 2), self.roverLow, m)
#         # Middle cell (0,1) has altitude 10 - ensure it is not in the path
#         print(path)
#         self.assertTrue(all(m.getLocationAt(loc.x, loc.y).altitude < 5 for loc in path))

# if __name__ == "__main__":
#     unittest.main()