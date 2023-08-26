import os
import datetime
import logging.config


RTSP_LINK = os.environ.get("RTSP_BE_LINK")
PATH_TO_SAVE = os.environ.get("PATH_TO_SAVE")
SIZE_LIMIT_OF_DIR = int(os.environ.get("SIZE_LIMIT_OF_DIR"))
VIDEO_LENGTH = os.environ.get("VIDEO_LENGTH")
LOGS = r"/code_app/logs"
DATABASE = os.environ.get("MYSQL_DATABASE")
HOST = "db"
USER = os.environ.get("MYSQL_USER")
PASSWORD = os.environ.get("MYSQL_PASSWORD")
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
