# Author: Gordon Ng
from .Location import Location
from models.rover import Rover
from .MapHandler import MapHandler

class PathFinder:

    def goTo(self, fromLoc: Location, toLoc: Location, rover: Rover, mapHandler: MapHandler) -> list[Location]:
        raise NotImplementedError("Subclasses must implement the goTo method.")

    def visitAll(self, fromLoc: Location, toVisit: list[Location], rover: Rover, mapHandler: MapHandler, progress_callback=None, ordered: bool = True) -> list[Location]:
        path = [fromLoc]
        if not toVisit:
            return path

        currentLoc = fromLoc
        total_locations_to_visit = len(toVisit)
        locations_visited_count = 0

        if progress_callback:
            progress_callback(locations_visited_count, total_locations_to_visit)

        if ordered:
            for targetLoc in toVisit:
                subPath = self.goTo(currentLoc, targetLoc, rover, mapHandler)
                if subPath:
                    # Path includes start node, extend excluding it
                    path.extend(subPath[1:])
                    currentLoc = subPath[-1]
                    locations_visited_count += 1
                    if progress_callback:
                        progress_callback(locations_visited_count, total_locations_to_visit)
                else:
                    print("Could not find path")
                    break 
        else:
            leftToVisitCoords = set((loc.x, loc.y) for loc in toVisit)

            while leftToVisitCoords:
                closestTargetCoord = None
                shortestSubPath = None
                minPathLen = float('inf')

                for targetCoord in leftToVisitCoords:
                    targetLoc = self.coordToLocation(targetCoord, mapHandler)
                    tempPath = self.goTo(currentLoc, targetLoc, rover, mapHandler)

                    if tempPath:
                        # Path length excludes the start node (currentLoc)
                        # Ensure tempPath is not empty before calculating length
                        currentPathLen = len(tempPath) - 1 if len(tempPath) > 0 else 0
                        if currentPathLen < minPathLen:
                            minPathLen = currentPathLen
                            closestTargetCoord = targetCoord
                            shortestSubPath = tempPath # Keep the best path found so far

                if closestTargetCoord and shortestSubPath:
                    # Append the path (excluding its start, which is currentLoc)
                    path.extend(shortestSubPath[1:])
                    currentLoc = shortestSubPath[-1] # Update current location
                    leftToVisitCoords.remove(closestTargetCoord)
                    locations_visited_count += 1
                    # Call the progress callback after visiting a location
                    if progress_callback:
                        progress_callback(locations_visited_count, total_locations_to_visit)
                else:
                    print("Could not find path to any remaining locations.")
                    break # Exit the loop if no path can be found

        return path

    def coordToLocation(self, coord: tuple[int, int], mapHandler: MapHandler) -> Location:
        x, y = coord
        return mapHandler.getLocationAt(x, y)