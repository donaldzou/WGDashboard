# Pull from small Debian stable image.
FROM alpine:latest
LABEL maintainer="dselen@nerthus.nl"
ENV PYTHONPATH="/usr/bin/python"

WORKDIR /opt/wireguarddashboard/src
RUN    apk update && \
    apk add --no-cache py3-bcrypt py3-psutil && \
    apk add --no-cache wireguard-tools && \
    apk add --no-cache net-tools iproute2 iptables ip6tables  && \
    apk add --no-cache inotify-tools procps openresolv  && \
    mkdir /opt/wireguarddashboard/src/master-key 
    
COPY ./src /opt/wireguarddashboard/src/
COPY ./docker/wgd.sh /opt/wireguarddashboard/src/
COPY ./docker/requirements.txt /opt/wireguarddashboard/src/

RUN   chmod u+x /opt/wireguarddashboard/src/entrypoint.sh 


# Defining a way for Docker to check the health of the container. In this case: checking the login URL.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:10086/signin || exit 1

ENTRYPOINT ["/opt/wireguarddashboard/src/entrypoint.sh"]