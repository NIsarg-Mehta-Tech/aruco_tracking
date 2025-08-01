from managers.VideoManager import VideoManage
import cv2 as cv
import atexit
from execution_timing import *

"""
    Main entry point for the ArUco Detection and Tracking System.
        - Initializes the video manager to process all videos sequentially.
        - Uses atexit to ensure proper report writing on exit.
"""
record_program_start()

def on_exit():
    record_program_end()
    write_report()

atexit.register(on_exit)

if __name__ == "__main__":
    manager = VideoManage()
    manager.run_all_videos()
    cv.destroyAllWindows()
