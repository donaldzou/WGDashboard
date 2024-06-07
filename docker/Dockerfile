# Pull from small Debian stable image.
FROM debian:stable-slim
LABEL maintainer="dselen@nerthus.nl"

# Copy the basic entrypoint.sh script.
COPY entrypoint.sh /entrypoint.sh

# Declaring environment variables, change Peernet to an address you like, standard is a 24 bit subnet.
ARG dash_ver="v3.0.6.2"
ENV wg_net="10.0.0.1"
# wg_net is used functionally as an ARG for its environment variable nature, do not change unless you know what you are doing.

# Following ENV variables are changable on container runtime because /entrypoint.sh handles that. See compose.yaml for more info.
ENV tz="Europe/Amsterdam"
ENV global_dns="1.1.1.1"
ENV enable_wg0="false"
ENV isolated_peers="true"
ENV public_ip="0.0.0.0"

# Doing basic system maintenance. Change the timezone to the desired timezone.
RUN ln -sf /usr/share/zoneinfo/${tz} /etc/localtime

# Doing package management operations, such as upgrading
RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends curl \
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
  && apt-get remove linux-image-* --autoremove -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
# Removing the Linux Image package to preserve space on the image, for this reason also deleting apt lists, to be able to install packages: run apt update.

# Using WGDASH -- like wg_net functionally as a ARG command. But it is needed in entrypoint.sh so it needs to be exported as environment variable.
ENV WGDASH=/opt/wireguardashboard
RUN python3 -m venv ${WGDASH}/venv

# Doing WireGuard Dashboard installation measures.
RUN . ${WGDASH}/venv/bin/activate \
  && git clone -b ${dash_ver} https://github.com/donaldzou/WGDashboard.git ${WGDASH}/app \
  && sed -i '/Restart=always/a\StandardOutput=file:{{APP_ROOT}}/log/log1.log\nStandardError=file:{{APP_ROOT}}/log/log2.log' ${WGDASH}/app/src/wg-dashboard.service \
  && pip3 install -r ${WGDASH}/app/src/requirements.txt \
  && chmod +x ${WGDASH}/app/src/wgd.sh \
  && .${WGDASH}/app/src/wgd.sh install

# Set the volume to be used for persistency.
VOLUME /etc/wireguard

# Generate basic WireGuard interface. Echoing the WireGuard interface config for readability, adjust if you want it for efficiency.
# Also setting the pipefail option, verbose: https://github.com/hadolint/hadolint/wiki/DL4006.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wg genkey | tee /etc/wireguard/wg0_privatekey \
  && echo "[Interface]" > /etc/wireguard/wg0.conf \
  && echo "SaveConfig = true" >> /etc/wireguard/wg0.conf \
  && echo "Address = ${wg_net}/24" >> /etc/wireguard/wg0.conf \
  && echo "PrivateKey = $(cat /etc/wireguard/wg0_privatekey)" >> /etc/wireguard/wg0.conf \
  && echo "PostUp = iptables -t nat -I POSTROUTING 1 -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /etc/wireguard/wg0.conf \
  && echo "PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP" >> /etc/wireguard/wg0.conf \
  && echo "PreDown = iptables -t nat -D POSTROUTING 1" >> /etc/wireguard/wg0.conf \
  && echo "PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP" >> /etc/wireguard/wg0.conf \
  && echo "ListenPort = 51820" >> /etc/wireguard/wg0.conf \
  #&& echo "DNS = ${global_dns}" >> /etc/wireguard/wg0.conf \
  && rm /etc/wireguard/wg0_privatekey

# Defining a way for Docker to check the health of the container.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://localhost:10086/signin || exit 1

# Exposing the default WireGuard Dashboard port for web access.
EXPOSE 10086
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]