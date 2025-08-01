from execution_timing import time_function


class PalletObject:
    def __init__(self, aruco_id):
        self.aruco_id = aruco_id
        self.last_roi = None  # None or 1 or 2

    @time_function
    def update_location(self, current_roi):
        event = None

        if self.last_roi == 1 and current_roi == 2:
            # Entering ROI from outside
            event = "IN"
        elif self.last_roi == 2 and current_roi == 1:
            # Exiting ROI to outside
            event = "OUT"

        self.last_roi = current_roi
        return event
