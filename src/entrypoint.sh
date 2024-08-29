#!/bin/bash

# Trap the SIGTERM signal and call the stop_service function
trap './wgd.sh stop' SIGTERM

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
  if find "/opt/wireguarddashboard/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestErrLog=$(find /opt/wireguarddashboard/src/log -name "error_*.log" | head -n 1)
    latestAccLog=$(find /opt/wireguarddashboard/src/log -name "access_*.log" | head -n 1)
    tail -f "${latestErrLog}" "${latestAccLog}"
  fi

  # Blocking command in case of erroring. So the container does not quit.
  sleep infinity
}

{ date; clean_up; printf "\n\n"; } >> ./log/install.txt

chmod u+x /opt/wireguarddashboard/src/wgd.sh
/opt/wireguarddashboard/src/wgd.sh install
/opt/wireguarddashboard/src/wgd.sh docker_start
ensure_blocking
# Store the PID of the background process
SERVICE_PID=$!

# Wait for the service process to exit
wait $SERVICE_PID