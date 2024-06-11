#!/bin/bash
echo "Starting the WireGuard Dashboard Docker container."

clean_up() {
  # Cleaning out previous data such as the .pid file and starting the WireGuard Dashboard. Making sure to use the python venv.
  echo "Looking for remains of previous instances..."
  if [ -f "/opt/wireguarddashboard/app/src/gunicorn.pid" ]; then
    echo "Found old .pid file, removing."
    rm /opt/wireguarddashboard/app/src/gunicorn.pid
  else
    echo "No remains found, continuing."
  fi
}

start_core() {
  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    cp "/wg0.conf" "/etc/wireguard/wg0.conf"
    echo "WireGuard interface file copied over."
  else
    echo "WireGuard interface file looks to already be existing."
  fi
  
  echo "Activating Python venv and executing the WireGuard Dashboard service."

  . "${WGDASH}"/venv/bin/activate
  cd "${WGDASH}"/app/src || return # If changing the directory fails (permission or presence error), then bash will exist this function, causing the WireGuard Dashboard to not be succesfully launched.
  bash wgd.sh start

  # The following section takes care of the firewall rules regarding the 'isolated_peers' feature, which allows or drops packets destined from the wg0 to the wg0 interface.
  if [ "${isolated_peers,,}" = "false" ]; then
    echo "Isolated peers disabled, adjusting."

    sed -i '/PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP/d' /etc/wireguard/wg0.conf
    sed -i '/PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP/d' /etc/wireguard/wg0.conf
  elif [ "${isolated_peers,,}" = "true" ]; then
    upblocking=$(grep -c "PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP" /etc/wireguard/wg0.conf)
    downblocking=$(grep -c "PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP" /etc/wireguard/wg0.conf)
    if [ "$upblocking" -lt 1 ] && [ "$downblocking" -lt 1 ]; then
      echo "Isolated peers enabled, adjusting."

      sed -i '/PostUp = iptables -t nat -I POSTROUTING 1 -s/a PostUp = iptables -I FORWARD -i wg0 -o wg0 -j DROP' /etc/wireguard/wg0.conf
      sed -i '/PreDown = iptables -t nat -D POSTROUTING 1 -s/a PreDown = iptables -D FORWARD -i wg0 -o wg0 -j DROP' /etc/wireguard/wg0.conf
    fi

  fi

  # The following section takes care of 
  if [ "${enable_wg0,,}" = "true" ]; then
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
    
    ln -sf /usr/share/zoneinfo/"${tz}" /etc/localtime
    echo "${tz}" > /etc/timezone
  fi

  # Changing the DNS used for clients and the dashboard itself.
  if [ "${global_dns}" != "$(grep "peer_global_dns = " /opt/wireguarddashboard/app/src/wg-dashboard.ini | awk '{print $NF}')" ]; then 
    echo "Changing default dns."

    #sed -i "s/^DNS = .*/DNS = ${global_dns}/" /etc/wireguard/wg0.conf # Uncomment if you want to have DNS on server-level.
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" /opt/wireguarddashboard/app/src/wg-dashboard.ini
  fi

  # Setting the public IP of the WireGuard Dashboard container host. If not defined, it will trying fetching it using a curl to ifconfig.me.
  if [ "${public_ip}" = "0.0.0.0" ]; then
    default_ip=$(curl -s ifconfig.me)
    echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" /opt/wireguarddashboard/app/src/wg-dashboard.ini
  elif [ "${public_ip}" != "$(grep "remote_endpoint = " /opt/wireguarddashboard/app/src/wg-dashboard.ini | awk '{print $NF}')" ]; then
    echo "Setting the Public-IP using given variable: ${public_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${public_ip}/" /opt/wireguarddashboard/app/src/wg-dashboard.ini
  fi
}

ensure_blocking() {
  sleep 1s
  echo "Ensuring container continuation."

  # This function checks if the latest error log is created and tails it for docker logs uses.
  if find "/opt/wireguarddashboard/app/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestErrLog=$(find /opt/wireguarddashboard/app/src/log -name "error_*.log" | head -n 1)
    latestAccLog=$(find /opt/wireguarddashboard/app/src/log -name "access_*.log" | head -n 1)
    tail -f "${latestErrLog}" "${latestAccLog}"
  fi

  # Blocking command in case of erroring. So the container does not quit.
  sleep infinity
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
clean_up
start_core
set_envvars
ensure_blocking