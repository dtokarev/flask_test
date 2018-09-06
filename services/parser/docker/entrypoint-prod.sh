#!/bin/bash

echo "RUNNING MIGRATIONS"
python manage.py db upgrade

service supervisor start

echo "STARTING FLASK"
gunicorn -b 0.0.0.0:5001 manage:app