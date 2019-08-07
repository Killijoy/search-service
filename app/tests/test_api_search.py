# coding: utf-8
import copy

from mock import patch
from app.tests import client


test_data = {'pages': {'count': 1, 'page': 1, 'size': 20},
             'posts': {'list': [{'content': ' 123 https://t.co/7c6uzO7Xuv - 23 билета '
                                                        'осталось на 21 февраля (Дилетантские чтения о '
                                                        'Махно) ',
                                            'fid': 4009,
                      'id': 62241339,
                      'link': 'http://shm.ru/visit/tickets/gim/',
                      'slug': '123-23-bileta-ostalos-na-21-fevralya-diletantskie-chteniya',
                      'title': '123 - 23 билета осталось на 21 февраля '
                               '(Дилетантские чтения...',
                      'ts': 1518502395},
                     {'content': ' Праздничный календарь с рамкой на 2018 год с '
                                 'Собакой - Пусть все мечты сбываются и счастье '
                                 'улыбается PSD | 4961x3508 | 300 dpi | 123,23 '
                                 'Mb Автор: Koaress ',
                      'fid': 84,
                      'id': 79974855,
                      'img': '//img.test.com/media/posts/images/20171109/79974855.jpg',
                      'link': 'http://deslife.ru/149009-prazdnichnyy-kalendar-s-ramkoy-na-2018-god-'
                              's-sobakoy-pust-vse-mechty-sbyvayutsya-i-schaste-ulybaetsya.html',
                      'slug': 'prazdnichnyj-kalendar-s-ramkoj-na-2018-god-s-sobakoj-pust-vse-mechty-'
                              'sbyvayutsya-i-schaste-ulybaetsya',
                      'summary': 'Праздничный календарь с рамкой на 2018 год с '
                                 'Собакой - Пусть все мечты сбываются и счастье '
                                 'улыбается\n'
                                 'PSD | 4961x3508 | 300 dpi | 123,23 Mb\n'
                                 'Автор: Koaress',
                      'title': 'Праздничный календарь с рамкой на 2018 год с '
                               'Собакой - Пусть все мечты сбываются и счастье '
                               'улыбается',
                      'ts': 1510225105},
                     {'content': ' Москва. 9 ноября. ИНТЕРФАКС - Комитет '
                                 'Госдумы по культуре в четверг по предложению '
                                 'Иосифа Кобзона поддержал поправку ко второму '
                                 'чтению проекта бюджета на 2018 и плановые '
                                 '2019-2020 гг. о выделении 123 млн рублей на '
                                 'восстановление Цугольского дацана в  ... ',
                      'fid': 10198,
                      'id': 79978419,
                      'link': 'http://realty.interfax.ru/ru/news/articles/87757',
                      'slug': 'dumskij-komitet-odobril-vydelenie-sredstv-na-vosstanovlenie-dacana-v-zabajkale',
                      'summary': 'Москва. 9 ноября. ИНТЕРФАКС - Комитет Госдумы '
                                 'по культуре в четверг по предложению Иосифа '
                                 'Кобзона поддержал поправку ко второму чтению '
                                 'проекта бюджета на 2018 и плановые 2019-2020 '
                                 'гг. о выделении 123',
                      'title': 'Думский комитет одобрил выделение средств на '
                               'восстановление дацана в Забайкалье',
                      'ts': 1510228411},
                     {'content': ' В четверг комитет Госдумы по культуре по '
                                 'предложению Иосифа Кобзона поддержал поправку '
                                 'ко второму чтению проекта бюджета на 2018 и '
                                 'плановые 2019-2020 гг о выделении 123 '
                                 'миллионов рублей для восстановления '
                                 'Цугольского дацана, передает "Интерфакс".В '
                                 'ходе  ... ',
                      'fid': 110,
                      'id': 79980120,
                      'img': '//img.test.com/media/posts/images/20171109/79980120.jpg',
                      'link': 'https://www.vesti.ru/doc.html?id=2952406',
                      'slug': 'kobzon-trebuet-postroit-buddijskij-hram-v-moskve',
                      'summary': 'В четверг комитет Госдумы по культуре по '
                                 'предложению Иосифа Кобзона поддержал поправку '
                                 'ко второму чтению проекта бюджета на 2018 и '
                                 'плановые 2019-2020 гг о выделении 123 '
                                 'миллионов рублей для',
                      'title': 'Кобзон требует построить буддийский храм в '
                               'Москве',
                      'ts': 1510229400},
                     {'content': ' Продолжаю коллекционировать гнилые отмазки '
                                 'дупел, не желающих привлекать к уголовной '
                                 'ответственности российских террористов. '
                                 'Последние несколько месяцев я решил '
                                 'ограничиться одной, но знаковой фигурой '
                                 '(Гиркин). И на этом персонаже протестировать  '
                                 '... ',
                      'fid': 322,
                      'id': 79980148,
                      'img': '//img.test.com/media/posts/images/20171109/79980148.jpg',
                      'link': 'https://politota.d3.ru/comments/1481412',
                      'mobile_link': 'https://politota.d3.ru/o-kompetentnosti-gosudarstvennykh-organov-rf-1481412/',
                      'slug': 'o-kompetentnosti-gosudarstvennyh-organov-rf',
                      'summary': 'Продолжаю коллекционировать гнилые отмазки '
                                 'дупел, не желающих привлекать к уголовной '
                                 'ответственности российских террористов. '
                                 'Последние несколько месяцев я решил '
                                 'ограничиться одной, но знаковой фигурой',
                      'title': 'О компетентности государственных органов РФ',
                      'ts': 1510229704}]}}


def test__full_text_search_view__error_no_q():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock:
        sphinx_mock.return_value = {}
        response = client().simulate_get('/search')

        assert response.status_code == 400


def test__full_text_search_view__error_no_second_page():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock:
        sphinx_mock.return_value = {}
        response = client().simulate_get('/search', query_string='q=test&page=2')

        assert response.status_code == 404


def test__full_text_search_view__error_404():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock:
        sphinx_mock.return_value = None
        response = client().simulate_get('/search', query_string='q=выфаыфаыфвафыавфыафывафывыацйу24выффавы@page=9999')
        assert response.status_code == 404


def test__full_text_search_view__default():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock,\
            patch('requests.Response') as dummy_api_mock:
        sphinx_mock.return_value = {62241339, 79974855, 79978419, 79980120, 79980148}
        dummy_api_mock.return_value = test_data
        response = client().simulate_get('/search', query_string='q=тест')

        assert response.status_code == 200
        assert response.json == test_data


def test__full_text_search_view__filter_region():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock,\
            patch('requests.Response') as dummy_api_mock:
        sphinx_mock.return_value = {62241339, 79974855, 79978419, 79980120, 79980148}
        dummy_api_mock.return_value = test_data
        response = client().simulate_get('/search', query_string='q=test&region=us')

        assert response.status_code == 200
        assert response.json == test_data


def test__full_text_search_view__filter_fid():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock, \
            patch('requests.Response') as dummy_api_mock:
        sphinx_mock.return_value = {62241339, 79974855, 79978419, 79980120, 79980148}
        dummy_api_mock.return_value = test_data
        response = client().simulate_get('/search', query_string='q=test&fid=32')

        assert response.status_code == 200
        assert response.json == test_data


def test__full_text_search_view__custom_page_size():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock,\
            patch('requests.Response') as dummy_api_mock:
        sphinx_mock.return_value = {62241339, 79974855, 79978419, 79980120, 79980148}
        dummy_api_mock.return_value = test_data
        response = client().simulate_get('/search', query_string='q=тест&size=5')
        current_test_data = copy.deepcopy(test_data)
        current_test_data['pages']['size'] = 5

        assert response.status_code == 200
        assert response.json == current_test_data


def test__full_text_search_view__paging():
    with patch('redis.StrictRedis.zincrby'), patch('search.api.sphinx.Sphinx.search') as sphinx_mock,\
            patch('requests.Response') as dummy_api_mock:
        sphinx_mock.return_value = {62241339, 79974855, 79978419, 79980120, 79980148}
        dummy_api_mock.return_value = test_data
        response = client().simulate_get('/search', query_string='q=тест&page=1')

        assert response.status_code == 200
        assert response.json == test_data
