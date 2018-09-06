#!/bin/bash

echo "RUNNING MIGRATIONS"
python manage.py db upgrade

echo "STARTING FLASK"
python manage.py run -h 0.0.0.0