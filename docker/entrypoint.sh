#!/bin/bash
echo "\nStarting the WireGuard Dashboard Docker container."

# Execute functions for the WireGuard Dashboard services, then set the environment variables
start_core
set_envvars
ensure_blocking

start_core() {
  # Cleaning out previous data such as the .pid file and starting the WireGuard Dashboard. Making sure to use the python venv.
  echo "Activating Python venv and executing the WireGuard Dashboard service..."

  rm /opt/wireguardashboard/app/src/gunicorn.pid
  . ${WGDASH}/venv/bin/activate
  bash ${WGDASH}/app/src/wgd.sh start
}

set_envvars() {
  echo "Setting relevant variables for operation..."

  # If the timezone is different, for example in North-America or Asia.
  if [ "$tz" != "Europe/Amsterdam" ]; then
    echo "Changing timezone..."
    
    ln -sf /usr/share/zoneinfo/$tz /etc/localtime
  fi

  # Changing the DNS used for clients and the dashboard itself.
  if [ "$global_dns" != "1.1.1.1" ]; then
    echo "Changing default dns..."

    sed -i 's/^DNS = .*/DNS = ${global_dns}/' /etc/wireguard/wg0.conf
    sed -i "s/^peer_global_dns = .*/peer_global_dns = $global_dns/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  fi

  # Setting the public IP of the WireGuard Dashboard container host. If not defined, it will trying fetching it using a curl to ifconfig.me.
  if [ "$public_ip" != "0.0.0.0" ]; then
    echo "Setting the Public-IP using given variable: $public_ip"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = $public_ip/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  else
    default_ip=$(curl ifconfig.me)
    echo "Trying to fetch the Public-IP using ifconfig.me: $default_ip"

    sed -i "s/^remote_endpoint = .*/remote_endpoint = $default_ip/" /opt/wireguardashboard/app/src/wg-dashboard.ini
  fi
}

ensure_blocking() {
  echo "Ensuring container continuation..."
  
  # This function checks if the latest error log is created and tails it for docker logs uses.
  if find "/opt/wireguardashboard/app/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestlog=$(ls -t /opt/wireguardashboard/app/src/log/error_*.log | head -n 1)
    sleep 3s
    tail -f $latestlog
  fi

  # Blocking command in case of erroring. So the container does not quit.
  sleep infinity
}