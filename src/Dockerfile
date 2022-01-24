FROM python:3.10.2-alpine3.15 as base


RUN  apk  --update-cache upgrade && apk add --no-cache gcc g++ libffi-dev  jpeg-dev zlib-dev libjpeg  wireguard-tools   iptables ip6tables inotify-tools \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /etc/wireguard/

# configure wireguard
RUN wg genkey |  tee /etc/wireguard/privatekey | wg pubkey |  tee /etc/wireguard/publick



RUN  cd /etc/wireguard/ && echo "[Interface]" >> wg0.conf &&  echo -n "PrivateKey = " >> wg0.conf && cat privatekey >> wg0.conf  \
    && echo  "ListenPort = 51820" >> wg0.conf && echo  "Address = 10.1.1.1/32" >> wg0.conf  && chmod 700 wg0.conf


COPY requirements.txt  /opt/wgdashboard/
RUN pip3 install -r /opt/wgdashboard/requirements.txt   --no-cache-dir


FROM base 
COPY . /opt/WGDashboard/src
WORKDIR /opt/WGDashboard/src 


EXPOSE 10086
EXPOSE 51820/udp

