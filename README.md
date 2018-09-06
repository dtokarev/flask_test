# Flask Boilerplate

Flask boilerplate app

- docker based
- microservice oriented

### TODO:
- Gunicorn
- ansible deployment 
- docker entrypoint


## Using Docker
- Run `docker-compose -f docker-compose-dev.yml up -d --build`
- Run tests `docker-compose -f docker-compose-dev.yml run users python manage.py test`
- Open `http://localhost:5001` in your browser

## Production
- Use Gunicorn `gunicorn wsgi:app --bind 0.0.0.0:$PORT --reload`
