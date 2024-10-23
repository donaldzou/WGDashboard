#!/bin/bash

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  # When using a custom directory to store the files, this part moves over and makes sure the installation continues.
  echo "Checking if everything is present."

  if [ -z "$(ls -A "${WGDASH}")" ]; then # [ ! -f "/data/wg-dashboard.ini" ] && [ ! -d "/data/db" ]
    echo "Detected empty directory, moving over..."

    # Moving over source files. (This does not include src/db and src/wg-dashboard.ini folder and file.)
    mv -v /setup/app/* "${WGDASH}"

    [ ! -d "/data/db" ] && echo "Creating database dir" && mkdir /data/db
    ln -s /data/db "${WGDASH}/src/db"

    [ ! -f "/data/wg-dashboard.ini" ] && echo "Creating wg-dashboard.ini file" && touch /data/wg-dashboard.ini
    ln -s /data/wg-dashboard.ini "${WGDASH}/src/wg-dashboard.ini"


    python3 -m venv "${WGDASH}"/src/venv
    . "${WGDASH}/src/venv/bin/activate"

    mv  /usr/lib/python3.12/site-packages/psutil* "${WGDASH}"/src/venv/lib/python3.12/site-packages
    mv  /usr/lib/python3.12/site-packages/bcrypt* "${WGDASH}"/src/venv/lib/python3.12/site-packages

    chmod +x "${WGDASH}"/src/wgd.sh
    cd "${WGDASH}"/src || exit
    ./wgd.sh install

    echo "Looks like the installation succesfully moved over."
  else
    echo "Looks like everything is present. Or the directory is not empty."
  fi

  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  # This is done so WGDashboard it works out of the box

  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    echo "Standard wg0 Configuration file not found, grabbing template."
    cp -a "/setup/conf/wg0.conf" "/etc/wireguard/wg0.conf"

    echo "Setting a secure private key." # SORRY 4 BE4 - Daan

    local privateKey=$(wg genkey)
    sed -i "s|^PrivateKey *=.*$|PrivateKey = ${privateKey}|g" /etc/wireguard/wg0.conf

    echo "Done setting template."
  else
    echo "Existing wg0 configuration file found, using that."
  fi
}

clean_up() {
  printf "\n------------------------ CLEAN UP --------------------------\n"

  local pid_file="${WGDASH}/src/gunicorn.pid"
  local pycache="${WGDASH}/src/__pycache__"
  local logdir="${WGDASH}/src/log"

  echo "Looking for remains of previous instances..."

  # Handle the .pid file cleanup
  if [ -f "$pid_file" ]; then
    echo "Found old pid file, removing."
    rm -f "$pid_file"
  else
    echo "No pid remains found, continuing."
  fi

  # Remove Python caches (__pycache__)
  echo "Looking for remains of pycache..."
  if [ -d "$pycache" ]; then
    if find "$pycache" -type f -print -quit | grep -q .; then
      echo "Found old pycaches, removing."
      rm -rf "$pycache"
    else
      echo "No pycaches found, continuing."
    fi
  else
    echo "No pycaches directory found, continuing."
  fi

  # Clean up log files
  echo "Cleaning log directory..."
  find "$logdir" -type f -name 'access_*.log' -o -name 'error_*.log' -exec rm -f {} +
  echo "Removed unneeded logs!"
}


set_envvars() {
  printf "\n------------- SETTING ENVIRONMENT VARIABLES ----------------\n"

  # Path to the configuration file (exists because of previous function).
  local config_file="/opt/wireguarddashboard/src/wg-dashboard.ini"

  # Check if the file is empty
  if [ ! -s "$config_file" ]; then
    echo "Config file is empty. Creating [Peers] section."
    
    # Create [Peers] section with initial values
    {
      echo "[Peers]"
      echo "remote_endpoint = ${public_ip}"
      echo "peer_global_dns = ${global_dns}"
    } > "$config_file"

  else
    echo "Config file is not empty"

    # Check and update the DNS if it has changed
    current_dns=$(grep "peer_global_dns = " "$config_file" | awk '{print $NF}')
    if [ "${global_dns}" != "$current_dns" ]; then
      echo "Changing default DNS."
      sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" "$config_file"
    else
      echo "DNS is set correctly."
    fi

    # Determine the public IP and update if necessary
    if [ "${public_ip}" = "0.0.0.0" ]; then
      default_ip=$(curl -s ifconfig.me)
      echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"
      sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" "$config_file"
    else
      current_ip=$(grep "remote_endpoint = " "$config_file" | awk '{print $NF}')
      if [ "${public_ip}" != "$current_ip" ]; then
        echo "Setting the Public-IP using given variable: ${public_ip}"
        sed -i "s/^remote_endpoint = .*/remote_endpoint = ${public_ip}/" "$config_file"
      fi

    fi

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
  #
  # WILL BE REMOVED IN FUTURE WHEN WGDASHBOARD ITSELF SUPPORTS THIS!!
  #

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
clean_up
start_core
ensure_blocking