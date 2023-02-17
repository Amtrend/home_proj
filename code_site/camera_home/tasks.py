from celery import shared_task
import requests
import os
import subprocess


TG_BOT_API = os.environ.get("TG_BOT_API")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
RTSP_LINK = os.environ.get("RTSP_LINK")


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


@shared_task(queue='for_alarm_entrance_task', name='alarm_entrance_task')
def go_alarm_entrance_task(targ_timesamp):
    try:
        filename = os.path.join(os.getcwd(), 'ae_video.mp4')
        command = f"ffmpeg -t 00:00:08 -i {RTSP_LINK} -vcodec copy {filename}"
        save_ae_video = subprocess.run(command, shell=True, capture_output=True)
        if save_ae_video.returncode == 0:
            try:
                send_tg_msg_and_video(api_key=TG_BOT_API, chat_id=TG_CHAT_ID, text_msg=f'Движение у <b>главного входа</b> в {targ_timesamp}', file='ae_video.mp4')
            except Exception as e:
                print(f'error with sending video - {e}')
            try:
                os.remove(filename)
            except Exception as e:
                print(f'error while deleting file: {e}')
        return "Выполнена задача по сработке у главного входа"
    except Exception as e:
        return f"Ошибка выполнения задачи по сработке у главного входа: {e}"
