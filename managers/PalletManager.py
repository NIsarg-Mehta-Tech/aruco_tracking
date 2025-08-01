from entities.PalletObject import PalletObject
from shapely.geometry import Point
from execution_timing import *

class PalletManager:
    def __init__(self, roi_polygons, db_manager):
        self.roi_polygons = roi_polygons
        self.db_manager = db_manager
        self.pallets = {}

    @time_function
    def process_detections(self, detected_list, video_id, timestamp):
        """
        detected_list: list of tuples (aruco_id, center_x, center_y)
        video_id: string
        timestamp: datetime or timestamp of event

        Returns:
            List of tuples: (aruco_id, event, roi_index)
        """
        events = []

        for aruco_id, cx, cy in detected_list:
            point = Point(cx, cy)
            current_roi = None
            for i, poly in enumerate(self.roi_polygons, start=1):
                if poly.contains(point):
                    current_roi = i
                    break

            if aruco_id not in self.pallets:
                self.pallets[aruco_id] = PalletObject(aruco_id)

            pallet = self.pallets[aruco_id]
            event = pallet.update_location(current_roi)

            if event is not None:
                self.db_manager.insert_event(video_id, aruco_id, event, timestamp)
                events.append((aruco_id, event, current_roi))

        return events
