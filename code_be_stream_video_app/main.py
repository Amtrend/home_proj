#!/usr/bin/env python
import subprocess
import os
import logging.config
import datetime


RTSP_LINK = os.environ.get("RTSP_BE_LINK")
PATH_TO_SAVE = os.environ.get("PATH_TO_SAVE")
LOGS = r"/code_app/logs"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            'format': '%(asctime)s : [%(levelname)s] : %(message)s',
            'datefmt': '%d-%b-%y %H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{LOGS}/{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.txt',
            'formatter': 'default_formatter',
            'maxBytes': 1048576,
            'backupCount': 10,
        },
    },
    'loggers': {
        'my_logger': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


def main(rtsp_link, path_to_save):
    output_path = os.path.join(path_to_save, 'streaming.m3u8')
    command = f"ffmpeg -i {rtsp_link} -c copy -hls_time 2 -hls_wrap 10 {output_path}"
    save_video_proc = subprocess.run(command, shell=True, capture_output=True)
    if save_video_proc.returncode != 0:
        logger.debug(f"Ошибка при стримминге видео: {save_video_proc.stdout}")


if __name__ == '__main__':
    while True:
        try:
            main(rtsp_link=RTSP_LINK, path_to_save=PATH_TO_SAVE)
        except Exception as e:
            logger.debug(f"Ошибка при запуске скрипта: {e}")
