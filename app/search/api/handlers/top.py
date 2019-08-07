import redis
from falcon.errors import (HTTPNotFound, HTTPServiceUnavailable)

from settings import REDIS_URL


class TopHandler:
    """
    Обработчик запроса статистики
    """
    def on_get(self, req, resp):
        count = req.get_param_as_int('count', min=1) or 100

        try:
            redis_conn = redis.from_url(REDIS_URL)
            result = redis_conn.zrange('queries', 0, count - 1, desc=True, withscores=True)
        except redis.RedisError:
            raise HTTPServiceUnavailable('Stats is unavailable.')

        if result:
            resp.media = {
                'count': len(result),
                'queries': [dict(zip(('query', 'count'), x)) for x in result]
            }
        else:
            raise HTTPNotFound(description='There were no requests to the service.')
