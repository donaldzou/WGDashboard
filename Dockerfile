FROM python:alpine
MAINTAINER Bengt Fredh "bengt@fredhs.net"

RUN apk update && apk upgrade -a && apk add wireguard-tools

RUN mkdir /wireguard-dashboard

ADD . /wireguard-dashboard/

RUN cd /wireguard-dashboard;pip install --no-cache-dir -r requirements.txt

RUN rm -rf /usr/include /tmp/* /var/cache/apk/*

VOLUME /etc/wireguard

EXPOSE 10086

ENV FLASK_APP dashboard.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_ENV development
ENV FLASK_DEBUG 0

WORKDIR /wireguard-dashboard/src

ENTRYPOINT [ "python3" ]
CMD [ "dashboard.py" ]

