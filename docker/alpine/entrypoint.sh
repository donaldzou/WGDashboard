#!/bin/bash

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  # When using a custom directory to store the files, this part moves over and makes sure the installation continues.
  echo "Checking if everything is present."

  if [ -z "$(ls -A "${WGDASH}")" ]; then
    echo "Detected empty directory, moving over..."

    mv /setup/app/* "${WGDASH}"
    python3 -m venv "${WGDASH}"/src/venv
    . "${WGDASH}/src/venv/bin/activate"
    chmod +x "${WGDASH}"/src/wgd.sh
    cd "${WGDASH}"/src || exit
    ./wgd.sh install

    echo "Looks like the installation succesfully moved over."
  else
    echo "Looks like everything is present."
  fi

  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    echo "Standard wg0 Configuration file not found, grabbing template."
    cp "/setup/conf/wg0.conf" "/etc/wireguard/wg0.conf"

    echo "Setting a secure private key."

    local privateKey
    privateKey=$(wg genkey)

    sed -i "s|^PrivateKey =$|PrivateKey = ${privateKey}|g" /etc/wireguard/wg0.conf
    sed -i "s|^PrivateKey *=.*$|PrivateKey = ${privateKey}|g" /etc/wireguard/wg0.conf
    echo "Done setting template."
  else
    echo "Existing wg0 configuration file found, using that."
  fi
}

# === CLEAN UP ===
clean_up() {
  printf "\n------------------------ CLEAN UP --------------------------\n"

  # Cleaning out previous data such as the .pid file and starting the WireGuard Dashboard. Making sure to use the python venv.
  echo "Looking for remains of previous instances..."
  local pid_file="${WGDASH}/src/gunicorn.pid"
  if [ -f "$pid_file" ]; then
    echo "Found old pid file, removing."
    rm $pid_file
  else
    echo "No pid remains found, continuing."
  fi

  # Also check for Python caches (pycache) inspired by https://github.com/shuricksumy
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

  local logdir="${WGDASH}/src/log"
  echo "Cleaning log directory."
  find /opt/wireguarddashboard/src/log -name 'access_*.log' -exec rm {} +
  find /opt/wireguarddashboard/src/log -name 'error_*.log' -exec rm {} +
  echo "Removed unneeded logs!"
}

#update_checker() {
  #if [ "$update" = "yes" ]; then
  # echo "Activating Python venv and executing the WireGuard Dashboard service."
  #  . "${WGDASH}/src/venv/bin/activate"
  #  cd "${WGDASH}"/src || exit
  #  bash wgd.sh update
  #else
  #  echo "Auto Updater disabled"
  #fi
#}

# === SET ENV VARS ===
set_envvars() {
  printf "\n------------- SETTING ENVIRONMENT VARIABLES ----------------\n"

  # If the timezone is different, for example in North-America or Asia.
  if [ "${TZ}" != "$(cat /etc/localtime)" ]; then
    echo "Changing timezone."
    
    ln -sf /usr/share/zoneinfo/"${TZ}" /etc/localtime
    echo "${TZ}" > /etc/timezone
  else
    echo "Timezone is set correctly."
  fi

  # Changing the DNS used for clients and the dashboard itself.
  if [ "${global_dns}" != "$(grep "peer_global_dns = " /opt/wireguarddashboard/src/wg-dashboard.ini | awk '{print $NF}')" ]; then 
    echo "Changing default dns."

    #sed -i "s/^DNS = .*/DNS = ${global_dns}/" /etc/wireguard/wg0.conf # Uncomment if you want to have DNS on server-level.
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" /opt/wireguarddashboard/src/wg-dashboard.ini
  else
    echo "DNS is set correctly."
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

# === CORE SERVICES ===
start_core() {
  printf "\n---------------------- STARTING CORE -----------------------\n"

  echo "Activating Python venv and executing the WireGuard Dashboard service."
  . "${WGDASH}"/src/venv/bin/activate
  cd "${WGDASH}"/src || return # If changing the directory fails (permission or presence error), then bash will exist this function, causing the WireGuard Dashboard to not be succesfully launched.
  bash wgd.sh start

  # Isolated peers feature, first converting the existing configuration files and the given names to arrays.
  local configurations=(/etc/wireguard/*)
  IFS=',' read -r -a do_isolate <<< "${isolate}"
  non_isolate=()

  # Checking if there are matches between the two arrays.
  for config in "${configurations[@]}"; do
    local config=$(echo "$config" | sed -e 's|.*/etc/wireguard/||' -e 's|\.conf$||')
    found=false
    for interface in "${do_isolate[@]}"; do
      if [[ "$config" == "$interface" ]]; then
        found=true
        break
      fi
    done
    if [ "$found" = false ]; then
      non_isolate+=("$config")
    fi
  done

  # Isolating the matches.
  for interface in "${do_isolate[@]}"; do
    if [ "$interface" = "none" ]; then
      echo "Found: $interface, stopping isolation checking."
      break
    else
      if [ -f "/etc/wireguard/${interface}.conf" ]; then
        echo "Isolating interface:" $interface
        upblocking=$(grep -c "PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/${interface}.conf)
        downblocking=$(grep -c "PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/${interface}.conf)

        if [ "$upblocking" -lt 1 ] && [ "$downblocking" -lt 1 ]; then
          sed -i "/PostUp =/a PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/${interface}.conf
          sed -i "/PreDown =/a PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/${interface}.conf
        fi
      else
        echo "Configuration for $interface does not seem to exist, continuing."
      fi
    fi
  done
  
  # Removing isolation for the configurations that did not match.
  for interface in "${non_isolate[@]}"; do
    if [ -f "/etc/wireguard/${interface}.conf" ]; then
      echo "Removing Isolation if present for:" $interface
      sed -i "/PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP/d" /etc/wireguard/${interface}.conf
      sed -i "/PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP/d" /etc/wireguard/${interface}.conf
    else
      echo "Configuration for $interface does not seem to exist, continuing."
    fi
  done

  # The following section takes care of enabling wireguard interfaces on startup. Using arrays and given arguments.
  IFS=',' read -r -a enable_array <<< "${enable}"

  for interface in "${enable_array[@]}"; do
    if [ "$interface" = "none" ]; then
      echo "Found: $interface, stopping enabling checking."
      break
    else
      echo "Enabling interface:" $interface
      
      local fileperms=$(stat -c "%a" /etc/wireguard/${interface}.conf)
      if [ $fileperms -eq 644 ]; then
        echo "Configuration is world accessible, adjusting."
        chmod 600 "/etc/wireguard/${interface}.conf"    
      fi

      if [ -f "/etc/wireguard/${interface}.conf" ]; then
        wg-quick up $interface
      else
        echo "No corresponding configuration file found for $interface doing nothing."
      fi
    fi
  done
}

# === CLEAN UP ===
ensure_blocking() {
  printf "\n-------------- ENSURING CONTAINER CONTINUATION -------------\n"

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
ensure_installation
clean_up
#update_checker
start_core
set_envvars
ensure_blocking