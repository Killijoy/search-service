# TODO: собрать свой образ
FROM stefobark/sphinxdocker:latest

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y python-pip

RUN pip install redis

COPY bin /opt/bin
COPY sphinx.conf.tpl /opt/sphinx.conf.tpl

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
RUN apt-get autoclean && \
    apt-get --purge -y autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
