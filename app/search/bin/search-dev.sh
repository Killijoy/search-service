#!/usr/bin/env bash

cd /opt/app

gunicorn wsgi:app --workers=1 \
                  --bind=0.0.0.0:8000 \
                  --worker-class=sync \
                  --reload \
                  --access-logfile - \
                  --capture-output