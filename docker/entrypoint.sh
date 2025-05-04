#!/bin/bash

# Path to the configuration file (exists because of previous function).
config_file="/data/wg-dashboard.ini"

trap 'stop_service' SIGTERM

stop_service() {
  echo "[WGDashboard] Stopping WGDashboard..."
  bash ./wgd.sh stop
  exit 0
}

# Function to hash password using bcrypt
hash_password() {
  local password="$1"
  # Generate bcrypt hash using Python
  python3 -c "import bcrypt; print(bcrypt.hashpw('${password}'.encode(), bcrypt.gensalt(12)).decode())"
}

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  # When using a custom directory to store the files, this part moves over and makes sure the installation continues.
  echo "Quick-installing..."

  chmod +x "${WGDASH}"/src/wgd.sh
  cd "${WGDASH}"/src || exit

  echo "Removing clear command from wgd.sh for better Docker logging."
  sed -i '/clear/d' ./wgd.sh

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

  current_wgd_port=$(grep "app_port = " "${config_file}" | awk '{print $NF}')
  if [ "${current_wgd_port}" == "${wgd_port}" ]; then
    echo "Current WGD port is set correctly, moving on."
  else
    echo "Changing default WGD port..."
    sed -i "s/^app_port = .*/app_port = ${wgd_port}/" "${config_file}"
  fi
  
  # Check and update account settings if provided
  if [ -n "${username}" ] && [ -n "${password}" ]; then
    current_username=$(grep "^username = " "${config_file}" | awk '{print $NF}')
    if [ "${username}" == "${current_username}" ]; then
      echo "Username is set correctly, moving on."
    else
      echo "Setting username..."
      if grep -q "^\[Account\]" "${config_file}"; then
        sed -i "s/^username = .*/username = ${username}/" "${config_file}"
      else
        echo -e "\n[Account]" >> "${config_file}"
        echo "username = ${username}" >> "${config_file}"
        echo "enable_totp = false" >> "${config_file}"
        echo "totp_verified = false" >> "${config_file}"
        echo "totp_key = " >> "${config_file}"
      fi
    fi
    
    # Always update password when provided
    echo "Setting password..."
    hashed_password=$(hash_password "${password}")
    if grep -q "^password = " "${config_file}"; then
      sed -i "s|^password = .*|password = ${hashed_password}|" "${config_file}"
    else
      # If [Account] section exists but password line doesn't
      if grep -q "^\[Account\]" "${config_file}"; then
        sed -i "/\[Account\]/a password = ${hashed_password}" "${config_file}"
      fi
    fi
    
    # Set welcome_session to false
    if grep -q "^\[Other\]" "${config_file}"; then
      current_welcome=$(grep "^welcome_session = " "${config_file}" | awk '{print $NF}')
      if [ "${current_welcome}" == "false" ]; then
        echo "Welcome session already disabled, moving on."
      else
        echo "Disabling welcome session..."
        sed -i "s/^welcome_session = .*/welcome_session = false/" "${config_file}"
      fi
    else
      echo -e "\n[Other]" >> "${config_file}"
      echo "welcome_session = false" >> "${config_file}"
    fi
  fi
  
  # Check TOTP setting if provided
  if [ -n "${enable_totp}" ]; then
    current_totp=$(grep "^enable_totp = " "${config_file}" | awk '{print $NF}')
    if [ "${enable_totp}" == "${current_totp}" ]; then
      echo "TOTP setting is correct, moving on."
    else
      echo "Setting TOTP configuration..."
      if grep -q "^enable_totp = " "${config_file}"; then
        sed -i "s/^enable_totp = .*/enable_totp = ${enable_totp}/" "${config_file}"
      fi
    fi
  fi
  
  # Check WireGuard autostart setting
  if [ -n "${wg_autostart}" ]; then
    if grep -q "^\[WireGuardConfiguration\]" "${config_file}"; then
      current_autostart=$(grep "^autostart = " "${config_file}" | awk '{print $NF}')
      if [ "${wg_autostart}" == "${current_autostart}" ]; then
        echo "WireGuard autostart is set correctly, moving on."
      else
        echo "Updating WireGuard autostart..."
        sed -i "s/^autostart = .*/autostart = ${wg_autostart}/" "${config_file}"
      fi
    else
      echo "Setting new WireGuard autostart configuration..."
      echo -e "\n[WireGuardConfiguration]" >> "${config_file}"
      echo "autostart = ${wg_autostart}" >> "${config_file}"
    fi
  fi
}

# === CORE SERVICES ===
start_core() {
  printf "\n---------------------- STARTING CORE -----------------------\n"

  echo "Activating Python venv and executing the WireGuard Dashboard service."
  bash ./wgd.sh start
}

ensure_blocking() {
  sleep 1s
  echo -e "\nEnsuring container continuation."

  # Find and tail the latest error and access logs if they exist
  local logdir="${WGDASH}/src/log"

  latestErrLog=$(find "$logdir" -name "error_*.log" -type f -print | sort -r | head -n 1)

  # Only tail the logs if they are found
  if [ -n "$latestErrLog" ]; then
    tail -f "$latestErrLog" &
    wait $!
  else
    echo "No log files found to tail. Something went wrong, exiting..."
  fi
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
ensure_installation
set_envvars
start_core
ensure_blocking
