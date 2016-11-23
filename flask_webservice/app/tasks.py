import random
import time
# from celery import shared_task

from . import celery
from svr.svr import predict


@celery.task(bind=True)
def long_task(self, imgpath):
    result = predict(imgpath, self)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': result[0]}