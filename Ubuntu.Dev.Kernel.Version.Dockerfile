FROM ubuntu:jammy
WORKDIR /WGDashboard
ENV TZ=UTC
EXPOSE 10086
COPY ./src /WGDashboard/

RUN cp -f /etc/apt/sources.list /etc/apt/sources.list.backup && \
    sed "s/# deb-src/deb-src/" /etc/apt/sources.list.backup > /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install wireguard sudo python3 python3-venv python3-pip net-tools -y && \
    apt install iproute2 -y && \
    apt install -y software-properties-common python3-launchpadlib gnupg2  && add-apt-repository ppa:amnezia/ppa -y && \
    sudo apt-get install -y amneziawg && \
    mkdir -p /etc/amnezia/amneziawg

# Copy AmneziaWG binaries
COPY entrypoint.sh /WGDashboard/entrypoint.sh

# Install necessary tools and libraries in the final image
RUN chmod +x /WGDashboard/wgd.sh && chmod +x /WGDashboard/entrypoint.sh

RUN if [ ! -c /dev/net/tun ]; then \
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200; \
fi


RUN ./wgd.sh install
# Start the script and keep it alive by tailing the logs
CMD ["/bin/bash", "-c", "/WGDashboard/wgd.sh start && tail -f /dev/null"]