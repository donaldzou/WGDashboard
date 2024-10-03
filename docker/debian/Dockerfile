# Pull from small Debian stable image.
FROM debian:stable-slim AS build
LABEL maintainer="dselen@nerthus.nl"

# Declaring environment variables, change Peernet to an address you like, standard is a 24 bit subnet.
ARG Git_Url="https://github.com/donaldzou/WGDashboard.git"
ARG wg_net="10.0.0.1"
ARG wg_port="51820"

# Following ENV variables are changable on container runtime because /entrypoint.sh handles that. See compose.yaml for more info.
ENV TZ="Europe/Amsterdam"
ENV global_dns="1.1.1.1"
ENV enable="none"
ENV isolate="wg0"
ENV public_ip="0.0.0.0"
ENV update="yes"

# Doing basic system maintenance. Change the timezone to the desired timezone.
RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime

# Using WGDASH -- like wg_net functionally as a ARG command. But it is needed in entrypoint.sh so it needs to be exported as environment variable.
ENV WGDASH=/opt/wireguarddashboard

# Doing package management operations, such as upgrading
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git \
    iptables python3 \
    wireguard wireguard-tools \
    sudo && \
    apt-get remove -y linux-image-* && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Removing the Linux Image package to preserve space on the image, for this reason also deleting apt lists, to be able to install packages: run apt update.

# Doing WireGuard Dashboard installation measures. Modify the git clone command to get the preferred version, with a specific branch for example.
RUN mkdir -p /setup/conf && mkdir /setup/app && mkdir ${WGDASH} \
  && git clone ${Git_Url} /setup/app

# Set the volume to be used for WireGuard configuration persistency.
VOLUME /etc/wireguard
VOLUME ${WGDASH}

# Generate basic WireGuard interface. Echoing the WireGuard interface config for readability, adjust if you want it for efficiency.
# Also setting the pipefail option, verbose: https://github.com/hadolint/hadolint/wiki/DL4006.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo "[Interface]" > /setup/conf/wg0.conf \
  && echo "Address = ${wg_net}/24" >> /setup/conf/wg0.conf \
  && echo "PrivateKey ="  >> /setup/conf/wg0.conf \
  && echo "PostUp = iptables -t nat -I POSTROUTING 1 -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /setup/conf/wg0.conf \
  && echo "PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP" >> /setup/conf/wg0.conf \
  && echo "PreDown = iptables -t nat -D POSTROUTING -s ${wg_net}/24 -o $(ip -o -4 route show to default | awk '{print $NF}') -j MASQUERADE" >> /setup/conf/wg0.conf \
  && echo "PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP" >> /setup/conf/wg0.conf \
  && echo "ListenPort = ${wg_port}" >> /setup/conf/wg0.conf \
  && echo "SaveConfig = true" >> /setup/conf/wg0.conf \
  && echo "DNS = ${global_dns}" >> /setup/conf/wg0.conf

# Defining a way for Docker to check the health of the container. In this case: checking the login URL.
HEALTHCHECK --interval=2m --timeout=1m --start-period=20s --retries=3 \
  CMD [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:10086/)" -eq "200" ] || exit 1


# Copy the basic entrypoint.sh script.
COPY entrypoint.sh /entrypoint.sh

# Exposing the default WireGuard Dashboard port for web access.
EXPOSE 10086
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]