# Pull from small Debian stable image.
FROM debian:stable-slim
LABEL maintainer="dselen@nerthus.nl"

# Copy the basic entrypoint.sh script.
COPY entrypoint.sh /entrypoint.sh

# Declaring environment variables, change Peernet to an address you like, standard is a 24 bit subnet.
ENV tz=Europe/Amsterdam
ENV public_ip=0.0.0.0
ENV wg_net=10.0.0.1
ENV global_dns=1.1.1.1

# Doing basic system maintenance. Change the timezone to the desired timezone.
RUN ln -sf /usr/share/zoneinfo/${tz} /etc/localtime \
  && apt-get update \
  && apt-get upgrade -y \
  && apt-get purge linux-image* -y \
  && apt-get autoremove -y
# Removing the linux-image package to preserve space on the container.

# Installing needed packages for installation.
RUN apt-get install -y --no-install-recommends git wireguard wireguard-tools python3 python3-pip python3-venv iproute2 openresolv procps iptables curl iputils-ping traceroute

ENV WGDASH=/opt/wireguardashboard
RUN python3 -m venv ${WGDASH}/venv

# Doing WireGuard Dashboard installation measures.
RUN . ${WGDASH}/venv/bin/activate \
  && git clone -b v3.0.6.2 https://github.com/donaldzou/WGDashboard.git ${WGDASH}/app \
  && pip3 install -r ${WGDASH}/app/src/requirements.txt \
  && chmod +x ${WGDASH}/app/src/wgd.sh \
  && .${WGDASH}/app/src/wgd.sh install

# Set the volume to be used for persistency.
VOLUME /etc/wireguard

# Generate basic WireGuard interface. Echoing the WireGuard interface config for readability, adjust if you want it for efficiency.
RUN wg genkey | tee /etc/wireguard/wg0_privatekey \
  && echo "[Interface]" > /etc/wireguard/wg0.conf \
  && echo "SaveConfig = true" >> /etc/wireguard/wg0.conf \
  && echo "Address = ${wg_net}/24" >> /etc/wireguard/wg0.conf \
  && echo "PrivateKey = $(cat /etc/wireguard/wg0_privatekey)" >> /etc/wireguard/wg0.conf \
  && echo "PostUp = iptables -t nat -I POSTROUTING 1 -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /etc/wireguard/wg0.conf \
  && echo "PreDown = iptables -t nat -D POSTROUTING -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /etc/wireguard/wg0.conf \
  && echo "ListenPort = 51820" >> /etc/wireguard/wg0.conf \
  && echo "DNS = ${global_dns}" >> /etc/wireguard/wg0.conf \
  && rm /etc/wireguard/wg0_privatekey

# Exposing the default WireGuard Dashboard port for web access.
EXPOSE 10086
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]