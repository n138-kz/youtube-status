FROM python:3.13
WORKDIR /tmp

COPY .env /tmp/
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip

ENTRYPOINT ["python3", "/tmp/youtube-status-bot.py"]
