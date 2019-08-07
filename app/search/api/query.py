import logging
from math import ceil
from itertools import chain
from hashlib import sha256

import ujson
import redis
import requests
from pymysql import MySQLError
from requests.exceptions import RequestException

from settings import (SPHINX_DB, SPHINX_MAX_MATCHES,
                      REDIS_URL, STATS_KEY, CACHE_TTL)
from api.sphinx import Sphinx


logger = logging.getLogger('search.app')


class QueryError(Exception):
    pass


class Query:
    """
    Класс, инкапсулирущий поиск и вывод результатов поиска
    """

    cache_key_prefix = 'search'

    def __init__(self, key_phrase, region=None, feed=None, category=None, highlight=None):
        self.__sphinx = Sphinx(SPHINX_DB, key_phrase,
                               region=region, category_id=category, feed_id=feed)
        self.__redis = redis.from_url(REDIS_URL)

        key_hash = sha256(f"{self.key_phrase}{region}{feed}{category}{highlight}".encode())
        self.cache_key = f"{Query.cache_key_prefix}:{key_hash.hexdigest()}"

        self.highlight_class = highlight

    @property
    def key_phrase(self):
        """
        Нормализованная поисковая фраза
        """
        return self.__sphinx.key_phrase

    def get(self, page, size):
        """
        Получение запрошенной страницы результатов поиска и увеличение счетчика запросов.

        :param int page: номер страницы
        :param int size: размер страницы
        :return: объект страницы
        :rtype: dict
        """
        if not self.__redis.exists(self.cache_key):
            # надо положить результаты поиска в redis
            self.search_posts()

        try:
            # вернуть из redis требуемую страницу
            count = self.__redis.zcard(self.cache_key)
            if not count:
                raise QueryError(f'Post for query "{self.key_phrase}" not found.')

            last_page = int(ceil(float(count) / size)) or 1
            assert page <= last_page, 'Page number out of range.'

            start_idx = (page - 1) * size

            return {
                'count': count,
                'next': page + 1 if page < last_page else None,
                'previous': page - 1 or None,
                'last': last_page,
                'size': size,
                'results': tuple(map(ujson.loads,
                                     self.__redis.zrevrange(self.cache_key, start_idx, start_idx + size - 1)))
            }
        finally:
            if page == 1:
                # увеличить статистику ключевой фразы
                self.inc_stats()

    def replace_highlight_snippets(self, post):
        """
        Заменяет заголовок и контент поста (если он есть) сниппетами с подсветкой совпадений

        :param dict post: словарь с данными поста
        :return: словарь с данными поста
        :rtype: dict
        """
        try:
            texts = post['title'], post.get('content', '')
            hl_results = tuple(self.__sphinx.highlight_snippets(texts, self.highlight_class))

            if len(hl_results) == 2:
                post['title'], post['content'] = hl_results
            else:
                post['title'] = hl_results[0]

            return post

        except MySQLError as err:
            logger.error(err)

    def inc_stats(self):
        """
        Увеличение счетчика количества запросов ключевой фразы
        :return: None
        """
        try:
            self.__redis.zincrby(STATS_KEY, self.key_phrase)
        except redis.RedisError as err:
            logger.error(err)

    def search_posts(self):
        """
        Поиск постов в индексе, получение данных из автобуса и подсветка совпадений.
        Результаты складываются в redis&

        :return: None
        """
        pids = list(self.__sphinx.search_ids(limit=SPHINX_MAX_MATCHES))
        pids_to_request = []

        while pids:
            pids_to_request.append(pids.pop())

            # получаем объекты постов из автобуса пачками по 20
            if len(pids_to_request) == 20 or not pids:
                posts = list(self.bus_posts_highlight(pids_to_request))

                if posts:
                    try:
                        self.__redis.zadd(self.cache_key, *chain.from_iterable(posts))
                    except redis.RedisError as err:
                        logger.error(err)

                pids_to_request = []

        try:
            # установим TTL для результатов поиска
            if self.__redis.exists(self.cache_key):
                self.__redis.expire(self.cache_key, CACHE_TTL)
        except redis.RedisError as err:
            logger.error(err)

    def bus_posts_highlight(self, pids):
        """
        Скачивание постов из автобуса и выделение совпадений в тексте

        :param list pids: список id постов
        :return: генератор объектов постов с подсвеченными совпадениями
        """
        try:
            bus_resp = requests.get('https://www.test.com/api/v4/posts/?ids=%s' %
                                    ','.join(map(str, pids)))
            if bus_resp.status_code < 400:
                for post in bus_resp.json():
                    post = self.replace_highlight_snippets(post)
                    if post is not None:
                        #
                        yield ujson.dumps(post), post['ts']
            else:
                logger.error(f'Post bus bad status code: {bus_resp.status_code} {bus_resp.reason}')

        except RequestException as err:
            logger.error(err)
