import os
import sys
import time
import shutil
import cv2
from PIL import Image
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


quality = 0

def compress_frame(filename, src, dst, frame_quality):
    filepath = os.path.join(src, filename)
    dst_path = os.path.join(dst, "Compressed_"+filename)
    picture = Image.open(filepath)
    picture.save(dst_path,
                 "JPEG",
                 quality = frame_quality)

def make_dir(src_path, dir):
    if dir == "":
        path = src_path
    else:
        path = os.path.join(src_path, dir)
    try:
        # Create target Directory
        os.mkdir(path)
        print("Directory ", path, " Created ")
    except FileExistsError:
        print("Directory ", path, " already exists")

class MonitorFolder(FileSystemEventHandler):

    def get_frames(self , filename, parent):
        video_path = os.path.join(parent, 'Train', filename)
        compressed_video_path = os.path.join(parent, 'Annotation', filename)
        make_dir(video_path, "")
        make_dir(compressed_video_path, "")
        vidcap = cv2.VideoCapture(filename)
        success, image = vidcap.read()
        count = 0
        while success:
            frame_path = os.path.join(video_path, "frame%d.png" % count)
            cv2.imwrite(frame_path, image) # save frame as JPEG file
            compress_frame("frame%d.png" % count, video_path, compressed_video_path, quality)
            success, image = vidcap.read()
            count += 1

    def on_created(self, event):
        parent = Path(event.src_path).parent.absolute()
        filename = os.path.basename(event.src_path)
        RAW_folder = os.path.join(parent, 'RAW', filename)
        shutil.copy(event.src_path, RAW_folder)
        self.get_frames(filename, parent)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Wrong number of arguments! Two arguments required: directory and quality")
        exit()
    src_path = sys.argv[1]
    quality = int(sys.argv[2])
    make_dir(src_path, 'RAW')
    make_dir(src_path, 'Train')
    make_dir(src_path, 'Annotation')
    event_handler = MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=False)
    print("Monitoring started")
    observer.start()
    try:
        while (True):
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()