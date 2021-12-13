from celery_task.web_task import func
from celery.result import AsyncResult
from celery_task.celerys import app

if __name__ == '__main__':
    res = func.delay(2, 3)

    async_res = AsyncResult(id=str(res), app=app)
    if async_res.successful():
        print(async_res.get())
    else:
        print('正在执行或执行错误')