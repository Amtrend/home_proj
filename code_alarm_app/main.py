import RPi.GPIO as GPIO
import time
import datetime as dt
import os


TG_BOT_API = os.environ.get("TG_BOT_API")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

GPIO.setmode(GPIO.BCM)
PIR_SENSOR = 18
GPIO.setup(PIR_SENSOR, GPIO.IN)


def check_motion(sensor):
    print(f"Motion detect at {dt.datetime.now()} - {sensor}")
    time.sleep(10)
    print('end doing func')

try:
    while True:
        if GPIO.input(PIR_SENSOR):
            check_motion(PIR_SENSOR)
except Exception as e:
    print(f"some error - {e}")
    GPIO.cleanup()
