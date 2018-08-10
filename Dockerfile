FROM python:3.6-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/

ENV DEBIAN_FRONTEND=noninteractive \
    FLASK_APP="/app/app.py"

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get install -y default-libmysqlclient-dev \
                          python3-libtorrent \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000
CMD ["flask", "run", "-p", "8000"]