#!/bin/bash

config_file="/data/wg-dashboard.ini"

trap 'bash ./wgd.sh stop; exit 0' SIGTERM

# Hash password with bcrypt
hash_password() {
  python3 -c "import bcrypt; print(bcrypt.hashpw('$1'.encode(), bcrypt.gensalt(12)).decode())"
}

# Function to set or update section/key/value in the INI file
set_ini() {
  local section="$1" key="$2" value="$3"
  local current_value
  
  # Add section if it doesn't exist
  grep -q "^\[${section}\]" "$config_file" \
    || printf "\n[%s]\n" "${section}" >> "$config_file"
  
  # Check current value if key exists
  if grep -q "^[[:space:]]*${key}[[:space:]]*=" "$config_file"; then
    current_value=$(grep "^[[:space:]]*${key}[[:space:]]*=" "$config_file" | cut -d= -f2- | xargs)
    
    # Don't display actual value if it's a password field
    if [[ "$key" == *"password"* ]]; then
      if [ "$current_value" = "$value" ]; then
        echo "- $key is already set correctly (value hidden)"
        return 0
      fi
      sed -i "/^\[${section}\]/,/^\[/{s|^[[:space:]]*${key}[[:space:]]*=.*|${key} = ${value}|}" "$config_file"
      echo "- Updated $key (value hidden)"
    else
      if [ "$current_value" = "$value" ]; then
        echo "- $key is already set correctly ($value)"
        return 0
      fi
      sed -i "/^\[${section}\]/,/^\[/{s|^[[:space:]]*${key}[[:space:]]*=.*|${key} = ${value}|}" "$config_file"
      echo "- Updated $key to: $value"
    fi
  else
    sed -i "/^\[${section}\]/a ${key} = ${value}" "$config_file"
    
    # Don't display actual value if it's a password field
    if [[ "$key" == *"password"* ]]; then
      echo "- Added new setting $key (value hidden)"
    else
      echo "- Added new setting $key: $value"
    fi
  fi
}

echo "------------------------- START ----------------------------"
echo "Starting the WireGuard Dashboard Docker container."

ensure_installation() {
  echo "Quick-installing..."
  chmod +x "${WGDASH}"/src/wgd.sh
  cd "${WGDASH}"/src || exit
  
  echo "Removing clear command from wgd.sh for better Docker logging."
  sed -i '/clear/d' ./wgd.sh
  
  # Create required directories and links
  [ ! -d "/data/db" ] && mkdir -p /data/db
  [ ! -d "${WGDASH}/src/db" ] && ln -s /data/db "${WGDASH}/src/db"
  [ ! -f "${config_file}" ] && touch "${config_file}"
  [ ! -f "${WGDASH}/src/wg-dashboard.ini" ] && ln -s "${config_file}" "${WGDASH}/src/wg-dashboard.ini"

  # Python venv
  python3 -m venv "${WGDASH}"/src/venv
  . "${WGDASH}/src/venv/bin/activate"
  
  # Copy libraries
  mv /usr/lib/python3.12/site-packages/{psutil,bcrypt}* "${WGDASH}"/src/venv/lib/python3.12/site-packages/
  
  ./wgd.sh install
  
  # Setup WireGuard if needed
  if [ ! -f "/etc/wireguard/wg0.conf" ]; then
    cp -a "/configs/wg0.conf.template" "/etc/wireguard/wg0.conf"
    sed -i "s|^PrivateKey *=.*$|PrivateKey = $(wg genkey)|g" /etc/wireguard/wg0.conf
  fi
}

set_envvars() {
  printf "\n------------- SETTING ENVIRONMENT VARIABLES ----------------\n"
  
  # Check if config file is empty
  if [ ! -s "${config_file}" ]; then
    echo "Config file is empty. Creating initial structure."
  fi
  
  echo "Checking basic configuration:"
  set_ini Peers peer_global_dns "${global_dns}"
  
  if [ -z "${public_ip}" ]; then
    public_ip=$(curl -s ifconfig.me)
    echo "Automatically detected public IP: ${public_ip}" 
  fi
  set_ini Peers remote_endpoint "${public_ip}"
  
  set_ini Server app_port "${wgd_port}"
  
  # Account settings - process all parameters
  echo "Configuring user account:"
  # Basic account variables
  [[ -n "$username" ]] && set_ini Account username "${username}"
  
  if [[ -n "$password" ]]; then
    echo "- Setting password"
    set_ini Account password "$(hash_password "${password}")"
  fi
  
  # Additional account variables
  [[ -n "$enable_totp" ]] && set_ini Account enable_totp "${enable_totp}"
  [[ -n "$totp_verified" ]] && set_ini Account totp_verified "${totp_verified}"
  [[ -n "$totp_key" ]] && set_ini Account totp_key "${totp_key}"
  
  # Welcome session
  [[ -n "$welcome_session" ]] && set_ini Other welcome_session "${welcome_session}"
  # If username and password are set but welcome_session isn't, disable it
  if [[ -n "$username" && -n "$password" && -z "$welcome_session" ]]; then
    set_ini Other welcome_session "false"
  fi
  
  # Autostart WireGuard
  if [[ -n "$wg_autostart" ]]; then
    echo "Configuring WireGuard autostart:"
    set_ini WireGuardConfiguration autostart "${wg_autostart}"
  fi
  
  # Email (check if any settings need to be configured)
  email_vars=("email_server" "email_port" "email_encryption" "email_username" "email_password" "email_from" "email_template")
  for var in "${email_vars[@]}"; do
    if [ -n "${!var}" ]; then
      echo "Configuring email settings:"
      break
    fi
  done
  
  # Email (iterate through all possible fields)
  email_fields=("server:email_server" "port:email_port" "encryption:email_encryption" 
                "username:email_username" "email_password:email_password" 
                "send_from:email_from" "email_template:email_template")
  
  for field_pair in "${email_fields[@]}"; do
    IFS=: read -r field var <<< "$field_pair"
    [[ -n "${!var}" ]] && set_ini Email "$field" "${!var}"
  done
}

# Start service and monitor logs
start_and_monitor() {
  printf "\n---------------------- STARTING CORE -----------------------\n"
  bash ./wgd.sh start
  
  sleep 1
  # Find and monitor log file
  find "${WGDASH}/src/log" -name "error_*.log" -type f -print0 | 
    xargs -0 ls -t 2>/dev/null | head -n1 | xargs tail -f 2>/dev/null ||
    echo "No log files found. Something went wrong!"
}

# Main execution flow
ensure_installation
set_envvars
start_and_monitor