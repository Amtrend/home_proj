import logging
import os
import requests
import subprocess

from celery import shared_task
from django.core.cache import cache
from requests.auth import HTTPDigestAuth
from smart_home.settings import RTSP_LINK, TG_BOT_API, TG_CHAT_ID, MAIN_CAMERA_PASS, MAIN_CAMERA_USER, MAIN_CAMERA_SNAPSHOT_LINK

DEBOUNCE_SECONDS = 7
PHOTO_FILENAME = 'ae_photo.jpeg'
MODEL_CAMERA_MAP = {
    'cam_entrance': {
        'model': CameraEntranceSaveVideos,
        'upload_to': 'archive/cam_entrance',
        'dir_path': os.path.join(MEDIA_ROOT, 'archive', 'cam_entrance'),
    },
    'cam_back_entrance': {
        'model': CameraBEntranceSaveVideos,
        'upload_to': 'archive/cam_b_entrance',
        'dir_path': os.path.join(MEDIA_ROOT, 'archive', 'cam_b_entrance'),
    }
}

_logger = logging.getLogger(__name__)


def rotate_archive(archive_dir, model_class, size_limit_bytes):
    if not os.path.exists(archive_dir):
        return

    files = [f for f in os.listdir(archive_dir) if f.endswith('.mp4')]
    files_with_paths = [(f, os.path.join(archive_dir, f)) for f in files]
    files_with_paths.sort(key=lambda x: os.path.getmtime(x[1]))

    current_size = sum(os.path.getsize(fp) for _, fp in files_with_paths)
    if current_size <= size_limit_bytes:
        return

    for filename, filepath in files_with_paths:
        if current_size <= size_limit_bytes:
            break

        file_size = os.path.getsize(filepath)

        try:
            os.unlink(filepath)
        except Exception as e:
            _logger.error(f'Failed to delete {filepath}: {e}')
            continue

        try:
            record = model_class.objects.filter(video__endswith=filename).first()
            if record:
                record.delete()
        except Exception as e:
            _logger.error(f'Failed to delete db record for {filename}: {e}')

        current_size -= file_size

def send_tg_msg_and_video(api_key, chat_id, text_msg, file):
    data_send = {
        'chat_id': chat_id,
        'caption': text_msg,
        'parse_mode': 'html',
    }
    file_send = {
        'video': open(file, 'rb'),
    }
    response = requests.post(f'https://api.telegram.org/bot{api_key}/sendVideo', data=data_send, files=file_send)
    return response


def send_tg_msg_and_photo(api_key, chat_id, text_msg, file):
    data_send = {
        'chat_id': chat_id,
        'caption': text_msg,
        'parse_mode': 'html',
    }
    file_send = {
        'photo': open(file, 'rb'),
    }
    response = requests.post(f'https://api.telegram.org/bot{api_key}/sendPhoto', data=data_send, files=file_send)
    return response

@shared_task(queue='for_alarm_entrance_task', name='main_entrance_alarm_task')
def main_entrance_alarm_task(targ_timestamp):
    cache_key = "motion_last_cam_entrance"

    if cache.get(cache_key):
        return "Alarm skipped: debounce active"

    cache.set(cache_key, True, timeout=7)

    try:
        response = requests.get(
            url=MAIN_CAMERA_SNAPSHOT_LINK,
            auth=HTTPDigestAuth(MAIN_CAMERA_USER, MAIN_CAMERA_PASS),
            timeout=DEBOUNCE_SECONDS
        )
        if response.status_code == 200:
            with open(PHOTO_FILENAME, 'wb') as f:
                f.write(response.content)

            try:
                send_tg_msg_and_photo(
                    api_key=TG_BOT_API,
                    chat_id=TG_CHAT_ID,
                    text_msg=f'Движение у <b>главного входа</b> в {targ_timestamp}',
                    file=PHOTO_FILENAME
                )
            except Exception as e:
                print(f'Ошибка при отправке фото: {e}')
        else:
            return "Ошибка при выполнении запроса к камере"

    except Exception as e:
        return f"Ошибка при получении снимка: {e}"
    finally:
        try:
            if os.path.exists(PHOTO_FILENAME):
                os.remove(PHOTO_FILENAME)
        except Exception as e:
            print(f'Ошибка при удалении файла: {e}')
    return "Задача по сработке у главного входа выполнена"


@shared_task(queue='for_alarm_entrance_task', name='go_alarm_entrance_task')
def go_alarm_entrance_task(targ_timesamp):
    try:
        filename = os.path.join(os.getcwd(), 'ae_photo.jpeg')
        command = f"ffmpeg -i {RTSP_LINK} -f image2 -vframes 1 {filename}"
        save_ae_photo = subprocess.run(command, shell=True, capture_output=True)
        if save_ae_photo.returncode == 0:
            try:
                send_tg_msg_and_photo(api_key=TG_BOT_API, chat_id=TG_CHAT_ID, text_msg=f'Движение у <b>главного входа</b> в {targ_timesamp}', file='ae_photo.jpeg')
            except Exception as e:
                print(f'ошибка при отправке фото - {e}')
            try:
                os.remove(filename)
            except Exception as e:
                print(f'ошибка при удалении файла - {e}')
        else:
            return "ошибка при записи фото с камеры"
        return "выполнена задача по сработке у главного входа"
    except Exception as e:
        return f"ошибка выполнения задачи по сработке у главного входа: {e}"


@shared_task(queue='for_alarm_entrance_task', name='go_alarm_entrance_task_video')
def go_alarm_entrance_task_video(targ_timesamp):
    try:
        filename = os.path.join(os.getcwd(), 'ae_video.mp4')
        command = f"ffmpeg -t 00:00:08 -i {RTSP_LINK} -vcodec copy {filename}"
        save_ae_video = subprocess.run(command, shell=True, capture_output=True)
        if save_ae_video.returncode == 0:
            try:
                send_tg_msg_and_video(api_key=TG_BOT_API, chat_id=TG_CHAT_ID, text_msg=f'Движение у <b>главного входа</b> в {targ_timesamp}', file='ae_video.mp4')
            except Exception as e:
                print(f'ошибка при отправке видео - {e}')
            try:
                os.remove(filename)
            except Exception as e:
                print(f'ошибка при удалении файла - {e}')
        else:
            return "ошибка при записи видео с камеры"
        return "выполнена задача по сработке у главного входа"
    except Exception as e:
        return f"ошибка выполнения задачи по сработке у главного входа: {e}"

@shared_task(queue='for_alarm_entrance_task', name='save_webrtc_video_task')
def save_webrtc_video_task(path, filename):
    if path not in MODEL_CAMERA_MAP:
        _logger.error(f'Unknown path {path}')
        return f'Unknown path {path}'

    config = MODEL_CAMERA_MAP[path]
    model_class = config['model']
    upload_to = config['upload_to']
    archive_dir = config['dir_path']
    base_name = os.path.basename(filename)
    title = base_name.replace('.mp4', '')

    try:
        start_recording = dt.strptime(title, '%Y-%m-%d_%H-%M-%S') + timedelta(hours=3)
    except ValueError:
        _logger.error(f'Cannot parse timestamp from filename: {filename}')
        return f'Cannot parse timestamp from filename: {filename}'

    video_record = model_class(title=title, video=f'{upload_to}/{base_name}', start_recording=start_recording)
    video_record.save()

    try:
        size_limit_bytes = int(os.getenv('SIZE_LIMIT_OF_DIR', 37580963840))
        rotate_archive(archive_dir=archive_dir, model_class=model_class, size_limit_bytes=size_limit_bytes)
    except Exception as e:
        _logger.error(f'Rotation failed for {path}: {e}')

    return "Task to save video from webrtc successfully completed"
