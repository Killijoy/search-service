# coding: utf-8

from mock import patch

from app.tests import client


test_data = {
    "count": 5,
    "queries:": [
        {
            "query": "тест",
            "count": 146
        },
        {
            "query": "test",
            "count": 93
        },
        {
            "query": "Путин",
            "count": 51
        },
        {
            "query": "путин",
            "count": 25
        },
        {
            "query": "порно",
            "count": 7
        }
    ]
}


redis_mock_data = [('тест', 146.0),
 ('test', 93.0),
 ('Путин', 51.0),
 ('путин', 25.0),
 ('порно', 7.0)]


def set(key, val):
    test_data[key] = val


def get(key):
    return test_data[key]


def test__top_queries_view__error_404():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock:
        sphinx_mock.return_value = None
        response = client().simulate_get('/top', query_string='count=test')

        assert response.status_code == 400


def test__top_queries_view__default():
    with patch('redis.StrictRedis.zrange') as redis_get_mock,\
            patch('search.api.sphinx.Sphinx.search') as sphinx_mock:
        redis_get_mock.return_value = redis_mock_data
        sphinx_mock.return_value = test_data
        response = client().simulate_get('/top', query_string='count=5')

        assert response.status_code == 200
        assert response.json == test_data
