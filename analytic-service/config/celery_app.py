from kombu import Queue
from celery import Celery
import os

celery = Celery(
    "analytic_service",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery.conf.task_queues = (
    Queue("analytics", routing_key="analytics.#"),
)

celery.conf.task_default_queue = "analytics"
celery.conf.task_default_exchange = "analytics"
celery.conf.task_default_routing_key = "analytics.default"

import analitic.tasks


celery.conf.timezone = "UTC"