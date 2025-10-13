#!/bin/bash
flask preprocess wait-for-db
flask preprocess wait-for-es
flask translate compile
flask db upgrade
exec gunicorn -b :5000 -w 4 --threads 8 -k gthread --access-logfile - --error-logfile - src.blog:app
