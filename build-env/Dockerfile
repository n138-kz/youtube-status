FROM python:3.10

COPY .env /tmp/
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["/usr/bin/python3", "/tmp/youtube-status-bot.py"]
