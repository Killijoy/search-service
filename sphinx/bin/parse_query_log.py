#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
import os
import re
import redis
import codecs

stats_key = os.getenv('STATS_KEY', 'queries')
line_tpl = re.compile(r'.*\s(?P<rows>\d+)\s.*\[posts\]\s?(?P<kw>[\w\s]*)', re.I | re.S | re.U)
query_log_path = os.path.join(os.getenv('SPHINX_LOG_DIR', '/var/log/sphinxsearch'),
                              'query.log')


def parse():
    """
    Парсит Sphinx query-log и сохраняет статистику запросов в Redis

    :return: None
    """
    redis_conn = redis.from_url(os.getenv('REDIS_URL'))
    if redis_conn.zcard(stats_key) > 0:
        return

    if os.path.isfile(query_log_path):
        for line in codecs.open(query_log_path, 'r', encoding='utf-8'):
            try:
                _d = line_tpl.match(line).groupdict()
                keyword = _d.get('kw', '').strip()
                rows = int(_d.get('rows', 0))
                if keyword and rows > 1:
                    redis_conn.zincrby(stats_key, keyword.lower())
            except (AttributeError, IndexError):
                pass


if __name__ == '__main__':
    parse()
