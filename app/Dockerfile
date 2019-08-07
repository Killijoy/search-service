FROM python:3.6-slim

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y gcc

COPY requirements.txt /opt/app/requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r /opt/app/requirements.txt

COPY search /opt/app

ENV LANG "C.UTF-8"
ENV PYTHONPATH "/opt/app:${PYTHONPATH}"

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
RUN apt-get autoclean && \
    apt-get --purge -y autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/app