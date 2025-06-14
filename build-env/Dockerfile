FROM python:3.10

COPY requirements.txt /tmp/
RUN if [ -f requirements.txt ]; then pip install -r /tmp/requirements.txt; fi

RUN set -x && mkdir /tmp/.secret
COPY .secret/config.json /tmp/.secret/
