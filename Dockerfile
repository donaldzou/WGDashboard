# Pull from small secure alpine image.
FROM alpine:latest AS builder

LABEL maintainer="dselen@nerthus.nl"
LABEL engineer="NOXCIS"

WORKDIR /opt/wireguarddashboard/src

RUN    apk update && \
    apk add --no-cache sudo gcc musl-dev rust cargo linux-headers 

COPY ./docker/alpine/builder.sh /opt/wireguarddashboard/src/
COPY ./docker/alpine/builder_requirements.txt /opt/wireguarddashboard/src/
RUN   chmod u+x /opt/wireguarddashboard/src/builder.sh
RUN  /opt/wireguarddashboard/src/builder.sh



FROM alpine:latest
WORKDIR /opt/wireguarddashboard/src

COPY ./src /opt/wireguarddashboard/src/
COPY --from=builder /opt/wireguarddashboard/src/venv /opt/wireguarddashboard/src/venv
COPY --from=builder /opt/wireguarddashboard/src/log /opt/wireguarddashboard/src/log/

RUN    apk update && \
    apk add --no-cache wireguard-tools sudo && \
    apk add --no-cache  iptables ip6tables && \
    chmod u+x /opt/wireguarddashboard/src/entrypoint.sh 

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD sh -c 'pgrep gunicorn > /dev/null && pgrep tail > /dev/null' || exit 1

ENTRYPOINT ["/opt/wireguarddashboard/src/entrypoint.sh"]


CMD ["docker_start"]

# Define the stop signal to be used by Docker
STOPSIGNAL SIGTERM