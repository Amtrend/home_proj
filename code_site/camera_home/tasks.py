from celery import shared_task
import time
from celery.contrib.abortable import AbortableTask


# @shared_task(bind=True, base=AbortableTask)
# def go_test_task(self, test_msg):
#     try:
#         while not self.is_aborted():
#             print(f'i am test task - {test_msg}')
#             time.sleep(3)
#     except Exception as e:
#         print(f'some error : {e}')


@shared_task(bind=True)
def go_test_task(self, test_msg):
    try:
        # while not self.is_aborted():
        print(f'i am test task - {test_msg}')
        time.sleep(20)
        print('end')
        print(self)
    except Exception as e:
        print(f'some error : {e}')
