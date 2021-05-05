#!/bin/bash

app_name="dashboard.py"

help () {
  printf "<Wireguard Dashboard> by Donald Zou - https://github.com/donaldzou \n"
  printf "Usage: sh wg-dashboard.sh <option>"
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
  git pull
  if check_wgd_status; then
     stop_wgd
     sleep 2
     printf "Wireguard Dashboard is stopped. \n"
     start_wgd_debug
  else
    start_wgd_debug
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

