import mysql.connector
from execution_timing import *

class DatabaseManager:
    def __init__(self, db_config):
        # Connect to the MySQL database using provided config dict
        self.connection = mysql.connector.connect(**db_config)
        self.create_table_if_not_exists()

    @time_function
    def create_table_if_not_exists(self):
        """
            This module defines the DatabaseManager class, responsible for managing all database-related operations for the ArUco marker detection system. It handles:
                - Establishing a connection to the MySQL database using the given configuration.
                - Creating the required table (`aruco_detection`) if it does not already exist.
                - Inserting detection event records (video ID, marker ID, event type, timestamp).
                - Tracking function execution time for performance logging.
        """
        # Create table if not exists with the required schema
        query = """
        CREATE TABLE IF NOT EXISTS aruco_detection (
            id INT AUTO_INCREMENT PRIMARY KEY,
            video_id VARCHAR(255),
            aruco_code VARCHAR(255),
            event_type VARCHAR(10),
            event_time TIMESTAMP
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    @time_function
    def insert_event(self, video_id, aruco_code, event_type, event_time):
        # Insert a new detection event into the table
        query = """
        INSERT INTO aruco_detection (video_id, aruco_code, event_type, event_time)
        VALUES (%s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (video_id, str(aruco_code), event_type, event_time))
        self.connection.commit()
        cursor.close()
