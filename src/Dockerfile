FROM lscr.io/linuxserver/wireguard

run  apt-get update && \
    apt-get install -y   python3 python3-pip   python3-dev  python3-setuptools  libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/WGDashboard
RUN pip3 install -r /opt/WGDashboard/requirements.txt   --no-cache-dir


EXPOSE 10086

CMD  ["python3", "/opt/WGDashboard/dashboard.py  > log/run.log 2>&1 &"]