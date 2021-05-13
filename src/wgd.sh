#!/bin/bash

app_name="dashboard.py"
dashes='------------------------------------------------------------'
help () {
  printf "<Wireguard Dashboard> by Donald Zou - https://github.com/donaldzou \n"
  printf "Usage: sh wgd.sh <option>"
  printf "\n \n"
  printf "Available options: \n"
  printf "    start: To start Wireguard Dashboard.\n"
  printf "    stop: To stop Wireguard Dashboard.\n"
  printf "    debug: To start Wireguard Dashboard in debug mode (i.e run in foreground).\n"
  printf "    update: To update Wireguard Dashboard to the newest version from GitHub.\n"
  printf "Thank you for using this dashboard! Your support is my motivation ;) \n"
  printf "\n"
}

check_wgd_status(){
  if ps aux | grep '[p]ython3 '$app_name > /dev/null;
    then
      return 0
      else
        return 1
  fi
}

start_wgd () {
    printf "%s" "$PLATFORM"
    printf "Starting Wireguard Dashboard in the background. \n"
    if [ ! -d "log" ]
      then mkdir "log"
    fi
    d=$(date '+%Y%m%d%H%M%S')
    python3 "$app_name" > log/"$d".txt 2>&1 &
    printf "Log file: log/%s""$d"".txt\n"
}

stop_wgd() {
  kill "$(ps aux | grep "[p]ython3 $app_name" | awk '{print $2}')"
}

start_wgd_debug() {
  printf "Starting Wireguard Dashboard in the foreground. \n"
  python3 "$app_name"
}

update_wgd() {
  new_ver=$(python3 -c "import json; import urllib.request; data = urllib.request.urlopen('https://api.github.com/repos/donaldzou/wireguard-dashboard/releases').read(); output = json.loads(data);print(output[0]['tag_name'])")
  printf "%s\n" "$dashes"
  printf "Are you sure you want to update to the %s? (Y/N): " "$new_ver"
  read up
  if [ "$up" = "Y" ]; then
    printf "| Shutting down Wireguard Dashboard...                     |\n"
    printf "| Downloading %s from GitHub...                            |\n" "$new_ver"
    git pull https://github.com/donaldzou/wireguard-dashboard.git $new_ver --force >  /dev/null 2>&1
    printf "| Installing all required python package                   |\n"
    python3 -m pip install -r requirements.txt
    printf "| Update Successfully!                                     |\n"
    printf "| Now you can start the dashboard with >> sh wgd.sh start  |\n"
    exit 1
  else
    printf "Cancel update. \n"
  fi
}


if [ "$#" != 1 ];
  then
    help
  else
    if [ "$1" = "start" ]; then
        if check_wgd_status; then
          printf "Wireguard Dashboard is already running. \n"
          else
            start_wgd
        fi
      elif [ "$1" = "stop" ]; then
        if check_wgd_status; then
            stop_wgd
            printf "Wireguard Dashboard is stopped. \n"
            else
              printf "Wireguard Dashboard is not running. \n"
        fi
      elif [ "$1" = "update" ]; then
        update_wgd
      elif [ "$1" = "restart" ]; then
         if check_wgd_status; then
           stop_wgd
           sleep 2
           printf "Wireguard Dashboard is stopped. \n"
           start_wgd_debug
        else
          start_wgd_debug
        fi
      elif [ "$1" = "debug" ]; then
        if check_wgd_status; then
          printf "Wireguard Dashboard is already running. \n"
          else
            start_wgd_debug
        fi
      else
        help
    fi
fi

