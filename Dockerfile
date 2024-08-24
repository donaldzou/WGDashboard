# Pull from small Debian stable image.
FROM alpine:latest
LABEL maintainer="dselen@nerthus.nl"
ENV PYTHONPATH="/usr/lib/python3.12/site-packages"

WORKDIR /opt/wireguarddashboard/src
RUN    apk update && \
    apk add --no-cache sudo gcc musl-dev linux-headers && \
    apk add --no-cache wireguard-tools && \
    apk add --no-cache  iptables ip6tables && \
    mkdir /opt/wireguarddashboard/src/master-key 
    

COPY ./src /opt/wireguarddashboard/src/
COPY ./docker/alpine/entrypoint.sh /opt/wireguarddashboard/src/
#COPY ./docker/alpine/wgd.sh /opt/wireguarddashboard/src/
#COPY ./docker/alpine/requirements.txt /opt/wireguarddashboard/src/

RUN   chmod u+x /opt/wireguarddashboard/src/entrypoint.sh 


# Defining a way for Docker to check the health of the container. In this case: checking the login URL.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:10086/signin || exit 1

ENTRYPOINT ["/opt/wireguarddashboard/src/entrypoint.sh"]