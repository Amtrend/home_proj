#!/usr/bin/env python
import subprocess
import datetime
import os
from work_with_db import WorkDb
from main_variables import RTSP_LINK, PATH_TO_SAVE, VIDEO_LENGTH, SIZE_LIMIT_OF_DIR, logger


def check_dir(target_path, size_limit):
    result = False
    size = 0
    for dirpath, dirnames, filenames in os.walk(target_path):
        all_files = [os.path.join(target_path, file) for file in filenames]
        try:
            first_file = min(all_files, key=os.path.getctime)
        except ValueError:
            pass
        for f in filenames:
            fp = os.path.join(dirpath, f)
            size += os.path.getsize(fp)
        if size > size_limit:
            result = True
            try:
                file_name = os.path.basename(first_file)
                worker_db = WorkDb()
                worker_db.delete_video_recording(name=file_name)
                os.remove(first_file)
            except Exception as e:
                logger.debug(f"Ошибка при удалении файла {file_name} и записи из бд: {e}")
    return result


def main(rtsp_link, path_to_save, video_length, size_limit):
    while True:
        check_res = check_dir(target_path=path_to_save, size_limit=size_limit)
        if not check_res:
            break
    start_recording = datetime.datetime.now()
    file_name = f'{start_recording.strftime(f"%d_%m_%Y-%H_%M_%S")}.mp4'
    file_path = os.path.join(path_to_save, file_name)
    command = f"ffmpeg -t {video_length} -i {rtsp_link} -vcodec copy {file_path}"
    save_video_proc = subprocess.run(command, shell=True, capture_output=True)
    if save_video_proc.returncode == 0:
        worker_db = WorkDb()
        falepath_to_db = os.path.join(r'archive/cam_entrance', file_name)
        worker_db.create_video_recording(title=file_name, path=falepath_to_db, start_record=start_recording)
    else:
        logger.debug(f"Ошибка при сохранении видео {file_name}: {save_video_proc.stdout}")


if __name__ == '__main__':
    while True:
        try:
            main(rtsp_link=RTSP_LINK, path_to_save=PATH_TO_SAVE, video_length=VIDEO_LENGTH,
                 size_limit=SIZE_LIMIT_OF_DIR)
        except Exception as e:
            logger.debug(f"Ошибка при запуске скрипта: {e}")
