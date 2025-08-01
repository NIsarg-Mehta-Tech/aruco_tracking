import json
import cv2 as cv
import queue
from entities.VideoObject import VideoObject
from constants import *
from execution_timing import *

class VideoManage:
    def __init__(self):
        self.roi_data = None
        self.frame_queue = queue.Queue()

    @time_function
    def load_roi(self):
        with open(ROI_JSON_PATH, 'r') as f:
            self.roi_data = json.load(f)

    @time_function
    def run_all_videos(self):
        self.load_roi()

        for video_name, video_path in VIDEO_PATHS.items():
            roi_entry = next((item for item in self.roi_data if item["camera_name"] == video_name), None)
            print(f"[App] Starting {video_name}")
            if roi_entry is None:
                print(f"No ROI data for {video_name}")
                continue

            cap = cv.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Cannot open video {video_path}")
                continue
            width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
            cap.release()

            scaled_rois = []
            for roi in roi_entry["rois"]:
                points = roi["points"]
                if points[0] == points[-1]:
                    points = points[:-1]
                scaled_points = [(int(pt[0] * width), int(pt[1] * height)) for pt in points]
                scaled_rois.append(scaled_points)

            record_video_start(video_name)
            video_obj = VideoObject(video_name, video_path, scaled_rois, self.frame_queue)
            video_obj.start()

            while True:
                frame = self.frame_queue.get()
                if frame is None:
                    break
                cv.imshow(f"Video {video_name}", frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

            video_obj.join()
            cv.destroyWindow(f"Video {video_name}")
            record_video_end(video_name)
