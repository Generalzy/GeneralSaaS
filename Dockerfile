FROM python:3.11

# 实时输出信息而非缓存
ENV PYTHONUNBUFFERED 1
# 工作目录设置为/code
WORKDIR /code

COPY . /code/
COPY requirements.txt /code/

# 安装依赖包和uwsgi
RUN pip install -r requirements.txt
RUN pip install uwsgi

# 收集静态文件
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uwsgi", "uwsgi.ini"]
