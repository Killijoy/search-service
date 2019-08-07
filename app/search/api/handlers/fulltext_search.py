import logging

from falcon.errors import (HTTPBadRequest, HTTPNotFound,
                           HTTPServiceUnavailable)
from pymysql import MySQLError
from redis import RedisError

from api.query import Query, QueryError
from settings import REGIONS


logger = logging.getLogger('search.app')


class SearchHandler:
    """
    Обработчик поискового запроса
    """
    def on_get(self, req, resp):
        # query params
        key_phrase = req.get_param('q', required=True)

        region = req.get_param('region')
        if region and region not in REGIONS:
            raise HTTPBadRequest(description=f'Region "{region}" not supported. '
                                             f'Available regions: {", ".join(REGIONS)}.')
        cid = req.get_param_as_int('category', min=1)
        fid = req.get_param_as_int('feed', min=1)

        highlight_class = req.get_param('highlight')

        # page params
        page_num = req.get_param_as_int('page', min=1) or 1
        page_size = req.get_param_as_int('size', min=1) or 20

        try:
            query = Query(key_phrase, region=region, feed=fid, category=cid,
                          highlight=highlight_class)

            resp.media = query.get(page_num, page_size)

        except AssertionError as err:
            raise HTTPBadRequest(description=str(err))

        except QueryError as err:
            raise HTTPNotFound(description=str(err))

        except (MySQLError, RedisError) as err:
            logger.error(err, exc_info=True)
            raise HTTPServiceUnavailable(description='Service component is unavailable.')
