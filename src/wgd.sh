#!/bin/bash

# wgd.sh - Copyright(C) 2024 Donald Zou [https://github.com/donaldzou]
# Under Apache-2.0 License
#trap "kill $TOP_PID"
export TOP_PID=$$

app_name="dashboard.py"
app_official_name="WGDashboard"
venv_python="./venv/bin/python3"
venv_gunicorn="./venv/bin/gunicorn"
pythonExecutable="python3"

heavy_checkmark=$(printf "\xE2\x9C\x94")
heavy_crossmark=$(printf "\xE2\x9C\x97")

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
        { $pythonExecutable -m venv $VIRTUAL_ENV; } >> ./log/install.txt
    fi
    
    if ! $venv_python --version > /dev/null 2>&1
    then
    	printf "[WGDashboard] %s Python Virtual Environment under ./venv failed to create. Halting now.\n" "$heavy_crossmark"	
    	kill  $TOP_PID
    fi
    
    . ${VIRTUAL_ENV}/bin/activate
}

_determineOS(){
  if [ -f /etc/os-release ]; then
      . /etc/os-release
      OS=$ID
  elif [ -f /etc/redhat-release ]; then
      OS="redhat"
  else
      printf "[WGDashboard] %s Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based OS." "$heavy_crossmark"
      printf "%s\n" "$helpMsg"
      kill  $TOP_PID
  fi
   printf "[WGDashboard] OS: %s\n" "$OS"
}

_installPython(){
	case "$OS" in
		ubuntu|debian)
			{ sudo apt update ; sudo apt-get install -y python3 net-tools; printf "\n\n"; } &>> ./log/install.txt 
		;;
		centos|fedora|redhat|rehl)
			if command -v dnf &> /dev/null; then
				{ sudo dnf install -y python3 net-tools; printf "\n\n"; } >> ./log/install.txt
			else
				{ sudo yum install -y python3 net-tools ; printf "\n\n"; } >> ./log/install.txt
			fi
		;;
		alpine)
			{ apk update; apk add python3 net-tools; printf "\n\n"; } &>> ./log/install.txt 
		;;
	esac
	
	if ! python3 --version > /dev/null 2>&1
	then
		printf "[WGDashboard] %s Python is still not installed, halting script now.\n" "$heavy_crossmark"
		printf "%s\n" "$helpMsg"
		kill  $TOP_PID
	else
		printf "[WGDashboard] %s Python is installed\n" "$heavy_checkmark"
	fi
}

_installPythonVenv(){
	if [ "$pythonExecutable" = "python3" ]; then
		case "$OS" in
			ubuntu|debian)
				{ sudo apt update ; sudo apt-get install -y python3-venv; printf "\n\n"; } &>> ./log/install.txt
			;;
			centos|fedora|redhat|rhel)
				if command -v dnf &> /dev/null; then
					{ sudo dnf install -y python3-virtualenv; printf "\n\n"; } >> ./log/install.txt
				else
					{ sudo yum install -y python3-virtualenv; printf "\n\n"; } >> ./log/install.txt
				fi
			;;
			alpine)
				{ apk add python3 py3-virtualenv; printf "\n\n"; } &>> ./log/install.txt 
			;;
			*)
				printf "[WGDashboard] %s Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based OS.\n" "$heavy_crossmark"
				printf "%s\n" "$helpMsg"
				kill  $TOP_PID
			;;
		esac
	else
		case "$OS" in
			ubuntu|debian)
				{ sudo apt-get update; sudo apt-get install ${pythonExecutable}-venv;  } &>> ./log/install.txt
			;;
		esac
	fi
	
	if ! $pythonExecutable -m venv -h > /dev/null 2>&1
	then
		printf "[WGDashboard] %s Python Virtual Environment is still not installed, halting script now.\n" "$heavy_crossmark"
		printf "%s\n" "$helpMsg"
	else
		printf "[WGDashboard] %s Python Virtual Environment is installed\n" "$heavy_checkmark"
	fi
}

_installPythonPip(){
	
	if ! $pythonExecutable -m pip -h > /dev/null 2>&1
	then
		case "$OS" in
			ubuntu|debian)
				if [ "$pythonExecutable" = "python3" ]; then
					{ sudo apt update ; sudo apt-get install -y python3-pip; printf "\n\n"; } &>> ./log/install.txt
				else
					{ sudo apt update ; sudo apt-get install -y ${pythonExecutable}-distutil python3-pip; printf "\n\n"; } &>> ./log/install.txt
				fi
			;;
			centos|fedora|redhat|rhel)
				if [ "$pythonExecutable" = "python3" ]; then
					{ sudo dnf install -y python3-pip; printf "\n\n"; } >> ./log/install.txt
				else
					{ sudo dnf install -y ${pythonExecutable}-pip; printf "\n\n"; } >> ./log/install.txt
				fi
			;;
			alpine)
				{ apk add py3-pip; printf "\n\n"; } &>> ./log/install.txt 
			;;
			*)
				printf "[WGDashboard] %s Sorry, your OS is not supported. Currently the install script only support Debian-based, Red Hat-based OS.\n" "$heavy_crossmark"
				printf "%s\n" "$helpMsg"
				kill  $TOP_PID
			;;
		esac
    fi
    	
	if ! $pythonExecutable -m pip -h > /dev/null 2>&1
	then
		printf "[WGDashboard] %s Python Package Manager (PIP) is still not installed, halting script now.\n" "$heavy_crossmark"
		printf "%s\n" "$helpMsg"
		kill  $TOP_PID
	else
		printf "[WGDashboard] %s Python Package Manager (PIP) is installed\n" "$heavy_checkmark"
	fi
}

_checkWireguard(){
	if ! wg -h > /dev/null 2>&1
	then
		printf "[WGDashboard] %s WireGuard is not installed. Please follow instruction on https://www.wireguard.com/install/ to install. \n" "$heavy_crossmark"
		kill  $TOP_PID
	fi
	if ! wg-quick -h > /dev/null 2>&1
	then
		printf "[WGDashboard] %s WireGuard is not installed. Please follow instruction on https://www.wireguard.com/install/ to install. \n" "$heavy_crossmark"
		kill  $TOP_PID
	fi
}



_checkPythonVersion(){
	version_pass=$($pythonExecutable -c 'import sys; print("1") if (sys.version_info.major == 3 and sys.version_info.minor >= 10) else print("0");')
	version=$($pythonExecutable --version)
	if [ $version_pass == "1" ]
	  	then 
			return;
	elif python3.10 --version > /dev/null 2>&1
		then
	 		printf "[WGDashboard] %s Found Python 3.10. Will be using [python3.10] to install WGDashboard.\n" "$heavy_checkmark"
	 		pythonExecutable="python3.10"
	elif python3.11 --version > /dev/null 2>&1
    	 then
    	 	printf "[WGDashboard] %s Found Python 3.11. Will be using [python3.11] to install WGDashboard.\n" "$heavy_checkmark"
    	 	pythonExecutable="python3.11"
    elif python3.12 --version > /dev/null 2>&1
    	 then
    	 	printf "[WGDashboard] %s Found Python 3.12. Will be using [python3.12] to install WGDashboard.\n" "$heavy_checkmark"
    	 	pythonExecutable="python3.12"
	else
		printf "[WGDashboard] %s Could not find a compatible version of Python. Current Python is %s.\n" "$heavy_crossmark" "$version"
		printf "[WGDashboard] WGDashboard required Python 3.10, 3.11 or 3.12. Halting install now.\n"
		kill $TOP_PID
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
    	printf "[WGDashboard] %s Python is installed\n" "$heavy_checkmark"
    fi
    
    _checkPythonVersion
    _installPythonVenv
    _installPythonPip

    if [ ! -d "db" ] 
		then 
			printf "[WGDashboard] Creating ./db folder\n"
			mkdir "db"
    fi
    _check_and_set_venv
    printf "[WGDashboard] Upgrading Python Package Manage (PIP)\n"
	{ date; python3 -m ensurepip --upgrade; printf "\n\n"; } >> ./log/install.txt
    { date; python3 -m pip install --upgrade pip; printf "\n\n"; } >> ./log/install.txt
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
  sudo "$venv_gunicorn" --config ./gunicorn.conf.py
  sleep 5
  checkPIDExist=0
  while [ $checkPIDExist -eq 0 ]
  do
  		if test -f './gunicorn.pid'; then
  			checkPIDExist=1
  			printf "[WGDashboard] Checking if WGDashboard w/ Gunicorn started successfully\n"
  		fi
  		sleep 2
  done
  printf "[WGDashboard] WGDashboard w/ Gunicorn started successfully\n"
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

startwgd_docker() {
	_checkWireguard
	printf "[WGDashboard][Docker] WireGuard configuration started\n"
	{ date; start_core ; printf "\n\n"; } >> ./log/install.txt
    gunicorn_start
}

start_core() {
	local iptable_dir="/opt/wireguarddashboard/src/iptable-rules"
	# Check if wg0.conf exists in /etc/wireguard
	if [[ ! -f /etc/wireguard/wg0.conf ]]; then
		echo "[WGDashboard][Docker] wg0.conf not found. Running generate configuration."
		newconf_wgd
	else
		echo "[WGDashboard][Docker] wg0.conf already exists. Skipping WireGuard configuration generation."
	fi
	# Re-assign config_files to ensure it includes any newly created configurations
	local config_files=$(find /etc/wireguard -type f -name "*.conf")
	
	# Set file permissions
	find /etc/wireguard -type f -name "*.conf" -exec chmod 600 {} \;
	find "$iptable_dir" -type f -name "*.sh" -exec chmod +x {} \;
	
	# Start WireGuard for each config file
	for file in $config_files; do
		config_name=$(basename "$file" ".conf")
		wg-quick up "$config_name"
	done
}



newconf_wgd() {
    local wg_port_listen=$wg_port
    local wg_addr_range=$wg_net
    private_key=$(wg genkey)
    public_key=$(echo "$private_key" | wg pubkey)
    cat <<EOF >"/etc/wireguard/wg0.conf"
[Interface]
PrivateKey = $private_key
Address = $wg_addr_range
ListenPort = $wg_port_listen
SaveConfig = true
PostUp = /opt/wireguarddashboard/src/iptable-rules/postup.sh
PreDown = /opt/wireguarddashboard/src/iptable-rules/postdown.sh
EOF
}

start_wgd_debug() {
	printf "%s\n" "$dashes"
	_checkWireguard
	printf "[WGDashboard] Starting WGDashboard in the foreground.\n"
	sudo "$venv_python" "$app_name"
	printf "%s\n" "$dashes"
}

update_wgd() {
	_determineOS
	if ! python3 --version > /dev/null 2>&1
	then
		printf "[WGDashboard] Python is not installed, trying to install now\n"
		_installPython
	else
		printf "[WGDashboard] %s Python is installed\n" "$heavy_checkmark"
	fi
	
	_checkPythonVersion
	_installPythonVenv
	_installPythonPip	
	
	new_ver=$($venv_python -c "import json; import urllib.request; data = urllib.request.urlopen('https://api.github.com/repos/donaldzou/WGDashboard/releases/latest').read(); output = json.loads(data);print(output['tag_name'])")
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
		printf "[WGDashboard] Update Canceled.\n"
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
			elif [ "$1" = "docker_start" ]; then
				printf "%s\n" "$dashes"
				startwgd_docker
				printf "%s\n" "$dashes"
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
					printf "[WGDashboard] WGDashboard is stopped.\n"
					sleep 4
					start_wgd
				else
					start_wgd
				fi
			elif [ "$1" = "debug" ]; then
				if check_wgd_status; then
					printf "[WGDashboard] WGDashboard is already running.\n"
				else
					start_wgd_debug
				fi
			else
				help
		fi
fi