from celery import shared_task
from celery.contrib.abortable import AbortableTask, AbortableAsyncResult
from smart_home import celery_app
from celery.signals import worker_ready
import requests
import os
from datetime import datetime as dt
import subprocess
from .models import *
import RPi.GPIO as GPIO


TG_BOT_API = os.environ.get("TG_BOT_API")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
PIR_SENSOR = int(os.environ.get("PIR_SENSOR"))
RTSP_LINK = os.environ.get("RTSP_LINK")
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_SENSOR, GPIO.IN)


def send_tg_msg(api_key, chat_id, text_msg):
    data_send = {
        'chat_id': chat_id,
        'text': text_msg,
        'parse_mode': 'html',
    }
    response = requests.get(f'https://api.telegram.org/bot{api_key}/sendMessage', data=data_send)
    return response


def send_tg_msg_and_file(api_key, chat_id, text_msg, file):
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


def catch_motion_ae(gpio, pir, dt, r_link):
    if gpio.input(pir):
        cur_dt = dt.now().strftime("%H:%M:%S %d.%m.%Y")
        filename = os.path.join(os.getcwd(), 'ae_video.mp4')
        command = f"ffmpeg -t 00:00:05 -i {r_link} -vcodec copy {filename}"
        save_ae_video = subprocess.run(command, shell=True, capture_output=True)
        if save_ae_video.returncode == 0:
            send_tg_msg_and_file(api_key=TG_BOT_API, chat_id=TG_CHAT_ID, text_msg=f'Движение у <b>главного входа</b> в {cur_dt}', file='ae_video.mp4')
            os.remove(filename)


@shared_task(bind=True, base=AbortableTask, acks_late=True, queue='for_alarm_entrance_task', name='alarm_entrance_task')
def go_alarm_entrance_task(self):
    try:
        if self.request.retries == 5:
            send_tg_msg(api_key=TG_BOT_API, chat_id=TG_CHAT_ID, text_msg=f'<b>Внимание!</b> пятая попытка выполнения задачи {self.name}!')
        while not self.is_aborted():
            try:
                catch_motion_ae(gpio=GPIO, pir=PIR_SENSOR, dt=dt, r_link=RTSP_LINK)
            except Exception as e:
                print(f'wtf error : {e}')
    except Exception as e:
        result = f'some error : {e}'
        raise self.retry(countdown=5, exc=e, max_retries=5)
    else:
        result = 'task will be aborted'
    return result


@worker_ready.connect
def at_start_workers(sender, **kwargs):
    if sender.hostname == 'celery@alarm_entrance_worker':
        cur_ae_sets = AlarmEntranceSettings.objects.first()
        if cur_ae_sets.ae_on:
            cur_ae_task_id = cur_ae_sets.ae_task_id
            revoked = AbortableAsyncResult(cur_ae_task_id)
            revoked.abort()
            new_task = go_alarm_entrance_task.delay()
            cur_ae_sets.ae_task_id = new_task.id
            cur_ae_sets.save()
