#!/usr/bin/env python
import cv2
import datetime
import os


RTSP_LINK = os.environ.get("RTSP_LINK")
PATH_TO_SAVE = os.environ.get("PATH_TO_SAVE")
SIZE_LIMIT_OF_DIR = os.environ.get("SIZE_LIMIT_OF_DIR")
VIDEO_LENGTH = os.environ.get("VIDEO_LENGTH")


def main(stream_link, target_path, size_limit, video_length):
    cap = cv2.VideoCapture(stream_link)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    frame_size = (frame_width, frame_height)
    cur_date = datetime.datetime.now().strftime(f"%d_%m_%Y(%H_%M_%S)")
    file_name = os.path.join(target_path, f'{cur_date}.mp4')
    out = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 20, frame_size)
    cur_size = 0
    for dirpath, dirnames, filenames in os.walk(target_path):
        all_files = [os.path.join(target_path, file) for file in filenames]
        try:
            first_file = min(all_files, key=os.path.getctime)
        except ValueError:
            pass
        for f in filenames:
            fp = os.path.join(dirpath, f)
            cur_size += os.path.getsize(fp)
        if cur_size > size_limit:
            os.remove(first_file)
    i = 0
    while True:
        ret, frame = cap.read()
        out.write(frame)
        i += 1
        if i > (video_length * 20):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    while True:
        try:
            main(stream_link=RTSP_LINK, target_path=PATH_TO_SAVE, size_limit=SIZE_LIMIT_OF_DIR, video_length=VIDEO_LENGTH)
        except KeyboardInterrupt:
            break
