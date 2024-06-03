#!/bin/bash

# if [ -z "$(ls -A /etc/wireguard)" ]; then
#   mv /wg0.conf /etc/wireguard
#   echo "Moved conf file to /etc/wireguard"
# else
#   rm wg0.conf
#   echo "Removed unneeded conf file"
# fi

# if they choose to run old
if [[ ${DASHBOARD_VERSON^^} == "NEW" ]] ; then
  echo "Using newer dashboard"
  cp dashboard.py dashboard_old.py
  cp dashboard_new.py dashboard.py
else
  echo "Defaulting to old dashboard"
  if ! $(cp dashboard_old.py dashboard.py 2>/dev/null) ; then
    echo "No dashboard_old.py file, assuming dashboard.py version is old"
  fi
fi

# wg-quick up wg0
chmod u+x /opt/wgdashboard/wgd.sh
if [ ! -f "/opt/wgdashboard/wg-dashboard.ini" ]; then
  /opt/wgdashboard/wgd.sh install
fi
/opt/wgdashboard/wgd.sh debug