#!/bin/bash

app_name="dashboard.py"
app_official_name="WGDashboard"
environment=$(if [[ $ENVIRONMENT ]]; then echo $ENVIRONMENT; else echo 'develop'; fi)
if [[ $CONFIGURATION_PATH ]]; then
  cb_work_dir=$CONFIGURATION_PATH/letsencrypt/work-dir
  cb_config_dir=$CONFIGURATION_PATH/letsencrypt/config-dir
else
  cb_work_dir=/etc/letsencrypt
  cb_config_dir=/var/lib/letsencrypt
fi

dashes='------------------------------------------------------------'
equals='============================================================'
help () {
  printf "=================================================================================\n"
  printf "+          <WGDashboard> by Donald Zou - https://github.com/donaldzou           +\n"
  printf "=================================================================================\n"
  printf "| Usage: ./wgd.sh <option>                                                      |\n"
  printf "|                                                                               |\n"
  printf "| Available options:                                                            |\n"
  printf "|    start: To start WGDashboard.                                               |\n"
  printf "|    stop: To stop WGDashboard.                                                 |\n"
  printf "|    debug: To start WGDashboard in debug mode (i.e run in foreground).         |\n"
  printf "|    update: To update WGDashboard to the newest version from GitHub.           |\n"
  printf "|    install: To install WGDashboard.                                           |\n"
  printf "| Thank you for using! Your support is my motivation ;)                         |\n"
  printf "=================================================================================\n"
}

install_wgd(){
    # Check Python3 version
    version_pass=$(python3 -c 'import sys; print("1") if (sys.version_info.major == 3 and sys.version_info.minor >= 7) else print("0");')
    if [ $version_pass == "0" ]
      then printf "| WGDashboard required Python3.7+                  |\n"
      printf "%s\n" "$dashes"
      exit 1
    fi
    rm db/hi.txt >  /dev/null 2>&1
    if [ ! -d "log" ]
      then mkdir "log"
    fi
    printf "| Installing latest Python dependencies                    |\n"
    python3 -m pip install -r requirements.txt >  /dev/null 2>&1
    printf "| WGDashboard installed successfully!              |\n"
    printf "| Starting Dashboard                                       |\n"
    start_wgd
}


check_wgd_status(){
  if [[ $environment == 'production' ]]; then
    if ps aux | grep -v grep | grep $(cat ./gunicorn.pid)  > /dev/null; then
      return 0
    else
      return 1
    fi
  else
    if ps aux | grep -v grep | grep '[p]ython3 '$app_name > /dev/null; then
      return 0
    else
      return 1
    fi
  fi
}

certbot_create_ssl () {
  certbot certonly --config ./certbot.ini --email "$EMAIL" --work-dir $cb_work_dir --config-dir $cb_config_dir --domain "$SERVERURL"
}

certbot_renew_ssl () {
  certbot renew --work-dir $cb_work_dir --config-dir $cb_config_dir
}

gunicorn_start () {
  if [[ $SSL ]]; then
    if [ ! -d $cb_config_dir ]; then
      certbot_create_ssl
    else
      certbot_renew_ssl
    fi
  fi
  printf "%s\n" "$dashes"
  printf "| Starting WGDashboard in the background.          |\n"
  if [ ! -d "log" ]; then
    mkdir "log"
  fi
  d=$(date '+%Y%m%d%H%M%S')
  if [[ $USER == root ]]; then
    export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
  fi
  if [[ $SSL ]]; then
    gunicorn --certfile $cb_config_dir/live/"$SERVERURL"/cert.pem \
    --keyfile $cb_config_dir/live/"$SERVERURL"/privkey.pem \
    --access-logfile log/access_"$d".log \
    --error-logfile log/error_"$d".log 'dashboard:run_dashboard()'
  else
    gunicorn --access-logfile log/access_"$d".log \
    --error-logfile log/error_"$d".log 'dashboard:run_dashboard()'
  fi
  printf "| Log files is under log/                                  |\n"
  printf "%s\n" "$dashes"
}

gunicorn_stop () {
  kill $(cat ./gunicorn.pid)
}

start_wgd () {
    if [[ $environment == 'production' ]]; then
      gunicorn_start
    else
      printf "%s\n" "$dashes"
      printf "| Starting WGDashboard in the background.          |\n"
      if [ ! -d "log" ]
        then mkdir "log"
      fi
      d=$(date '+%Y%m%d%H%M%S')
      python3 "$app_name" > log/"$d".txt 2>&1 &
      printf "| Log files is under log/                                  |\n"
      printf "%s\n" "$dashes"
    fi
}

stop_wgd() {
  if [[ $environment == 'production' ]]; then
    gunicorn_stop
  else
    kill "$(ps aux | grep "[p]ython3 $app_name" | awk '{print $2}')"
  fi
}

start_wgd_debug() {
  printf "%s\n" "$dashes"
  printf "| Starting WGDashboard in the foreground.                  |\n"
  python3 "$app_name"
  printf "%s\n" "$dashes"
}

update_wgd() {
  new_ver=$(python3 -c "import json; import urllib.request; data = urllib.request.urlopen('https://api.github.com/repos/donaldzou/WGDashboard/releases/latest').read(); output = json.loads(data);print(output['tag_name'])")
  printf "%s\n" "$dashes"
  printf "| Are you sure you want to update to the %s? (Y/N): " "$new_ver"
  read up
  if [ "$up" = "Y" ]; then
    printf "| Shutting down WGDashboard...                             |\n"
    kill "$(ps aux | grep "[p]ython3 $app_name" | awk '{print $2}')"
    printf "| Downloading %s from GitHub...                            |\n" "$new_ver"
    git stash > /dev/null 2>&1
    git pull https://github.com/donaldzou/wireguard-dashboard.git $new_ver --force >  /dev/null 2>&1
    printf "| Installing latest Python dependencies                    |\n"
    python3 -m pip install -r requirements.txt >  /dev/null 2>&1
    printf "| Update Successfully!                                     |\n"
    start_wgd
  else
    printf "%s\n" "$dashes"
    printf "| Update Canceled.                                         |\n"
    printf "%s\n" "$dashes"
  fi
}


if [ "$#" != 1 ];
  then
    help
  else
    if [ "$1" = "start" ]; then
        if check_wgd_status; then
          printf "%s\n" "$dashes"
          printf "| WGDashboard is already running.                          |\n"
          printf "%s\n" "$dashes"
          else
            start_wgd
        fi
      elif [ "$1" = "stop" ]; then
        if check_wgd_status; then
            printf "%s\n" "$dashes"
            stop_wgd
            printf "| WGDashboard is stopped.                                  |\n"
            printf "%s\n" "$dashes"
            else
              printf "%s\n" "$dashes"
              printf "| WGDashboard is not running.                              |\n"
              printf "%s\n" "$dashes"
        fi
      elif [ "$1" = "update" ]; then
        update_wgd
      elif [ "$1" = "install" ]; then
        install_wgd
      elif [ "$1" = "restart" ]; then
         if check_wgd_status; then
           printf "%s\n" "$dashes"
           stop_wgd
           printf "| WGDashboard is stopped.                                  |\n"
           sleep 2
           start_wgd
        else
          start_wgd
        fi
      elif [ "$1" = "debug" ]; then
        if check_wgd_status; then
          printf "| WGDashboard is already running.                          |\n"
          else
            start_wgd_debug
        fi
      else
        help
    fi
fi

