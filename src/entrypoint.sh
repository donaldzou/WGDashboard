#!/bin/bash

# Trap the SIGTERM signal and call the stop_service function
trap 'stop_service' SIGTERM

echo "Starting the WireGuard Dashboard Docker container."

stop_service() {
  echo "SIGTERM received. Stopping WireGuard Dashboard."
  ./wgd.sh stop
  exit 0
}

clean_up() {
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

  if find "/opt/wireguarddashboard/src/log" -mindepth 1 -maxdepth 1 -type f | read -r; then
    latestErrLog=$(find /opt/wireguarddashboard/src/log -name "error_*.log" | head -n 1)
    latestAccLog=$(find /opt/wireguarddashboard/src/log -name "access_*.log" | head -n 1)
    tail -f "${latestErrLog}" "${latestAccLog}" &
  fi

  wait
}

{ date; clean_up; printf "\n\n"; } >> ./log/install.txt

chmod u+x /opt/wireguarddashboard/src/wgd.sh
/opt/wireguarddashboard/src/wgd.sh install
/opt/wireguarddashboard/src/wgd.sh docker_start &

SERVICE_PID=$!
ensure_blocking
