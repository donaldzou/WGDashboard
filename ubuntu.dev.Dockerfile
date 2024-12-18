# Compiler: Build AmneziaWG (Obfuscated Wireguard)
FROM golang:1.23.4-bookworm@sha256:ef30001eeadd12890c7737c26f3be5b3a8479ccdcdc553b999c84879875a27ce AS compiler
WORKDIR /go


RUN apt-get update && apt-get install -y --no-install-recommends \
    git make bash build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


RUN git clone --depth=1 https://github.com/amnezia-vpn/amneziawg-tools.git && \
    git clone --depth=1 https://github.com/amnezia-vpn/amneziawg-go.git
RUN cd /go/amneziawg-tools/src && make
RUN cd /go/amneziawg-go && \
    go get -u ./... && \
    go mod tidy && \
    make && \
    chmod +x /go/amneziawg-go/amneziawg-go /go/amneziawg-tools/src/wg /go/amneziawg-tools/src/wg-quick/linux.bash
RUN echo "DONE AmneziaWG"


FROM scratch AS bins
COPY --from=compiler /go/amneziawg-go/amneziawg-go /amneziawg-go
COPY --from=compiler /go/amneziawg-tools/src/wg /awg
COPY --from=compiler /go/amneziawg-tools/src/wg-quick/linux.bash /awg-quick




FROM ubuntu:latest
WORKDIR /WGDashboard
ENV TZ=UTC
EXPOSE 10086
COPY ./src /WGDashboard/

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install wireguard sudo python3 python3-venv python3-pip net-tools -y && \
    apt install iproute2 -y && \
    mkdir -p /etc/amnezia/amneziawg

# Copy AmneziaWG binaries
COPY entrypoint.sh /WGDashboard/entrypoint.sh
COPY --from=bins /amneziawg-go /usr/bin/amneziawg-go
COPY --from=bins /awg /usr/bin/awg
COPY --from=bins /awg-quick /usr/bin/awg-quick

# Install necessary tools and libraries in the final image
RUN chmod +x /WGDashboard/wgd.sh && chmod +x /WGDashboard/entrypoint.sh

RUN if [ ! -c /dev/net/tun ]; then \
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200; \
fi


RUN ./wgd.sh install
# Start the script and keep it alive by tailing the logs
CMD ["/bin/bash", "-c", "/WGDashboard/wgd.sh start && tail -f /dev/null"]
