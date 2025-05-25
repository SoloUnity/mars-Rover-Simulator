# Author: Gordon Ng
from .Location import Location

class MapHandler:
    def __init__(self, mapData):
        self.map = mapData
        self.width = len(mapData)
        self.height = len(mapData[0])

    def getAltitude(self, x, y):
        return self.map[x][y][2]
    
    def isValidLocation(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def getNeighbors(self, x, y):
        cell = self.map[x][y]
        _, _, _, walls = cell
        neighbors = []
        # Vertical horizontal diagonal
        for i, (dx, dy) in enumerate([(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]):
            newX, newY = x + dx, y + dy
            # walls[i] contains angle to reach i, -1 if unreachable
            if walls[i] != -1:
                neighbors.append((newX, newY, walls[i]))
        return neighbors
    
    def getMapSection(self, startX, startY, width, height):
        endX = min(startX + width, self.width)
        endY = min(startY + height, self.height)
        return [row[startY:endY] for row in self.map[startX:endX]]
    
    def getLocationAt(self, x: int, y: int):
        cell = self.map[x][y]
        _, (lat, lon), altitude, walls = cell
        return Location(x, y, lon, lat, altitude, walls)