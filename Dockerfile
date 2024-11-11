# Исходный образ Alpine Linux
FROM alpine:latest
LABEL maintainer="dselen@nerthus.nl"

# Определение переменных окружения
ARG wg_net="10.0.0.1"
ARG wg_port="51820"

# Переменные окружения, которые можно изменить во время выполнения контейнера
ENV TZ="Europe/Amsterdam"
ENV global_dns="1.1.1.1"
ENV isolate="none"
ENV public_ip="0.0.0.0"
ENV WGDASH=/opt/wireguarddashboard

# Установка необходимых пакетов
RUN apk update \
  && apk add --no-cache bash git tzdata \
  iptables ip6tables openrc curl wireguard-tools \
  sudo py3-psutil py3-bcrypt \
  && apk upgrade

# Создание директорий для хранения данных и конфигурации
RUN mkdir -p /data /configs ${WGDASH}/src \
  && chmod 700 /data /configs

# Копирование файлов WGDashboard в контейнер
COPY ./src ${WGDASH}/src

# Генерация шаблона конфигурации WireGuard с использованием аргументов
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

# Проверка работоспособности контейнера (процесс gunicorn и tail)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD sh -c 'pgrep gunicorn > /dev/null && pgrep tail > /dev/null' || exit 1

# Копирование скрипта запуска
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Определение постоянных томов для сохранения данных и конфигураций
VOLUME ["/data", "/configs", "/opt/wireguarddashboard/db"]

# Открытие порта для WGDashboard
EXPOSE 10086

# Запуск скрипта entrypoint при запуске контейнера
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
