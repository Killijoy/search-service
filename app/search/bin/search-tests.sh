#!/usr/bin/env bash

cd /app

pytest --cache-clear --cov=search ./tests
