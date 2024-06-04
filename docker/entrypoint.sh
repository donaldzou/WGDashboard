echo "Starting the WireGuard Dashboard."

outgoing=$(ip -o -4 route show to default | awk '{print $NF}')
echo $outgoing

. ${WGDASH}/venv/bin/activate
cd /opt/wireguardashboard/app/src
bash ./wgd.sh start

if [ "$tz" != "Europe/Amsterdam" ]; then
  echo "Changing timezone..."
  ln -sf /usr/share/zoneinfo/$tz /etc/localtime
fi

sleep 3s
tail -f /opt/wireguardashboard/app/src/log/*.log

# Blocking command in case of erroring.
sleep infinity