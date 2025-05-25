# Callum Airlie
import math
import sqlite3
import uuid
from datetime import datetime

from database.db import get_connection
from src.ai_algos.heuristics import *

class Rover:
    def __init__(self, rover_id=None, project_id=None, name='', weight=0.0, yearLaunched=None, status='Healthy', 
                 manufacturer='', top_speed=0.0, wheel_count=0, max_incline=0.0, last_trajectory=None, 
                 total_distance_traveled=0.0, power_source='', description='', last_accessed=None,
                 lowSlopeEnergy=0.0, midSlopeEnergy=0.0, highSlopeEnergy=0.0, heuristics=[], distance_method=None):
        self.rover_id = rover_id or str(uuid.uuid4())
        self.project_id = project_id
        self.name = name
        self.weight = weight
        self.yearLaunched = yearLaunched or datetime.now().year
        self.status = status
        self.manufacturer = manufacturer
        self.top_speed = top_speed
        self.wheel_count = wheel_count
        self.max_incline = max_incline
        self.last_trajectory = last_trajectory
        self.total_distance_traveled = total_distance_traveled
        self.power_source = power_source
        self.description = description
        self.last_accessed = last_accessed or datetime.now()
        self.lowSlopeEnergy = lowSlopeEnergy
        self.midSlopeEnergy = midSlopeEnergy
        self.highSlopeEnergy = highSlopeEnergy
        self.tanMaxSlope = math.tan(math.radians(max_incline))
        self.tanHighSlope = math.tan(math.radians(2 * max_incline/3))
        self.tanMidSlope = math.tan(math.radians(max_incline/3))

        self.heuristics: list[tuple[float, callable]] = heuristics
        self.distance_method: callable = distance_method
        
    def set_heuristics(self, h):
        self.heuristics = h.copy()
    
    def get_heuristics(self):
        return self.heuristics.copy()
    
    def set_distance_method(self, fn):
        self.distance_method = fn

    def get_distance_method(self):
        return self.distance_method

def get_rover_by_id(rover_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rover WHERE RoverID = ?", (rover_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Rover(
            rover_id=row["RoverID"],
            project_id=row["ProjectID"],
            name=row["Name"],
            weight=row["Weight"],
            yearLaunched=row["yearLaunched"],
            status=row["Status"],
            manufacturer=row["Manufacturer"],
            top_speed=row["topSpeed"],
            wheel_count=row["wheelCount"],
            max_incline=row["maxIncline"],
            last_trajectory=row["lastTrajectory"],
            total_distance_traveled=row["totalDistanceTraveled"],
            power_source=row["powerSource"],
            description=row["description"],
            last_accessed=row["LastAccessed"],
            lowSlopeEnergy=row["lowSlopeEnergy"],
            midSlopeEnergy=row["midSlopeEnergy"],
            highSlopeEnergy=row["highSlopeEnergy"]
        )
    return None

def get_all_rovers():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rover")
    rows = cursor.fetchall()
    conn.close()
    rovers = []
    map = {
        "Euclidean": euclidean_distance_h,
        "Manhattan": manhattan_distance_h,
        "Geographical": geographical_distance_h 
    }
    for row in rows:
        dist_method = row["distanceMethod"]
        dist = row["distanceH"]
        stable = row["stableAltitudeH"]
        solar = row["solarH"]
        energy = row["energyH"]
        low = row["lowAltitudeH"]

        h = [
            (dist, map[dist_method]),
            (stable, stable_altitude_h),
            (solar, has_sunlight_obstacle_h),
            (energy, energy_for_slope_h),
            (low, low_altitude_h)
        ]

        h = [(w, fn) for w, fn in h if w != 0]

        rovers.append(Rover(
            rover_id=row["RoverID"],
            project_id=row["ProjectID"],
            name=row["Name"],
            weight=row["Weight"],
            yearLaunched=row["yearLaunched"],
            status=row["Status"],
            manufacturer=row["Manufacturer"],
            top_speed=row["topSpeed"],
            wheel_count=row["wheelCount"],
            max_incline=row["maxIncline"],
            last_trajectory=row["lastTrajectory"],
            total_distance_traveled=row["totalDistanceTraveled"],
            power_source=row["powerSource"],
            description=row["description"],
            last_accessed=row["LastAccessed"],
            lowSlopeEnergy=row["lowSlopeEnergy"],
            midSlopeEnergy=row["midSlopeEnergy"],
            highSlopeEnergy=row["highSlopeEnergy"],
            heuristics=h,
            distance_method=map[dist_method]
        ))
    return rovers

# This needs to be here to prevent circular importing. Please don't remove.
from models.presets import (create_curiosity, create_lunokhod1,
                            create_lunokhod2, create_perseverance)


def create_rover(rover_type: str | Rover, project_id):
    rover = rover_type # if it's a Rover instance
    if type(rover_type) == str:
        r = rover_type.lower()
        if r == "curiosity":
            rover = create_curiosity()
        elif r == "perseverance":
            rover = create_perseverance()
        elif r == "lunokhod1":
            rover = create_lunokhod1()
        elif r == "lunokhod2":
            rover = create_lunokhod2()
        else:
            raise ValueError("Unknown rover type: " + rover_type)

    rover.project_id = project_id
    stable, solar, energy, low = 0, 0, 0, 0
    dist = 0
    for val, h in rover.get_heuristics():
        match h.__name__:
            case "stable_altitude_h":
                stable = val
                continue
            case "has_sunlight_obstacle_h":
                solar = val
                continue
            case "energy_for_slope_h":
                energy = val
                continue
            case "low_altitude_h":
                low = val
                continue
            case _:
                dist = val
                continue

    map = {
        "euclidean_distance_h": "Euclidean",
        "manhattan_distance_h": "Manhattan",
        "geographical_distance_h": "Geographical"
    }

    dist_method = map[rover.get_distance_method().__name__]

    conn = get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO Rover 
               (RoverID, ProjectID, Name, Weight, yearLaunched, Status, Manufacturer, topSpeed, 
                wheelCount, maxIncline, lastTrajectory,
                totalDistanceTraveled, powerSource, description, LastAccessed,
                lowSlopeEnergy, midSlopeEnergy, highSlopeEnergy, distanceMethod, distanceH,
                stableAltitudeH, solarH, energyH, lowAltitudeH) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(query, (
        rover.rover_id,
        rover.project_id,
        rover.name,
        rover.weight,
        rover.yearLaunched,
        rover.status,
        rover.manufacturer,
        rover.top_speed,
        rover.wheel_count,
        rover.max_incline,
        rover.last_trajectory,
        "rover.sprite_file_path",
        rover.total_distance_traveled,
        rover.power_source,
        rover.description,
        rover.lowSlopeEnergy,
        rover.midSlopeEnergy,
        rover.highSlopeEnergy,
        dist_method, dist,
        stable, solar, energy, low
    ))
    conn.commit()
    conn.close()
    
    return rover

def delete_rover(rover_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM Rover WHERE RoverID = ?"
    cursor.execute(query, (rover_id,))
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_deleted > 0

def update_rover(rover):
    conn = get_connection()
    cursor = conn.cursor()
    query = """UPDATE Rover SET 
               ProjectID = ?,
               Name = ?,
               Weight = ?,
               yearLaunched = ?,
               Status = ?,
               Manufacturer = ?,
               topSpeed = ?,
               wheelCount = ?,
               maxIncline = ?,
               lastTrajectory = ?,
               totalDistanceTraveled = ?,
               powerSource = ?,
               description = ?,
               LastAccessed = ?,
               lowSlopeEnergy = ?,
               midSlopeEnergy = ?,
               highSlopeEnergy = ?
               WHERE RoverID = ?"""
    cursor.execute(query, (
        rover.project_id,
        rover.name,
        rover.weight,
        rover.yearLaunched,
        rover.status,
        rover.manufacturer,
        rover.top_speed,
        rover.wheel_count,
        rover.max_incline,
        rover.last_trajectory,
        rover.sprite_file_path,
        rover.total_distance_traveled,
        rover.power_source,
        rover.description,
        datetime.now(),
        rover.lowSlopeEnergy,
        rover.midSlopeEnergy,
        rover.highSlopeEnergy,
        rover.rover_id
    ))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0

def get_rovers_by_project(project_id) -> list[Rover]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rover WHERE ProjectID = ?", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    rovers = []
    for row in rows:
        rovers.append(Rover(
            rover_id=row["RoverID"],
            project_id=row["ProjectID"],
            name=row["Name"],
            weight=row["Weight"],
            yearLaunched=row["yearLaunched"],
            status=row["Status"],
            manufacturer=row["Manufacturer"],
            top_speed=row["topSpeed"],
            wheel_count=row["wheelCount"],
            max_incline=row["maxIncline"],
            last_trajectory=row["lastTrajectory"],
            total_distance_traveled=row["totalDistanceTraveled"],
            power_source=row["powerSource"],
            description=row["description"],
            last_accessed=row["LastAccessed"],
            lowSlopeEnergy=row["lowSlopeEnergy"],
            midSlopeEnergy=row["midSlopeEnergy"],
            highSlopeEnergy=row["highSlopeEnergy"]
        ))
    return rovers

def save_rover(rover):
    exists = get_rover_by_id(rover.rover_id)
    if exists:
        return update_rover(rover)
    else:
        return create_rover(rover)