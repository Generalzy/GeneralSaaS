# import django
# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GeneralSaaS.settings")
# django.setup()
from celery import Celery

broker = 'redis://127.0.0.1:6379/2'
backend = 'redis://127.0.0.1:6379/3'

app = Celery(__name__, broker=broker, backend=backend, include=['celery_task.web_task'])
