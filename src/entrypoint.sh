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



ensure_blocking() {
  sleep 1s
  echo "Ensuring container continuation."

  # This function checks if the latest error log is created and tails it for docker logs uses.
  if find "/home/app/wireguarddashboard/app/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestErrLog=$(find /home/app/wireguarddashboard/app/log -name "error_*.log" | head -n 1)
    latestAccLog=$(find /home/app/wireguarddashboard/app/log -name "access_*.log" | head -n 1)
    tail -f "${latestErrLog}" "${latestAccLog}"
  fi

  # Blocking command in case of erroring. So the container does not quit.
  sleep infinity
}

# Execute functions for the WireGuard Dashboard services, then set the environment variables
clean_up

chmod u+x /home/app/wgd.sh
if [ ! -f "/home/app/wg-dashboard.ini" ]; then
  /home/app/wgd.sh install
  
fi
/home/app/wgd.sh start
ensure_blocking
