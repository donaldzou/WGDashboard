# Pull from small Debian stable image.
FROM debian:stable-slim AS build
LABEL maintainer="dselen@nerthus.nl"

# Declaring environment variables, change Peernet to an address you like, standard is a 24 bit subnet.
ENV wg_net="10.0.0.1"
# wg_net is used functionally as an ARG for its environment variable nature, do not change unless you know what you are doing.

# Following ENV variables are changable on container runtime because /entrypoint.sh handles that. See compose.yaml for more info.
ENV tz="Europe/Amsterdam"
ENV global_dns="1.1.1.1"
ENV enable="none"
ENV isolate="wg0"
ENV public_ip="0.0.0.0"

# Doing basic system maintenance. Change the timezone to the desired timezone.
RUN ln -sf /usr/share/zoneinfo/${tz} /etc/localtime

# Using WGDASH -- like wg_net functionally as a ARG command. But it is needed in entrypoint.sh so it needs to be exported as environment variable.
ENV WGDASH=/opt/wireguarddashboard

# Doing package management operations, such as upgrading
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    iproute2 \
    iptables \
    iputils-ping \
    openresolv \
    procps \
    python3 \
    python3-pip \
    python3-venv \
    traceroute \
    wireguard \
    wireguard-tools \
    sudo && \
    apt-get remove -y linux-image-* && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Removing the Linux Image package to preserve space on the image, for this reason also deleting apt lists, to be able to install packages: run apt update.

# Doing WireGuard Dashboard installation measures. Modify the git clone command to get the preferred version, with a specific branch for example.
RUN git clone https://github.com/donaldzou/WGDashboard.git ${WGDASH} \
  && rm ${WGDASH}/.git -rdf \
  && python3 -m venv ${WGDASH}/src/venv \
  && . ${WGDASH}/src/venv/bin/activate \
  && chmod +x ${WGDASH}/src/wgd.sh \
  && cd ${WGDASH}/src \
  && ./wgd.sh install

# Set the volume to be used for WireGuard configuration persistency.
VOLUME /etc/wireguard
VOLUME ${WGDASH}

# Generate basic WireGuard interface. Echoing the WireGuard interface config for readability, adjust if you want it for efficiency.
# Also setting the pipefail option, verbose: https://github.com/hadolint/hadolint/wiki/DL4006.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wg genkey | tee /etc/wireguard/wg0_privatekey \
  && echo "[Interface]" > /wg0.conf \
  && echo "SaveConfig = true" >> /wg0.conf \
  && echo "Address = ${wg_net}/24" >> /wg0.conf \
  && echo "PrivateKey = $(cat /etc/wireguard/wg0_privatekey)" >> /wg0.conf \
  && echo "PostUp = iptables -t nat -I POSTROUTING 1 -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /wg0.conf \
  && echo "PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP" >> /wg0.conf \
  && echo "PreDown = iptables -t nat -D POSTROUTING -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /wg0.conf \
  && echo "PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP" >> /wg0.conf \
  && echo "ListenPort = 51820" >> /wg0.conf \
  #&& echo "DNS = ${global_dns}" >> /wg0.conf \
  && rm /etc/wireguard/wg0_privatekey

# Defining a way for Docker to check the health of the container. In this case: checking the login URL.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:10086/)" -eq "200" ] || exit 1


# Copy the basic entrypoint.sh script.
COPY entrypoint.sh /entrypoint.sh

# Exposing the default WireGuard Dashboard port for web access.
EXPOSE 10086
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]