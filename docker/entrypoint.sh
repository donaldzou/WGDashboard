#!/bin/bash
echo "Starting the WireGuard Dashboard Docker container."

clean_up() {
  echo "Looking for remains of previous instances..."
  if [ -f "/opt/wireguardashboard/app/src/gunicorn.pid" ]; then
    echo "Found old .pid file, removing."
    rm /opt/wireguardashboard/app/src/gunicorn.pid
  else
    echo "No remains found, continuing."
  fi
}

start_core() {
  # Cleaning out previous data such as the .pid file and starting the WireGuard Dashboard. Making sure to use the python venv.
  echo "Activating Python venv and executing the WireGuard Dashboard service."

  . ${WGDASH}/venv/bin/activate
  cd ${WGDASH}/app/src
  bash wgd.sh start

  echo "${isolated_peers}"
  if [ "${isolated_peers,,}" == "false" ]; then
    echo "Isolated peers disabled, adjusting."

    sed -i '/^.*FORWARD -i wg0 -o wg0 -j DROP.*$/s/^/#/' /etc/wireguard/wg0.conf
  elif [ "${isolated_peers,,}" == "true" ]; then
    echo "Isolated peers enabled, adjusting."

    sed -i 's/^#//' /etc/wireguard/wg0.conf
  fi

  if [ "${enable_wg0,,}" == "true" ]; then
    echo "Preference for wg0 to be turned on found."

    wg-quick up wg0
  else
    echo "Preference for wg0 to be turned off found."
  fi
}

set_envvars() {
  echo "Setting relevant variables for operation."

  # If the timezone is different, for example in North-America or Asia.
  if [ "${tz}" != "$(cat /etc/timezone)" ]; then
    echo "Changing timezone."
    
    ln -sf /usr/share/zoneinfo/${tz} /etc/localtime
    echo ${tz} > /etc/timezone
  fi

  # Changing the DNS used for clients and the dashboard itself.
  if [ "${global_dns}" != "$(grep "peer_global_dns = " /opt/wireguardashboard/app/src/wg-dashboard.ini | awk '{print $NF}')" ]; then 
    echo "Changing default dns."

    sed -i 's/^DNS = .*/DNS = ${global_dns}/' /etc/wireguard/wg0.conf
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  fi

  # Setting the public IP of the WireGuard Dashboard container host. If not defined, it will trying fetching it using a curl to ifconfig.me.
  if [ "${public_ip}" == "0.0.0.0" ]; then
    default_ip=$(curl -s ifconfig.me)
    echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  elif [ "${public_ip}" != $(grep "remote_endpoint = " /opt/wireguardashboard/app/src/wg-dashboard.ini | awk '{print $NF}') ]; then
    echo "Setting the Public-IP using given variable: ${public_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${public_ip}/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  fi
}

ensure_blocking() {
  echo "Ensuring container continuation."

  # This function checks if the latest error log is created and tails it for docker logs uses.
  if find "/opt/wireguardashboard/app/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestlog=$(ls -t /opt/wireguardashboard/app/src/log/error_*.log | head -n 1)
    sleep 3s
    tail -f ${latestlog}
  fi

  # Blocking command in case of erroring. So the container does not quit.
  sleep infinity
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
clean_up
start_core
set_envvars
ensure_blocking