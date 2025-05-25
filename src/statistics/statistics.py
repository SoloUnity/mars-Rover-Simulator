#Author : Mathilde Peruzzo

from src.ai_algos.Location import Location
from src.ai_algos.distances import euclidean_distance
from src.ai_algos.heuristics import altitude_difference, has_sunlight_obstacle_h

def path_avg_altitude(path : list[Location]) :
    if path is None :
        return 0

    total_altitude = 0
    for loc in path :
        total_altitude += loc.altitude
    return total_altitude / len(path)

def path_length(path : list[Location], distance_f) :
    length = 0.0
    for i in range(len(path)-1) :
        length += distance_f(path[i], path[i+1])
    return length

def path_energy(path : list[Location], rover) :
    total_energy = 0.0
    for i in range(len(path)-1) :
        slope = altitude_difference(path[i], path[i+1]) / euclidean_distance(path[i], path[i+1])
        if slope < 0 : total_energy += 0
        elif (0 <= slope and slope < rover.tanMidSlope) :
            total_energy += rover.lowSlopeEnergy
        elif (rover.tanMidSlope <= slope and slope < rover.tanHighSlope) :
            total_energy += rover.midSlopeEnergy
        else :
            total_energy += rover.highSlopeEnergy
    
    return total_energy

def path_solar_exposure(path : list[Location], mapHandler) :
    if path is None : 
        return 0

    nb_non_exposed_loc = 0
    for loc in path :
        nb_non_exposed_loc += has_sunlight_obstacle_h(None, loc, None, None, mapHandler)
    return 100 - 100 * nb_non_exposed_loc / len(path) # in percentage

def path_avg_altitude_change(path : list[Location]) :
    if path is None : 
        return 0

    total_alt_change = 0.0
    for i in range(len(path)-1) :
        total_alt_change += abs(altitude_difference(path[i], path[i+1]))
    return total_alt_change / len(path)