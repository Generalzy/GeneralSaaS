from celery_task.celerys import app
from celery.result import AsyncResult


@app.task
def func(x, y):
    return x + y



