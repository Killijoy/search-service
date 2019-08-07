import time

import redis
import pymysql
import requests

from api.query import Query
from settings import (SPHINX_DB, STATS_KEY,
                      REDIS_URL, BUS_DOMAIN)

# TODO: надо обобщить хэлсчек и вынести в отдельную библиотеку

UP = 0
WARNING = 1
PROBLEM = 2
DOWN = 3
DISABLED = 4
UNKNOWN = 5
STATUSES = {
    UP: 'UP',
    WARNING: 'WARNING',
    PROBLEM: 'PROBLEM',
    DOWN: 'DOWN',
    DISABLED: 'DISABLED',
    UNKNOWN: 'UNKNOWN'
}


def safe_to_int(val):
    try:
        return int(val)
    except ValueError:
        return val


class HealthcheckHandler:
    """
    Обработчик запроса хэлсчека
    """
    def on_get(self, req, resp):
        sphinx_resp = self._check_sphinx()
        redis_resp = self._check_redis()
        bus_resp = self._check_bus()

        status_code = max(sphinx_resp['status'], redis_resp['status'], bus_resp['status'])
        sphinx_resp['status'] = STATUSES[sphinx_resp['status']]
        redis_resp['status'] = STATUSES[redis_resp['status']]
        bus_resp['status'] = STATUSES[bus_resp['status']]
        resp.media = {
            'status': STATUSES[status_code],
            'index': sphinx_resp,
            'db': redis_resp,
            'bus': bus_resp
        }
    
    @staticmethod
    def _check_sphinx():
        """
        Проверяем статус Sphinx.

        Значение статуса - худший показатель метрики (пинг, последнее добавление)
        """
        try:
            metrics = []

            sphinx_conn = pymysql.connect(
                host=SPHINX_DB.get('host'),
                port=SPHINX_DB.get('port'),
                db=SPHINX_DB.get('db'),
                user=SPHINX_DB.get('user'),
                passwd=SPHINX_DB.get('password'),
            )

            # время ответа
            start = time.time()
            sphinx_conn.ping()
            ping = time.time() - start
            if ping < 1:
                metrics.append(UP)
            elif 1 < ping < 2:
                metrics.append(WARNING)
            elif ping > 2:
                metrics.append(PROBLEM)
            else:
                metrics.append(UNKNOWN)

            # данные об индексах
            meta = {}
            docs_count = 0
            for index in ('main', 'delta'):
                with sphinx_conn.cursor() as cursor:
                    cursor.execute(f'SHOW INDEX {index} STATUS')

                meta[index] = {k: safe_to_int(v) for k, v in cursor.fetchall()}
                docs_count += meta[index].get('indexed_documents', 0)

            if docs_count == 0:
                metrics.append(WARNING)

            if sphinx_conn.open:
                sphinx_conn.close()

            return {
                'status': max(metrics),
                'details': {
                    'ping': ping,
                    'meta': meta
                }
            }
        except Exception as err:
            return {
                'status': DOWN,
                'details': '; '.join(map(str, err.args))
            }
    
    @staticmethod
    def _check_redis():
        """
        Проверяем статус Redis.
        """
        try:
            metrics = []
            redis_conn = redis.from_url(REDIS_URL)

            start = time.time()
            redis_conn.ping()
            ping = time.time() - start
            metrics.append(min(int(ping), PROBLEM))

            meta_keys = {'uptime_in_seconds', 'used_memory_peak_human',
                         'connected_clients', 'blocked_clients',
                         'loading', }
            return {
                'status': max(metrics),
                'details': {
                    'ping': ping,
                    'stats_count': redis_conn.zcard(STATS_KEY),
                    'cache_count': len(redis_conn.keys(f'{Query.cache_key_prefix}:*')),
                    'meta': {k: v for k, v in redis_conn.info().items() if k in meta_keys}
                }
            }
        except (ConnectionError, TimeoutError) as err:
            return {
                'status': DOWN,
                'details': '; '.join(map(str, err.args))
            }

    @staticmethod
    def _check_bus():
        """
        Проверка статуса Post Bus
        """
        try:
            metrics = []

            start = time.time()
            resp = requests.get(f'https://{BUS_DOMAIN}/api/v4/bus/_health/')
            ping = time.time() - start
            metrics.append(min(int(ping), WARNING))

            meta = resp.json()
            _mem = meta['used_memory_peak_human'].upper()

            if _mem.endswith('G'):
                metrics.append(UP)
            elif _mem.endswith('M'):
                metrics.append(WARNING)
            elif _mem.endswith('K'):
                metrics.append(PROBLEM)
            else:
                metrics.append(UNKNOWN)

            return {
                'status': max(metrics),
                'details': {
                    'ping': ping,
                    'meta': meta
                }
            }
        except (requests.RequestException, ValueError, KeyError) as err:
            return {
                'status': DOWN,
                'details': err.args[0]
            }
