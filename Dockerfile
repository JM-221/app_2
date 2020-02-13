FROM python:3.6.1-slim

ENV key1=value1
ENV key2=value2

COPY app_2 /app
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN cd /app && pip install -r requirements.txt

EXPOSE 5000

CMD python run.py
