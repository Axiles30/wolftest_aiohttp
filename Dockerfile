FROM python:3.10.0-alpine

WORKDIR /app

COPY app /app

RUN pip install -r requirements.txt

RUN pip install gunicorn

CMD ["gunicorn", "server:main", "--bind", "0:8080", "--worker-class", "aiohttp.GunicornWebWorker"]
