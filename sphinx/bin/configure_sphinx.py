#!/usr/bin/env python
from os import getenv
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def get_mysql_connection_params(host='127.0.0.1', port=3306, user='', password='', db='test'):
    config = {
        'sql_host': getenv('MYSQL_HOST', host),
        'sql_port': int(getenv('MYSQL_PORT', port)),
        'sql_user': getenv('MYSQL_USER', user),
        'sql_pass': getenv('MYSQL_PASSWORD', password),
        'sql_db': getenv('MYSQL_DB', db)
    }

    db_url = getenv('MYSQL_URL')
    if db_url:
        db_url = urlparse.urlparse(db_url)

        if db_url.scheme != 'mysql':
            raise RuntimeError('Wrong scheme for mysql url: %s' % db_url.geturl())

        config['sql_host'] = db_url.host or host
        config['sql_port'] = int(db_url.port) if db_url.port else port
        config['sql_user'] = db_url.username or user
        config['sql_pass'] = db_url.password or password
        config['sql_db'] = db_url.path.strip('/') or db

    return config


_sphinx_config_path = getenv('SPHINX_CONFIG_PATH', '/etc/sphinxsearch/sphinxy.conf')

if __name__ == '__main__':
    try:
        print('Read config template...')
        with open('/opt/sphinx.conf.tpl', 'r') as ftpl:
            tpl = ftpl.read()
    except Exception as e:
        print('Fail!')
        print('Error: %s' % e)
        exit(1)

    try:
        _sphinx_config = get_mysql_connection_params()
        _sphinx_config['log_dir'] = getenv('SPHINX_LOG_DIR', '/var/log/sphinxsearch')

        print('Write config to: %s' % _sphinx_config_path)
        with open(_sphinx_config_path, 'w') as fcfg:
            fcfg.write(tpl % _sphinx_config)
    except Exception as e:
        print('Fail!')
        print('Error: %s' % e)
        exit(1)
    else:
        print('Done!')
