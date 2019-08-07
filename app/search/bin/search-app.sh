#!/usr/bin/env bash

cd /opt/app

gunicorn wsgi:app --workers=4 \
                  --bind=0.0.0.0:8000 \
                  --worker-class=meinheld.gmeinheld.MeinheldWorker \
                  --reload \
                  --access-logfile - \
                  --capture-output