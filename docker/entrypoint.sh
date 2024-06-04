echo "\nStarting the WireGuard Dashboard."

# Cleaning out previous data such as the .pid file.
rm /opt/wireguardashboard/app/src/gunicorn.pid

# Starting the WireGuard Dashboard Web-UI.
. ${WGDASH}/venv/bin/activate
cd ${WGDASH}/app/src
bash ./wgd.sh start

if [ "$tz" != "Europe/Amsterdam" ]; then
  echo "Changing timezone..."
  ln -sf /usr/share/zoneinfo/$tz /etc/localtime
fi

if [ "$global_dns" != "1.1.1.1" ]; then # Changing the DNS used for clients. Had to change it in 2 locations.
  echo "Changing default dns..."
  sed -i 's/^DNS = .*/DNS = ${global_dns}/' /etc/wireguard/wg0.conf
  sed -i "s/^peer_global_dns = .*/peer_global_dns = $global_dns/" /opt/wireguardashboard/app/src/wg-dashboard.ini
fi

if [ "$public_ip" != "0.0.0.0" ]; then # Setting the public IP of the WireGuard Dashboard container host. If not defined, it will be tried using ifconfig.me.
  sed -i "s/^remote_endpoint = .*/remote_endpoint = $public_ip/" /opt/wireguardashboard/app/src/wg-dashboard.ini
else
  sed -i "s/^remote_endpoint = .*/remote_endpoint = $(curl ifconfig.me)/" /opt/wireguardashboard/app/src/wg-dashboard.ini
fi

sleep 3s
tail -f $(ls -t /opt/wireguardashboard/app/src/log/error_*.log | head -n 1)

# Blocking command in case of erroring.
sleep infinity