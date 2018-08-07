FROM ubuntu:16.04

RUN mkdir /app_parser
WORKDIR /app_parser
ADD . /app_parser/

ENV DEBIAN_FRONTEND=noninteractive
    FLASK_APP="/app_parser/app.py"

RUN apt update && \
    apt install -y libmysqlclient-dev python3.5 \
        python3-pip \
        python3-libtorrent \
        && \
    apt clean && \
    pip3 install --upgrade pip' && \
    pip3 install -r requirements.txt

EXPOSE 8000
CMD ["flask", "run", "p", "8000"]