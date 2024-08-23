# Pull from small Debian stable image.
FROM alpine:latest
LABEL maintainer="dselen@nerthus.nl"
ENV PYTHONPATH="/usr/bin/python"

WORKDIR /home/app 
RUN    apk update && \
    apk add --no-cache py3-bcrypt py3-psutil && \
    apk add --no-cache wireguard-tools && \
    apk add --no-cache net-tools iproute2 iptables ip6tables  && \
    apk add --no-cache inotify-tools procps openresolv  && \
    mkdir /home/app/master-key 
    
COPY ./src /home/app
COPY ./docker/wgd.sh /home/app/
COPY ./docker/requirements.txt /home/app/

RUN   chmod u+x /home/app/entrypoint.sh 


# Defining a way for Docker to check the health of the container. In this case: checking the login URL.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:10086/signin || exit 1

ENTRYPOINT ["/home/app/entrypoint.sh"]