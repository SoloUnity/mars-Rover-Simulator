#Author Mathilde Peruzzo

from math import sqrt, asin, cos, radians

def euclidean_distance(loc1, loc2) :
    """
    Computes the euclidean distance based on the coordinates of the locations in the map (their indices in the matrix)
    This method considers that the map has a point every 10 meters
    """
    return 200 * sqrt(((loc1.x - loc2.x)**2 + (loc1.y - loc2.y)**2))

def manhattan_distance(loc1, loc2) :
    """
    Computes a modified version of the Manhattan distance based on the coordinates of the 
        locations in the map (their indices in the matrix)
    This version accounts for the fact that rovers can move diagonally in the map
    """
    diagonal = min(abs(loc1.x - loc2.x), abs(loc1.y - loc2.y))
    horizontal= abs(loc1.x - loc2.x) - diagonal
    vertical = abs(loc1.y - loc2.y) - diagonal
    return diagonal + horizontal + vertical

def geographical_distance(loc1, loc2) :
    """
    Computes the distance according to spherical geometry using the Haversine formula
    """
    r = 3389000 # meters
    dphi = loc2.lat - loc1.lat
    dlambda = loc2.lon - loc1.lon
    hav = (1-cos(radians(dphi)))/2 + cos(radians(loc1.lat)) * cos(radians(loc2.lat)) * (1-cos(radians(dlambda)))/2
    return 2 * r * asin(sqrt(hav))

def distance_for_path(path, distance) :
    """
    Computes the distance travelled so far using the provided distance
    Estimates the distance to go by computing the distance between loc and toLoc
    """
    d = 0
    for i in range(len(path) - 1) :
        d += distance(path[i], path[i+1])
    return d

def is_distance_function(function) -> bool :
    """
    Tests if the provided function is one of the defined distance functions
    """
    return function == euclidean_distance \
            or function == manhattan_distance \
            or function == geographical_distance