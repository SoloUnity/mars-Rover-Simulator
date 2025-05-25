# Callum Airlie
import uuid
from datetime import datetime
from database.db import get_connection
from models.rover import Rover, get_rover_by_id, get_rovers_by_project
from models.trajectory import get_trajectory_by_id
import sqlite3

class Project:
    def __init__(self, project_id=None, project_name=None, created_on=None, last_accessed=None,
                 top_left_x=0.0, top_left_y=0.0, bottom_right_x=100.0, bottom_right_y=100.0):
        self.project_id = project_id or str(uuid.uuid4())
        self.project_name = project_name
        self.created_on = created_on or datetime.now()
        self.last_accessed = last_accessed or datetime.now()
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y
        self.rovers: list[Rover] = []

    def get_rovers(self):
        self.rovers = get_rovers_by_project(self.project_id)

def get_project_by_id(project_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Project WHERE ProjectID = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Project(
            project_id=row["ProjectID"], 
            project_name=row["ProjectName"],
            created_on=row["CreatedOn"], 
            last_accessed=row["LastAccessed"],
            top_left_x=row["TopLeftX"],
            top_left_y=row["TopLeftY"],
            bottom_right_x=row["BottomRightX"],
            bottom_right_y=row["BottomRightY"]
        )
    return None

def get_all_projects() -> list[Project]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Project ORDER BY LastAccessed DESC")
    rows = cursor.fetchall()
    conn.close()
    
    projects = []
    for row in rows:
        projects.append(Project(
            project_id=row["ProjectID"],
            project_name=row["ProjectName"],
            created_on=row["CreatedOn"], 
            last_accessed=row["LastAccessed"],
            top_left_x=row["TopLeftX"],
            top_left_y=row["TopLeftY"],
            bottom_right_x=row["BottomRightX"],
            bottom_right_y=row["BottomRightY"]
        ))
    return projects


def get_last_accessed():
    projects = get_all_projects()
    if not projects:
        return None, None, None
    last_project = projects[0]

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Rover WHERE ProjectID = ? ORDER BY LastAccessed DESC LIMIT 1",
        (last_project.project_id,)
    )
    rover_row = cursor.fetchone()
    rover = None
    trajectory = None
    if rover_row:
        rover = get_rover_by_id(rover_row["RoverID"])
        cursor.execute(
            "SELECT * FROM Trajectory WHERE RoverID = ? ORDER BY LastAccessed DESC LIMIT 1",
            (rover.rover_id,)
        )
        traj_row = cursor.fetchone()
        if traj_row:
            trajectory = get_trajectory_by_id(traj_row["TrajectoryID"])
    conn.close()
    return last_project, rover, trajectory

def create_project(project):
    conn = get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO Project 
               (ProjectID, ProjectName, CreatedOn, LastAccessed, TopLeftX, TopLeftY, BottomRightX, BottomRightY) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    try:
        cursor.execute(query, (
            project.project_id,
            project.project_name,
            project.created_on,
            project.last_accessed,
            project.top_left_x,
            project.top_left_y,
            project.bottom_right_x,
            project.bottom_right_y
        ))
        conn.commit()
        return project
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback() 
        return None
    finally:
        conn.close()


def update_project(project):
    conn = get_connection()
    cursor = conn.cursor()
    query = """UPDATE Project 
              SET LastAccessed = ?, TopLeftX = ?, TopLeftY = ?, 
                  BottomRightX = ?, BottomRightY = ? 
              WHERE ProjectID = ?"""
    cursor.execute(query, (
        datetime.now(),
        project.top_left_x,
        project.top_left_y,
        project.bottom_right_x,
        project.bottom_right_y,
        project.project_id
    ))
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_updated > 0

def save_project(project):
    exists = get_project_by_id(project.project_id)
    if exists:
        return update_project(project)
    else:
        return create_project(project)

def delete_project(project):
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM Project WHERE ProjectID = ?"
    try:
        cursor.execute(query, (project.project_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        return rows_deleted > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()