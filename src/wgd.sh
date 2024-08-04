#!/bin/bash

# wgd.sh - Copyright(C) 2024 Donald Zou [https://github.com/donaldzou]
# Under Apache-2.0 License
app_name="dashboard.py"
app_official_name="WGDashboard"
venv_python="./venv/bin/python3"
venv_gunicorn="./venv/bin/gunicorn"

PID_FILE=./gunicorn.pid
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
helpMsg="[WGDashboard] Please check ./log/install.txt for more details. For further assistance, please open a ticket on https://github.com/donaldzou/WGDashboard/issues/new/choose, I'm more than happy to help :)"
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

_check_and_set_venv(){
    VIRTUAL_ENV="./venv"
    if [ ! -d $VIRTUAL_ENV ]; then
    	printf "[WGDashboard] Creating Python Virtual Environment under ./venv\n"
        { python3 -m venv $VIRTUAL_ENV; } >> ./log/install.txt
    fi
    printf "[WGDashboard] Activate Python Virtual Environment under ./venv\n"
    . ${VIRTUAL_ENV}/bin/activate
}

_determineOS(){
  if [ -f /etc/os-release ]; then
      . /etc/os-release
      OS=$ID
  elif [ -f /etc/redhat-release ]; then
      OS="redhat"
#  elif [ -f /etc/arch-release ]; then
#      OS="arch"
  else
      printf "[WGDashboard] Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based OS."
      printf "%s\n" "$helpMsg"
      exit 1
  fi
}

_installPython(){
	case "$OS" in
		ubuntu|debian)
			{ sudo apt update ; sudo apt-get install -y python3; printf "\n\n"; } &>> ./log/install.txt 
		;;
		centos|fedora|redhat)
			if command -v dnf &> /dev/null; then
				{ sudo dnf install -y python3; printf "\n\n"; } >> ./log/install.txt
			else
				{ sudo yum install -y python3; printf "\n\n"; } >> ./log/install.txt
			fi
		;;
#		arch)
#			{ sudo pacman -Sy python python-pip; printf "\n\n"; } >> ./log/install.txt
#		;;
#		*)
#        	printf "[WGDashboard] Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based and Arch-based OS."
#        	printf "%s" "$helpMsg"
#        	exit 1
#        ;;
	esac
	
	if ! python3 --version > /dev/null 2>&1
	then
		printf "[WGDashboard] Python is still not installed, halting script now.\n"
		printf "%s\n" "$helpMsg"
		exit 1
	else
		printf "[WGDashboard] \xE2\x9C\x94 Python is installed\n"
	fi
}

_installPythonVenv(){
	case "$OS" in
		ubuntu|debian)
			{ sudo apt update ; sudo apt-get install -y python3-venv; printf "\n\n"; } &>> ./log/install.txt 
		;;
		centos|fedora|redhat)
			if command -v dnf &> /dev/null; then
				{ sudo dnf install -y python3-virtualenv; printf "\n\n"; } >> ./log/install.txt
			else
				{ sudo yum install -y python3-virtualenv; printf "\n\n"; } >> ./log/install.txt
			fi
		;;
		*)
        	printf "[WGDashboard] Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based OS."
        	printf "%s\n" "$helpMsg"
        	exit 1
        ;;
	esac
	
	if ! python3 -m venv -h > /dev/null 2>&1
	then
		printf "[WGDashboard] Python Virtual Environment is still not installed, halting script now.\n"
		printf "%s\n" "$helpMsg"
	else
		printf "[WGDashboard] \xE2\x9C\x94 Python Virtual Environment is installed\n"
	fi
}

_installPythonPip(){
	case "$OS" in
    		ubuntu|debian)
    			{ sudo apt update ; sudo apt-get install -y python3-pip; printf "\n\n"; } &>> ./log/install.txt 
    		;;
    		centos|fedora|redhat)
    			if command -v dnf &> /dev/null; then
    				{ sudo dnf install -y python3-pip; printf "\n\n"; } >> ./log/install.txt
    			else
    				{ sudo yum install -y python3-pip printf "\n\n"; } >> ./log/install.txt
    			fi
    		;;
    		*)
            	printf "[WGDashboard] Sorry, your OS is not support auto install. Currently the install script only support Debian-based, Red Hat-based OS."
            	printf "%s\n" "$helpMsg"
            	exit 1
            ;;
    	esac
    	
    	if ! python3 -m pip -h > /dev/null 2>&1
    	then
    		printf "[WGDashboard] Python Package Manager (PIP) is still not installed, halting script now.\n"
    		printf "%s\n" "$helpMsg"
    	else
    		printf "[WGDashboard] \xE2\x9C\x94 Python Package Manager (PIP) is installed\n"
    	fi
}

_checkWireguard(){
	if ! wg -h > /dev/null 2>&1
	then
		printf "[WGDashboard] WireGuard is not installed. Please follow instruction on https://www.wireguard.com/install/ to install. \n"
		exit 1
	fi
	if ! wg-quick -h > /dev/null 2>&1
	then
		printf "[WGDashboard] WireGuard is not installed. Please follow instruction on https://www.wireguard.com/install/ to install. \n"
		exit 1
	fi
}

install_wgd(){
    printf "[WGDashboard] Starting to install WGDashboard\n"
    _checkWireguard
    sudo chmod -R 755 /etc/wireguard/
    
    if [ ! -d "log" ]
	  then 
		printf "[WGDashboard] Creating ./log folder\n"
		mkdir "log"
	fi
    _determineOS
    if ! python3 --version > /dev/null 2>&1
    then
    	printf "[WGDashboard] Python is not installed, trying to install now\n"
    	_installPython
    else
    	printf "[WGDashboard] \xE2\x9C\x94 Python is installed\n"
    fi
    _installPythonVenv
    _installPythonPip

    
    version_pass=$(python3 -c 'import sys; print("1") if (sys.version_info.major == 3 and sys.version_info.minor >= 10) else print("0");')
    if [ $version_pass == "0" ]
      then 
        printf "[WGDashboard] WGDashboard required Python 3.7 or above\n"
        exit 1
    fi

    if [ ! -d "db" ] 
      then 
        printf "[WGDashboard] Creating ./db folder\n"
        mkdir "db"
    fi
    _check_and_set_venv
    printf "[WGDashboard] Upgrading Python Package Manage (PIP)\n"
    { date; python3 -m pip install pip; printf "\n\n"; } >> ./log/install.txt
    printf "[WGDashboard] Installing latest Python dependencies\n"
    { date; python3 -m pip install -r requirements.txt ; printf "\n\n"; } >> ./log/install.txt
    printf "[WGDashboard] WGDashboard installed successfully!\n"
    printf "[WGDashboard] Enter ./wgd.sh start to start the dashboard\n"
}

check_wgd_status(){
  if test -f "$PID_FILE"; then
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
  printf "%s\n" "$dashes"
  printf "[WGDashboard] Starting WGDashboard with Gunicorn in the background.\n"
  d=$(date '+%Y%m%d%H%M%S')
  if [[ $USER == root ]]; then
    export PATH=$PATH:/usr/local/bin:$HOME/.local/bin
  fi
  _check_and_set_venv
  sudo "$venv_gunicorn" --access-logfile log/access_"$d".log \
  --log-level 'debug' --capture-output \
  --error-logfile log/error_"$d".log 'dashboard:app'
  printf "[WGDashboard] Log files is under ./log\n"
  printf "%s\n" "$dashes"
}

gunicorn_stop () {
  sudo kill $(cat ./gunicorn.pid)
}

start_wgd () {
	_checkWireguard
    gunicorn_start
}

stop_wgd() {
  if test -f "$PID_FILE"; then
    gunicorn_stop
  else
    kill "$(ps aux | grep "[p]ython3 $app_name" | awk '{print $2}')"
  fi
}

start_wgd_debug() {
  printf "%s\n" "$dashes"
  _checkWireguard
  printf "[WGDashboard] Starting WGDashboard in the foreground.\n"
  sudo "$venv_python" "$app_name"
  printf "%s\n" "$dashes"
}

update_wgd() {
  new_ver=$(python3 -c "import json; import urllib.request; data = urllib.request.urlopen('https://api.github.com/repos/donaldzou/WGDashboard/releases/latest').read(); output = json.loads(data);print(output['tag_name'])")
  printf "%s\n" "$dashes"
  printf "[WGDashboard] Are you sure you want to update to the %s? (Y/N): " "$new_ver"
  read up
  if [ "$up" = "Y" ] || [ "$up" = "y" ]; then
    printf "[WGDashboard] Shutting down WGDashboard\n"
    if check_wgd_status; then
      stop_wgd
    fi
    mv wgd.sh wgd.sh.old
    printf "[WGDashboard] Downloading %s from GitHub..." "$new_ver"
    { date; git stash; git pull https://github.com/donaldzou/WGDashboard.git $new_ver --force; } >> ./log/update.txt
    chmod +x ./wgd.sh
    sudo ./wgd.sh install
    printf "[WGDashboard] Update completed!\n"
    printf "%s\n" "$dashes"
    rm wgd.sh.old
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
          printf "[WGDashboard] WGDashboard is already running.\n"
          printf "%s\n" "$dashes"
          else
            start_wgd
        fi
      elif [ "$1" = "stop" ]; then
        if check_wgd_status; then
            printf "%s\n" "$dashes"
            stop_wgd
            printf "[WGDashboard] WGDashboard is stopped.\n"
            printf "%s\n" "$dashes"
            else
              printf "%s\n" "$dashes"
              printf "[WGDashboard] WGDashboard is not running.\n"
              printf "%s\n" "$dashes"
        fi
      elif [ "$1" = "update" ]; then
        update_wgd
      elif [ "$1" = "install" ]; then
        printf "%s\n" "$dashes"
        install_wgd
        printf "%s\n" "$dashes"
      elif [ "$1" = "restart" ]; then
         if check_wgd_status; then
           printf "%s\n" "$dashes"
           stop_wgd
           printf "| WGDashboard is stopped.                                  |\n"
           sleep 4
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
