#!/bin/bash

# Path to the configuration file (exists because of previous function).
config_file="/data/wg-dashboard.ini"

trap 'stop_service' SIGTERM

stop_service() {
  echo "[WGDashboard] Stopping WGDashboard..."
  /bin/bash ./wgd.sh stop
  exit 0
}

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  # When using a custom directory to store the files, this part moves over and makes sure the installation continues.
  echo "Quick-installing..."

  # Make the wgd.sh script executable.
  chmod +x "${WGDASH}"/src/wgd.sh
  cd "${WGDASH}"/src || exit

  # Github issue: https://github.com/donaldzou/WGDashboard/issues/723
  echo "Checking for stale pids..."
  if [[ -f ${WGDASH}/src/gunicorn.pid ]]; then
    echo "Found stale pid, removing..."
    rm ${WGDASH}/src/gunicorn.pid
  fi

  # Removing clear shell command from the wgd.sh script to enhance docker logging.
  echo "Removing clear command from wgd.sh for better Docker logging."
  sed -i '/clear/d' ./wgd.sh

  # Create the databases directory if it does not exist yet.
  if [ ! -d "/data/db" ]; then
    echo "Creating database dir"
    mkdir /data/db
  fi

  # Linking the database on the persistent directory location to where WGDashboard expects.
  if [ ! -d "${WGDASH}/src/db" ]; then
    ln -s /data/db "${WGDASH}/src/db"
  fi

  # Create the wg-dashboard.ini file if it does not exist yet.
  if [ ! -f "${config_file}" ]; then
    echo "Creating wg-dashboard.ini file"
    touch "${config_file}"
  fi

  # Link the wg-dashboard.ini file from the persistent directory to where WGDashboard expects it.
  if [ ! -f "${WGDASH}/src/wg-dashboard.ini" ]; then
    ln -s "${config_file}" "${WGDASH}/src/wg-dashboard.ini"
  fi

  # Create the Python virtual environment.
  . "${WGDASH}/src/venv/bin/activate"

  # Use the bash interpreter to install WGDashboard according to the wgd.sh script.
  /bin/bash ./wgd.sh install

  echo "Looks like the installation succeeded. Moving on."

  # This first step is to ensure the wg0.conf file exists, and if not, then its copied over from the ephemeral container storage.
  # This is done so WGDashboard it works out of the box, it also sets a randomly generated private key.

  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    echo "Standard wg0 Configuration file not found, grabbing template."
    cp -a "/configs/wg0.conf.template" "/etc/wireguard/wg0.conf"

    echo "Setting a secure private key."

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
      echo -e "\n[Server]"
      echo "app_port = ${wgd_port}"
    } > "${config_file}"

  else
    echo "Config file is not empty, using pre-existing."
  fi

  echo "Verifying current variables..."

  # Check and update the DNS if it has changed
  current_dns=$(grep "peer_global_dns = " "${config_file}" | awk '{print $NF}')
  if [ "${global_dns}" == "$current_dns" ]; then
    echo "DNS is set correctly, moving on."

  else
    echo "Changing default DNS..."
    sed -i "s/^peer_global_dns = .*/peer_global_dns = ${global_dns}/" "${config_file}"
  fi

  # Checking the current set public IP and changing it if it has changed.
  current_public_ip=$(grep "remote_endpoint = " "${config_file}" | awk '{print $NF}')
  if [ "${public_ip}" == "" ]; then
    default_ip=$(curl -s ifconfig.me)

    echo "Trying to fetch the Public-IP using ifconfig.me: ${default_ip}"
    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${default_ip}/" "${config_file}"
  elif [ "${current_public_ip}" != "${public_ip}" ]; then
    sed -i "s/^remote_endpoint = .*/remote_endpoint = ${public_ip}/" "${config_file}"
  else
    echo "Public-IP is correct, moving on."
  fi

  # Checking the current WGDashboard web port and changing if needed.
  current_wgd_port=$(grep "app_port = " "${config_file}" | awk '{print $NF}')
  if [ "${current_wgd_port}" == "${wgd_port}" ]; then
    echo "Current WGD port is set correctly, moving on."
  else
    echo "Changing default WGD port..."
    sed -i "s/^app_port = .*/app_port = ${wgd_port}/" "${config_file}"
  fi
}

# === CORE SERVICES ===
start_core() {
  printf "\n---------------------- STARTING CORE -----------------------\n"

  # Due to some instances complaining about this, making sure its there every time.
  mkdir -p /dev/net
  mknod /dev/net/tun c 10 200
  chmod 600 /dev/net/tun

  # Actually starting WGDashboard
  echo "Activating Python venv and executing the WireGuard Dashboard service."
  /bin/bash ./wgd.sh start
}

ensure_blocking() {
  # Wait a second before continuing, to give the python program some time to get ready.
  sleep 1s
  echo -e "\nEnsuring container continuation."

  # Find and tail the latest error and access logs if they exist
  local logdir="${WGDASH}/src/log"

  latestErrLog=$(find "$logdir" -name "error_*.log" -type f -print | sort -r | head -n 1)

  # Only tail the logs if they are found
  if [ -n "$latestErrLog" ]; then
    tail -f "$latestErrLog" &

    # Wait for the tail process to end.
    wait $!
  else
    echo "No log files found to tail. Something went wrong, exiting..."
    exit 1
  fi
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
ensure_installation
set_envvars
start_core
ensure_blocking
