#Author Gordon Ng
#Author Noah Lepage
#Author Mathilde Peruzzo

import heapq
from .Pathfinder import PathFinder
from models.rover import Rover
from .heuristics import manhattan_distance_h

class AStar(PathFinder):
    def __init__(self, heuristic_funcs=None):
        """
        heuristic_funcs: list of (weight: float, func: callable(loc, goal)->float).
        If None, defaults to [(1.0, manhattan_distance)].
        """
        if heuristic_funcs is not None :
            self.heuristic_funcs = []

            for w, fn in heuristic_funcs:
                print(f"HEURISTIC: {fn.__name__} with weight {w}")
                if not callable(fn):
                    raise TypeError(f"Heuristic {fn!r} is not callable")
                self.heuristic_funcs.append((float(w), fn))
        else:
            # Unit test case
            self.heuristic_funcs = [(1.0, manhattan_distance_h)]
            
    def _heuristic(self, prevLoc, loc, goalLoc, rover, mapHandler):
        """Combine all heuristics at a given node."""
        h = 0.0
        for w, fn in self.heuristic_funcs:
            h += w * fn(prevLoc, loc, goalLoc, rover, mapHandler)
        return h

    def goTo(self, startLoc, goalLoc, rover: Rover, mapHandler):
        start = (startLoc.x, startLoc.y)
        goal  = (goalLoc.x,  goalLoc.y)

        gScore = {start: 0.0}
        fScore = {start: self._heuristic(startLoc, startLoc, goalLoc, rover, mapHandler)}

        open_heap = [(fScore[start], start)]
        came_from = {}
        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            if current == goal:
                return self._reconstruct_path(came_from, startLoc, mapHandler, current)

            closed.add(current)
            cx, cy = current
            current_g = gScore[current]
            currLoc   = mapHandler.getLocationAt(cx, cy)

            for nx, ny, angle in mapHandler.getNeighbors(cx, cy):
                if angle > rover.max_incline:
                    continue
                
                neighbor = (nx, ny)
                if neighbor in closed:
                    continue

                neighLoc = mapHandler.getLocationAt(nx, ny)
                # cost: base 1 + uphill penalty only
                delta    = neighLoc.altitude - currLoc.altitude
                moveCost = 1 + max(0, delta)

                tentative_g = current_g + moveCost
                if tentative_g < gScore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    gScore[neighbor]    = tentative_g

                    h = self._heuristic(currLoc, neighLoc, goalLoc, rover, mapHandler)
                    f = tentative_g + h
                    fScore[neighbor] = f
                    heapq.heappush(open_heap, (f, neighbor))

        return []

    def _reconstruct_path(self, came_from, startLoc, mapHandler, current_coord):
        """Builds the Location list once the goal is reached."""
        path = []
        while current_coord in came_from:
            path.append(self.coordToLocation(current_coord, mapHandler))
            current_coord = came_from[current_coord]
        path.reverse()
        return [startLoc] + path