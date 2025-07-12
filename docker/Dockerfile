FROM golang:1.24 AS awg

RUN git clone https://github.com/WGDashboard/amneziawg-go /awg
WORKDIR /awg
RUN go mod download && \
    go mod verify && \
    go build -ldflags '-linkmode external -extldflags "-fno-PIC -static"' -v -o /usr/bin

FROM alpine:latest
LABEL maintainer="dselen@nerthus.nl"

RUN apk update && apk add \
    iproute2 iptables bash curl wget unzip procps sudo \
    tzdata wireguard-tools python3 py3-psutil py3-bcrypt openresolv \
  && cd /usr/bin/ \
  && git clone https://github.com/WGDashboard/amneziawg-tools \
  && cd amneziawg-tools \
  && cd src \
  && make \
  && make install \
  && chmod +x /usr/bin/awg /usr/bin/awg-quick \
  && cd .. && cd .. \
  && rm -R amneziawg-tools

COPY --from=awg /usr/bin/amneziawg-go /usr/bin/amneziawg-go

# Declaring environment variables, change Peernet to an address you like, standard is a 24 bit subnet.
ARG wg_net="10.0.0.1" \
    wg_port="51820"

# Following ENV variables are changable on container runtime because /entrypoint.sh handles that. See compose.yaml for more info.
ENV TZ="Europe/Amsterdam" \
    global_dns="9.9.9.9" \
    wgd_port="10086" \
    public_ip=""

# Using WGDASH -- like wg_net functionally as a ARG command. But it is needed in entrypoint.sh so it needs to be exported as environment variable.
ENV WGDASH=/opt/wgdashboard

# Doing WireGuard Dashboard installation measures. Modify the git clone command to get the preferred version, with a specific branch for example.
RUN mkdir /data \
  && mkdir /configs \
  && mkdir -p ${WGDASH}/src \
  && mkdir -p /etc/amnezia/amneziawg
COPY ./src ${WGDASH}/src

# Generate basic WireGuard interface. Echoing the WireGuard interface config for readability, adjust if you want it for efficiency.
# Also setting the pipefail option, verbose: https://github.com/hadolint/hadolint/wiki/DL4006.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN out_adapt=$(ip -o -4 route show to default | awk '{print $NF}') \
  && echo -e "[Interface]\n\
Address = ${wg_net}/24\n\
PrivateKey =\n\
PostUp = iptables -t nat -I POSTROUTING 1 -s ${wg_net}/24 -o ${out_adapt} -j MASQUERADE\n\
PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP\n\
PreDown = iptables -t nat -D POSTROUTING -s ${wg_net}/24 -o ${out_adapt} -j MASQUERADE\n\
PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP\n\
ListenPort = ${wg_port}\n\
SaveConfig = true\n\
DNS = ${global_dns}" > /configs/wg0.conf.template \
  && chmod 600 /configs/wg0.conf.template

# Defining a way for Docker to check the health of the container. In this case: checking the gunicorn process.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD sh -c 'pgrep gunicorn > /dev/null && pgrep tail > /dev/null' || exit 1

# Copy the basic entrypoint.sh script.
COPY ./docker/entrypoint.sh /entrypoint.sh

# Exposing the default WireGuard Dashboard port for web access.
EXPOSE 10086
WORKDIR $WGDASH

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
