# app.py
from managers.VideoManager import VideoManage
import cv2 as cv
import atexit
from execution_timing import *

record_program_start()

def on_exit():
    record_program_end()
    write_report()

atexit.register(on_exit)

if __name__ == "__main__":
    manager = VideoManage()
    manager.run_all_videos()
    cv.destroyAllWindows()
