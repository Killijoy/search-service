#!/usr/bin/env bash

echo "SHELL=/bin/sh" | crontab -
(crontab -l && echo "*/5 * * * * indexer --merge main delta --rotate --config /etc/sphinxsearch/sphinxy.conf && indexer delta --rotate --config /etc/sphinxsearch/sphinxy.conf >> /var/log/sphinxsearch/delta-index.log") | crontab -
(crontab -l && echo "0 3 * * sun indexer --all --rotate --config /etc/sphinxsearch/sphinxy.conf >> /var/log/sphinxsearch/all-reindex.log") | crontab -

/opt/bin/configure_sphinx.py
/opt/bin/parse_query_log.py

/opt/bin/run_sphinx.sh