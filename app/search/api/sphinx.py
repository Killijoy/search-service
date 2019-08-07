import re
import pymysql


class Sphinx:
    """
    Враппер для Sphinx Search Engine по протоколу Mysql
    """
    min_word_len = 3

    def __init__(self, sphinx_db, key_phrase, region=None, category_id=None, feed_id=None):
        self.connection = pymysql.connect(
            host=sphinx_db.get('host', '127.0.0.1'),
            port=sphinx_db.get('port', 9306),
            db=sphinx_db.get('db'),
            user=sphinx_db.get('user'),
            passwd=sphinx_db.get('password'),
            connect_timeout=sphinx_db.get('timeout', 30),
            charset='utf8'
        )
        self.max_matches = sphinx_db.get('max_matches', 1000)

        self.key_phrase = self.normalize(key_phrase)

        assert self.key_phrase, f'Key phrase "{key_phrase}" is empty after normalization.'
        assert len(self.key_phrase) >= self.min_word_len, f'Normalized key phrase "{self.key_phrase}" is to short. ' \
                                                          f'Requires at least {self.min_word_len} characters.'

        self.region = region
        self.category_id = category_id
        self.feed_id = feed_id

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.open:
            self.connection.close()

    @staticmethod
    def normalize(key_phrase):
        """
        Очистка ключевой фразы от мусора (остаются только буквы и пробелы)

        :param str key_phrase: строка запроса
        :return: очищенная строка запроса
        :rtype: str
        """
        key_phrase = re.sub(r'\s+', ' ', key_phrase, re.U)
        return ''.join(re.findall(r'[\w\s-]+', key_phrase, re.U)).lower()

    @staticmethod
    def clean_html(raw_html):
        """
        Очистка такста от html-тегов (для подсветки сниппетов)

        :param str raw_html: html-код
        :return: очищенный текст
        """
        return re.sub('<.*?>', '', raw_html.replace('<br>', '\n')
                                           .replace('<br />', '\n'),
                      re.U)

    def build_sphinxql(self, selection='*', order_by=None, limit=None):
        """
        Построение SphinxQL-запроса в индекс

        :param str selection: строка полей выборки
        :param str order_by: строка полей сортировки
        :param int limit: ограничение выборки
        :return: строка SphinxQl-запроса
        :rtype: str
        """
        query = f"SELECT {selection} FROM posts WHERE MATCH('{self.key_phrase}')"

        if self.category_id:
            query += f" AND category_id={self.category_id}"

        if self.region:
            query += f" AND region='{self.region}'"

        if self.feed_id:
            query += f" AND feed_id={self.feed_id}"

        if order_by:
            query += f" ORDER BY {order_by} DESC"

        if limit:
            query += f" LIMIT {limit}"

        if self.max_matches:
            query += f" OPTION max_matches={self.max_matches}"

        return query

    def index_count(self):
        """
        Количество постов в индексе по ключевой фразе

        :return: количество постов в индексе
        ":rtype: int
        """
        query = self.build_sphinxql('COUNT(*)')

        with self.connection.cursor() as cursor:
            cursor.execute(query.encode('utf-8'))

        return cursor.fetchone()[0]

    def search_ids(self, limit=None):
        """
        Список id постов, найденных по запросу. Отсортированные по дате публикации (по убыванию).
        Возвращает `limit` идентификаторов (по умолчанию 20).

        :param limit: маскимальное количество постов
        :return: генератор id постов, удовлетворяющих запросу
        :rtype: generator
        """
        query = self.build_sphinxql('id', order_by='post_date_ts', limit=limit)

        with self.connection.cursor() as cursor:
            cursor.execute(query.encode('utf-8'))

        for row in cursor.fetchall():
            yield row[0]

    def highlight_snippets(self, data, span_class=None):
        """
        Подсветка совпадений в тексте. Возвращает не весь текст, а сниппеты, разделенные многоточием,
        с выделенными html-тегами совпадениями. По умолчанию выделяет совпадения жирным текстом.

        :param data: текст или список текстов
        :param span_class: имя css-класса для подсветки
        :return: генератор строк со сниппетами
        :rtype: generator
        """

        if not isinstance(data, str):
            data = "(" + ", ".join(map(lambda x: f"'{self.clean_html(x)}'", data)) + ")"
        else:
            data = f"'{self.clean_html(data)}'"

        query = f"CALL SNIPPETS({data}, 'main', '{self.key_phrase}'"

        if span_class:
            query += f", '<span class=\"{span_class}\">' AS before_match"
            query += ", '</span>' AS after_match"

        query += ")"

        with self.connection.cursor() as cursor:
            cursor.execute(query.encode('utf-8'))

        for row in cursor.fetchall():
            yield row[0]
