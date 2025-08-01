import threading
import cv2 as cv
import cv2.aruco as aruco
import numpy as np
from shapely.geometry import Polygon
from managers.PalletManager import PalletManager
from managers.DatabaseManager import DatabaseManager
from constants import *
from datetime import datetime
from execution_timing import *

class VideoObject(threading.Thread):
  
    def __init__(self, video_id, video_path, roi_points, frame_queue):
        super().__init__()
        self.video_id = video_id
        self.video_path = video_path
        self.roi_polygons = [Polygon(points) for points in roi_points]
        self.frame_queue = frame_queue
        self.db_manager = DatabaseManager(DB_CONFIG)
        self.pallet_manager = PalletManager(self.roi_polygons, self.db_manager)

    @time_function
    def run(self):
        cap = cv.VideoCapture(self.video_path)
        print(f"[{self.video_id}] Thread started")
        if not cap.isOpened():
            print(f"[{self.video_id}] Cannot open video")
            self.frame_queue.put(None)
            return

        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_7X7_1000)
        parameters = aruco.DetectorParameters()
        in_count, out_count = 0, 0
        last_seen_ids = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            increment_frame_count(self.video_id)

            # Draw ROI polygons
            for i, poly in enumerate(self.roi_polygons, start=1):
                pts = np.array([[int(x), int(y)] for x, y in poly.exterior.coords], np.int32)
                color = self.ROI_COLORS.get(i, (0, 255, 0))
                cv.polylines(frame, [pts], True, color, 2)
                centroid = poly.centroid
                cv.putText(frame, f"ROI {i}", (int(centroid.x), int(centroid.y)), cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Detect ArUco markers
            gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            frame = aruco.drawDetectedMarkers(frame, corners, ids)

            detected_list = []
            if ids is not None:
                for idx, corner in zip(ids.flatten(), corners):
                    c = corner[0]
                    center_x = int(c[:, 0].mean())
                    center_y = int(c[:, 1].mean())
                    detected_list.append((idx, center_x, center_y))
                    last_seen_ids[idx] = (center_x, center_y)
                    cv.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)

            # Draw all last seen ArUco IDs (even if not detected in this frame)
            for aruco_id, (x, y) in last_seen_ids.items():
                cv.putText(frame, f"ID:{aruco_id}", (x + 10, y), cv.FONT_HERSHEY_SIMPLEX, 1 , (0, 0, 255), 2)

            # Event processing
            timestamp = datetime.now()
            events = self.pallet_manager.process_detections(detected_list, self.video_id, timestamp)

            for aruco_id, event, roi_index in events:
                if roi_index is None:
                    continue
                poly = self.roi_polygons[roi_index - 1]
                centroid = poly.centroid
                text_pos = (int(centroid.x), int(centroid.y))

                color = self.EVENT_COLORS.get(event, (0, 255, 0))
                cv.putText(frame, f"ID {aruco_id} {event}", text_pos, cv.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                if event.upper() == "IN":
                    in_count += 1
                elif event.upper() == "OUT":
                    out_count += 1

            # Display IN/OUT count
            cv.putText(frame, f"IN: {in_count}", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv.putText(frame, f"OUT: {out_count}", (10, 180), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            # Resize and send to queue
            small_frame = cv.resize(frame, (640, 360))
            self.frame_queue.put(small_frame)

        cap.release()
        self.frame_queue.put(None)