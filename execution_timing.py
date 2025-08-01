import time
from collections import defaultdict

# Global timing and frame stats
timing_stats = defaultdict(float)
frame_counts = defaultdict(int)
video_start_times = {}
video_end_times = {}
program_start_time = None
program_end_time = None

# Decorator to measure function execution time
def time_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        timing_stats[func.__name__] += end - start
        return result
    return wrapper

# Program-level timing
def record_program_start():
    global program_start_time
    program_start_time = time.time()

def record_program_end():
    global program_end_time
    program_end_time = time.time()

# Per-video timing
def record_video_start(video_name):
    video_start_times[video_name] = time.time()

def record_video_end(video_name):
    video_end_times[video_name] = time.time()

# Frame count tracking
def increment_frame_count(video_id):
    frame_counts[video_id] += 1

# Final report writer
def write_report():
    with open("execution_report.txt", "w") as f:
        f.write("Execution Timing Report\n")
        f.write("=" * 60 + "\n\n")

        f.write("Function Execution Times:\n")
        for func, total_time in timing_stats.items():
            f.write(f"{func:<35} : {total_time:.4f} seconds\n")

        f.write("\nPer-Video Execution Times:\n")
        for video, start in video_start_times.items():
            end = video_end_times.get(video)
            if end:
                duration = end - start
                f.write(f"{video:<35} : {duration:.4f} seconds\n")

        total_video_time = sum(
            video_end_times[v] - video_start_times[v]
            for v in video_start_times
            if v in video_end_times
        )
        f.write(f"\nTotal Video Processing Time         : {total_video_time:.4f} seconds\n")

        if program_end_time:
            total_program_time = program_end_time - program_start_time
            f.write(f"Total Program Execution Time        : {total_program_time:.4f} seconds\n")

        f.write("\nFrame Count Per Video:\n")
        for video_id, count in frame_counts.items():
            f.write(f"{video_id:<35} : {count} frames\n")
