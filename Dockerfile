FROM python:3.8

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install .

CMD [ "python", "music_dl/main.py" ]