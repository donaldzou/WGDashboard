#!/bin/bash

# Path to the configuration file (exists because of previous function).
config_file="/data/wg-dashboard.ini"

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  # When using a custom directory to store the files, this part moves over and makes sure the installation continues.
  echo "Quick-installing..."

  if [ ! -d "/data/db" ]; then
    echo "Creating database dir"
    mkdir /data/db
  fi

  if [ ! -d "${WGDASH}/src/db" ]; then
    ln -s /data/db "${WGDASH}/src/db"
  fi
  
  if [ ! -f "${config_file}" ]; then
    echo "Creating wg-dashboard.ini file"
    touch "${config_file}"
  fi

  if [ ! -f "${WGDASH}/src/wg-dashboard.ini" ]; then
    ln -s "${config_file}" "${WGDASH}/src/wg-dashboard.ini"
  fi

  python3 -m venv "${WGDASH}"/src/venv
  . "${WGDASH}/src/venv/bin/activate"

  echo "Moving PIP dependency from ephemerality to runtime environment: psutil"
  mv /usr/lib/python3.12/site-packages/psutil* "${WGDASH}"/src/venv/lib/python3.12/site-packages
  
  echo "Moving PIP dependency from ephemerality to runtime environment: bcrypt"
  mv /usr/lib/python3.12/site-packages/bcrypt* "${WGDASH}"/src/venv/lib/python3.12/site-packages


  chmod +x "${WGDASH}"/src/wgd.sh
  cd "${WGDASH}"/src || exit
  ./wgd.sh install

  echo "Looks like the installation succeeded. Moving on."

  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  # This is done so WGDashboard it works out of the box

  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    echo "Standard wg0 Configuration file not found, grabbing template."
    cp -a "/configs/wg0.conf.template" "/etc/wireguard/wg0.conf"

    echo "Setting a secure private key." # SORRY 4 BE4 - Daan

    local privateKey
    privateKey=$(wg genkey)
    sed -i "s|^PrivateKey *=.*$|PrivateKey = ${privateKey}|g" /etc/wireguard/wg0.conf

    echo "Done setting template."
  else
    echo "Existing wg0 configuration file found, using that."
  fi
}

set_envvars() {
  printf "\n------------- SETTING ENVIRONMENT VARIABLES ----------------\n"

  # Check if the file is empty
  if [ ! -s "${config_file}" ]; then
    echo "Config file is empty. Creating [Peers] section."
    
    # Create [Peers] section with initial values
    {
      echo "[Peers]"
      echo "peer_global_dns = ${global_dns}"
      echo "remote_endpoint = ${public_ip}"
      #echo -e "\n[Server]"
    } > "${config_file}"

  else
    echo "Config file is not empty, using pre-existing."
  fi

  echo "Verifying current variables..."

  # Check and update the DNS if it has changed
  current_dns=$(grep "peer_global_dns = " "${config_file}" | awk '{print $NF}')
  if [ "${global_dns}" == "$current_dns" ]; then
    echo "DNS is correct, moving on."
    
  else
    echo "Changing default DNS..."
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" "${config_file}"
  fi

  if [ "${public_ip}" == "0.0.0.0" ]; then

    default_ip=$(curl -s ifconfig.me)

    echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"
    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" "${config_file}"

  else
    echo "Public-IP is correct, moving on."
  fi

}

# === CORE SERVICES ===
start_core() {
  printf "\n---------------------- STARTING CORE -----------------------\n"

  echo "Activating Python venv and executing the WireGuard Dashboard service."

  . "${WGDASH}"/src/venv/bin/activate
  cd "${WGDASH}"/src || return
  bash wgd.sh start

  # Isolated peers feature, first converting the existing configuration files and the given names to arrays.
  #
  # WILL BE REMOVED IN FUTURE WHEN WGDASHBOARD ITSELF SUPPORTS THIS!!
  #

  local configurations=(/etc/wireguard/*)
  IFS=',' read -r -a do_isolate <<< "${isolate}"
  non_isolate=()

  # Checking if there are matches between the two arrays.
  for config in "${configurations[@]}"; do
    config=$(echo "$config" | sed -e 's|.*/etc/wireguard/||' -e 's|\.conf$||')

    local found
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
  noneFound=0

  for interface in "${do_isolate[@]}"; do

    if [ "$interface" = "none" ] || [ "$interface" = "" ]; then
      echo "Found none, stopping isolation checking."
      noneFound=1
      break

    else

      if [ ! -f "/etc/wireguard/${interface}.conf" ]; then
        echo "Ignoring ${interface}"

      elif [ -f "/etc/wireguard/${interface}.conf" ]; then


        echo "Isolating interface:" "$interface"

        upblocking=$(grep -c "PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/"${interface}".conf)
        downblocking=$(grep -c "PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/"${interface}".conf)

        if [ "$upblocking" -lt 1 ] && [ "$downblocking" -lt 1 ]; then
          sed -i "/PostUp =/a PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/"${interface}".conf
          sed -i "/PreDown =/a PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP" /etc/wireguard/"${interface}".conf
        fi

      else
        echo "Configuration for $interface in enforce isolation does not seem to exist, continuing."
      fi

    fi

  done
  
  # Removing isolation for the configurations that did not match.


  for interface in "${non_isolate[@]}"; do
    if [ $noneFound -eq 1 ]; then
      break

    elif [ ! -f "/etc/wireguard/${interface}.conf" ]; then
      echo "Ignoring ${interface}"

    elif [ -f "/etc/wireguard/${interface}.conf" ]; then
      echo "Removing isolation, if isolation is present for:" "$interface"

      sed -i "/PostUp = iptables -I FORWARD -i ${interface} -o ${interface} -j DROP/d" /etc/wireguard/"${interface}".conf
      sed -i "/PreDown = iptables -D FORWARD -i ${interface} -o ${interface} -j DROP/d" /etc/wireguard/"${interface}".conf
    else
      echo "Configuration for $interface in removing isolation does not seem to exist, continuing."
    fi

  done

}

ensure_blocking() {
  sleep 1s
  echo -e "\nEnsuring container continuation."

  # Find and tail the latest error and access logs if they exist
  local logdir="/opt/wireguarddashboard/src/log"
  
  latestErrLog=$(find "$logdir" -name "error_*.log" -type f -print | sort -r | head -n 1)
  latestAccLog=$(find "$logdir" -name "access_*.log" -type f -print | sort -r | head -n 1)

  # Only tail the logs if they are found
  if [ -n "$latestErrLog" ] || [ -n "$latestAccLog" ]; then
    tail -f "$latestErrLog" "$latestAccLog"
  else
    echo "No log files found to tail."
  fi

  # Blocking command to keep the container running as a last resort.
  sleep infinity
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
ensure_installation
set_envvars
start_core
ensure_blocking