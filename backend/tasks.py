import os
from celery import Celery
from celery.app import autoretry

from resources.util import get_result

celery = Celery(__name__)
celery.conf.broker_url = os.environ['CELERY_BROKER_URL']
celery.conf.result_backend = os.environ['CELERY_RESULT_BACKEND']
celery.conf.update(result_extended=True)


@celery.task(name="start_ticker_ai")
def start_ticker_ai(ticker, multiplier, horizon):
    return get_result(ticker, multiplier, horizon)
