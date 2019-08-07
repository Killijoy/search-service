import os

# sphinx
SPHINX_MAX_MATCHES = int(os.getenv('SPHINX_MAX_MATCHES', 1000)) or None
SPHINX_DB = {
    'host': os.getenv('SPHINX_HOST', '127.0.0.1'),
    'port': 9306,
    'max_matches': SPHINX_MAX_MATCHES
}


# redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
STATS_KEY = os.getenv('STATS_KEY', 'queries')
CACHE_TTL = int(os.getenv('CACHE_TTL', 60 * 5))


BUS_DOMAIN = os.getenv('BUS_DOMAIN', 'dev.test.com')
REGIONS = set(map(lambda x: x.strip(),
                  os.getenv('REGIONS', 'ru,us,ua,br,fr,se').split(',')))


# logging
SENTRY_DSN = os.getenv('SENTRY',
                       'http://0a7886c0fcda4e70b14d5c2f18b26daf:5dc98e3be6514a75904df8c44a562b1a@sentry.test.com/24')
LOG_DIR = os.getenv('LOG_DIR', '/var/log/search')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s | %(name)s | %(message)s'
        },
        'standard': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(levelname)s | %(asctime)s | %(name)s | %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s | %(asctime)s |'
                      ' %(pathname)s:%(lineno)d | %(process)d | %(thread)d | %(name)s | %(message)s'
        }
    },
    'handlers': {
        'console_simple': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        },
        'search.app': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'search-app.log'),
            'formatter': 'standard',
            'level': 'DEBUG',
            'maxBytes': 1024 * 1024 * 30,  # 30M
            'backupCount': 10
        }

    },
    'loggers': {
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console_simple'],
            'propagate': True,
            'qualname': 'gunicorn.access'
        },
        'gunicorn.error': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
            'qualname': 'gunicorn.error'
        },
        'search.app': {
            'handlers': ['search.app', 'sentry'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR'
    }
}
