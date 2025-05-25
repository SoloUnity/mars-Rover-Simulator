#Author : Mathilde Peruzzo

from math import sqrt, tan, fsum, radians
from .MapHandler import MapHandler
from .distances import *

################# helpers ###################

def altitude_difference(loc1, loc2) :
    return loc2.altitude - loc1.altitude

def get_mid_point(loc1, loc2) :
    return (loc1.x + (loc2.x - loc1.x)//2, loc1.y + (loc2.y - loc1.y)//2)

################# heuristics ################

def euclidean_distance_h(prevLoc, loc, toLoc, rover, mapHandler) :
    return euclidean_distance(loc, toLoc)

def manhattan_distance_h(prevLoc, loc, toLoc, rover, mapHandler) :
    return manhattan_distance(loc, toLoc)

def geographical_distance_h(prevLoc, loc, toLoc, rover, mapHandler) :
    return geographical_distance(loc, toLoc)

def has_sunlight_obstacle_h(prevLoc, loc, toLoc, rover, mapHandler) :
    """
    Returns 0 if the location is exposed to the sun at midday, 1 otherwise
    Neglects the axial tilt of the planet and approximates the ground as a flat surface
    Only considers potential obstacles two kilometers away
    """
    if abs(loc.lat) < 10 : return 0
    sign = 1 if loc.lat > 0 else -1
    # checks the the north-south direction towards the equator
    for i in range(1, 10) :
        y = loc.y + sign * i
        if not mapHandler.isValidLocation(loc.x, y) :
            return 0

        loc1 = mapHandler.getLocationAt(loc.x, y)
        if sign != (1 if loc1.lat > 0 else -1) :
            return 0 # no obstacle if cross the equator

        alt_diff = altitude_difference(loc, loc1)
        if alt_diff > 0 : 
            return 1
    return 0

def energy_for_slope_h(prevLoc, loc, toLoc, rover, mapHandler) :
    """
    Computes the energy needed by the provided rover 
    to go from loc1 to loc2 depending on the slope between the two locations
    """
    distance = euclidean_distance(loc, toLoc)
    if distance == 0 : return 0

    slope = altitude_difference(loc, toLoc) / distance
    if slope < 0 : return 0
    elif (0 <= slope and slope < rover.tanMidSlope) :
        return rover.lowSlopeEnergy * manhattan_distance(loc, toLoc)
    elif (rover.tanMidSlope <= slope and slope < rover.tanHighSlope) :
        return rover.midSlopeEnergy * manhattan_distance(loc, toLoc)
    else :
        return rover.highSlopeEnergy * manhattan_distance(loc, toLoc)

def stable_altitude_h(prevLoc, loc, toLoc, rover, mapHandler) :
    """
    Computes the sum of thealtitude differences between prevLoc and loc and between loc and toLoc
    When used as a heuristic it encourages the path to keep a stable altitude
    """
    return abs(altitude_difference(prevLoc, loc)) + abs(altitude_difference(loc, toLoc))

def low_altitude_h(prevLoc, loc, toLoc, rover, mapHandler) :
    """
    Returns the altitude
    When used as a heuristic it encourages the path to stay at low altitudes
    """
    return loc.altitude

def hazardous_regions_h(prevLoc, loc, toLoc, rover, mapHandler) :
    """
    Returns 1 if loc is hazardous, 0 otherwise
    Encourages the path to avoid hazardous regions
    """
    return mapHandler.isHazardous(loc.x, loc.y)
