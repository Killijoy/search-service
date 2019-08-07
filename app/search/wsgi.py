import logging.config

from falcon import (API, MEDIA_JSON,
                    HTTPNotFound)

import version
from settings import LOGGING
from api.handlers.fulltext_search import SearchHandler
from api.handlers.top import TopHandler
from api.handlers.health_check import HealthcheckHandler


__all__ = ('app',)


logging.config.dictConfig(LOGGING)


_ROOT = '/'
_SEARCH = _ROOT + 'search'
_TOP = _ROOT + 'top'
_HEALTH = _ROOT + '_health'


class RootHandler:
    def on_get(self, req, resp):
        resp.media = {
            'release': version.version,
            'status': version.status,
            'routes': [_SEARCH, _TOP, _HEALTH]
        }


# ----- application
app = application = API()

app.add_route(_ROOT, RootHandler())
app.add_route(_SEARCH, SearchHandler())
app.add_route(_TOP, TopHandler())
app.add_route(_HEALTH, HealthcheckHandler())


# error info in json (default xml)
def json_error_serializer(req, resp, exception):
    """
    JSON http-error info
    """
    preferred = req.client_prefers((MEDIA_JSON,))

    if preferred is not None:
        resp.body = exception.to_json()
        resp.content_type = preferred


app.set_error_serializer(json_error_serializer)


def not_found(ex, req, resp, params):
    """
    Reraise falcon.HTTPNotFound with additional info
    """
    raise HTTPNotFound(description=ex.description or 'Route not found')


app.add_error_handler(HTTPNotFound, not_found)


