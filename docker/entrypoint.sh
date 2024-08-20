#!/bin/bash
echo "Starting the WireGuard Dashboard Docker container."

# === CLEAN UP ===
clean_up() {
  echo "---------------------    CLEAN UP    -----------------------"
  # Cleaning out previous data such as the .pid file and starting the WireGuard Dashboard. Making sure to use the python venv.
  echo "Looking for remains of previous instances..."
  local pid_file="${WGDASH}/src/gunicorn.pid"
  if [ -f $pid_file ]; then
    echo "Found old .pid file, removing."
    rm $pid_file
  else
    echo "No pid remains found, continuing."
  fi

  local pycache="${WGDASH}/src/__pycache__"
  if [ -d "$pycache" ]; then
    local pycache_filecount=$(find "$pycache" -maxdepth 1 -type f | wc -l)
    if [ "$pycache_filecount" -gt 0 ]; then
      echo "Found old pycaches, removing."
      rm -rf "$pycache"/*
    else
      echo "No pycaches found, continuing."
    fi
  else
    echo "No pycaches found, continuing."
  fi
}

# === CORE SERVICES ===
start_core() {
  echo "---------------------  STARTING CORE -----------------------"

  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    cp "/wg0.conf" "/etc/wireguard/wg0.conf"
    echo "Standard WG0 Configuration file not found, grabbing template."
  else
    echo "Standard WG0 Configuration file found, using that."
  fi
  
  echo "Activating Python venv and executing the WireGuard Dashboard service."
  . "${WGDASH}"/src/venv/bin/activate
  cd "${WGDASH}"/src || return # If changing the directory fails (permission or presence error), then bash will exist this function, causing the WireGuard Dashboard to not be succesfully launched.
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

  # The following section takes care of enabling wireguard interfaces on startup.
  IFS=',' read -r -a enable_array <<< "${enable}"
  for interface in "${enable_array[@]}"; do
    echo "Preference for $interface to be turned on found."
    if [ -f "/etc/wireguard/${interface}.conf" ]; then
      echo "Found corresponding configuration file, activating..."
      wg-quick up $interface
    else
      echo "No corresponding configuration file found for $interface doing nothing."
    fi
  done
}

# === SET ENV VARS ===
set_envvars() {
  echo "------------------------------------------------------------"
  echo "Setting relevant variables for operation."

  # If the timezone is different, for example in North-America or Asia.
  if [ "${tz}" != "$(cat /etc/timezone)" ]; then
    echo "Changing timezone."
    
    ln -sf /usr/share/zoneinfo/"${tz}" /etc/localtime
    echo "${tz}" > /etc/timezone
  fi

  # Changing the DNS used for clients and the dashboard itself.
  if [ "${global_dns}" != "$(grep "peer_global_dns = " /opt/wireguarddashboard/src/wg-dashboard.ini | awk '{print $NF}')" ]; then 
    echo "Changing default dns."

    #sed -i "s/^DNS = .*/DNS = ${global_dns}/" /etc/wireguard/wg0.conf # Uncomment if you want to have DNS on server-level.
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" /opt/wireguarddashboard/src/wg-dashboard.ini
  fi

  # Setting the public IP of the WireGuard Dashboard container host. If not defined, it will trying fetching it using a curl to ifconfig.me.
  if [ "${public_ip}" = "0.0.0.0" ]; then
    default_ip=$(curl -s ifconfig.me)
    echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" /opt/wireguarddashboard/src/wg-dashboard.ini
  elif [ "${public_ip}" != "$(grep "remote_endpoint = " /opt/wireguarddashboard/src/wg-dashboard.ini | awk '{print $NF}')" ]; then
    echo "Setting the Public-IP using given variable: ${public_ip}"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${public_ip}/" /opt/wireguarddashboard/src/wg-dashboard.ini
  fi
}

# === CLEAN UP ===
ensure_blocking() {
  echo "------------------------------------------------------------"
  sleep 1s
  echo "Ensuring container continuation."

  # This function checks if the latest error log is created and tails it for docker logs uses.
  if find "/opt/wireguarddashboard/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestErrLog=$(find /opt/wireguarddashboard/src/log -name "error_*.log" | head -n 1)
    latestAccLog=$(find /opt/wireguarddashboard/src/log -name "access_*.log" | head -n 1)
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