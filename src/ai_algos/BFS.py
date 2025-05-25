# #Author : Mathilde Peruzzo
# Class deprecated

# from collections import deque

# from .Pathfinder import PathFinder
# from .Location import Location
# from .Node import Node

# class BFS(PathFinder):

#     def goTo(self, fromLoc, toLoc, rover, mapHandler):
#         q = deque()
#         visited_coords = set()

#         startCoord = (fromLoc.x, fromLoc.y)
#         goalCoord = (toLoc.x, toLoc.y)

#         startNode = Node(startCoord, None)
#         q.append(startNode)
#         visited_coords.add(startCoord)

#         while q:
#             currentNode = q.popleft()
#             currentCoord = currentNode.coord

#             if currentCoord == goalCoord:
#                 return [fromLoc] + self.getPath(currentNode, mapHandler)

#             currentLocation = self.coordToLocation(currentCoord, mapHandler)

#             for nx, ny, angle in mapHandler.getNeighbors(currentCoord[0], currentCoord[1]):
#                 if angle > rover.max_incline or angle == -1:
#                     continue

#                 neighborCoord = (nx, ny)
#                 if neighborCoord not in visited_coords:
#                     visited_coords.add(neighborCoord)
#                     neighborNode = Node(neighborCoord, currentNode)
#                     q.append(neighborNode)

#         return []