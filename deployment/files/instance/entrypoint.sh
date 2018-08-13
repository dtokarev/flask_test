#!/bin/bash
flask db upgrade &&
/etc/init.d/supervisor start &&
flask run -p 8000