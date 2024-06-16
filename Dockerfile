FROM ubuntu:22.04

ARG WG_ADDRESS=$WG_ADDRESS

RUN apt-get update && \
 apt-get install -y --no-install-recommends iproute2 wireguard-tools iptables nano net-tools python3 python3-pip python3-venv procps openresolv inotify-tools && \
 apt-get clean

RUN mkdir -p /etc/wireguard/
RUN mkdir -p /opt/wgdashboard
RUN mkdir -p /opt/wgdashboard_tmp
# configure wireguard
RUN wg genkey |  tee /opt/wgdashboard_tmp/privatekey | wg pubkey |  tee /opt/wgdashboard_tmp/publickey

RUN  cd / && echo "[Interface]" > wg0.conf && echo "SaveConfig = true" >> wg0.conf && echo -n "PrivateKey = " >> wg0.conf && cat /opt/wgdashboard_tmp/privatekey >> wg0.conf \
    && echo  "ListenPort = 51820" >> wg0.conf && echo  "Address = ${WG_ADDRESS}" >> wg0.conf  && chmod 700 wg0.conf

COPY ./src /opt/wgdashboard_tmp
RUN pip3 install -r /opt/wgdashboard_tmp/requirements.txt   --no-cache-dir
# install requirements for old dashboard
RUN pip3 install -r /opt/wgdashboard_tmp/requirements_old.txt   --no-cache-dir
RUN rm -rf /opt/wgdashboard_tmp
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /opt/wgdashboard 

EXPOSE 10086
EXPOSE 51820/udp