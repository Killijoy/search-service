#!/usr/bin/env bash

if [[ -f /usr/local/var/lib/sphinxsearch/posts.main.sph ]]; then
    ./searchd.sh
else
    ./indexandsearch.sh
fi