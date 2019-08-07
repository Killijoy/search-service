# coding: utf-8

from app import Sphinx
from app import SPHINX_DB

test_data = ['Путин', 'Водка', 'Медведев', 'новости', 'Утро', 'тест']


def test__clean_query():
    assert Sphinx.normalize('Test') == 'Test'
    assert Sphinx.normalize('Test 123') == 'Test 123'
    assert Sphinx.normalize('тест@#$') == 'тест'
    assert Sphinx.normalize('Test_test') == 'Test_test'
    assert Sphinx.normalize('test.') == 'test'


def test__index_count():
    for test_case in test_data:
        assert Sphinx(**SPHINX_DB).index_count(test_case) is not None


def test__search():
    for test_case in test_data:
        assert Sphinx(**SPHINX_DB).search_ids(test_case) is not None
