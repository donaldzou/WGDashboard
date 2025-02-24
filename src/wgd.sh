#!/bin/bash
# wgd.sh - Copyright (C) 2024 Donald Zou [https://github.com/donaldzou]
# Under Apache-2.0 License

set -e  # Stop script execution on error

#trap "kill $TOP_PID"
export TOP_PID=$$

APP_SCRIPT="dashboard.py"
APP_NAME="WGDashboard"

VENV_DIR="./venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
VENV_GUNICORN="$VENV_DIR/bin/gunicorn"
PYTHON_EXECUTABLE="python3"

# Emojis for messages
HEAVY_CHECKMARK=$(printf "\xE2\x9C\x85")  # ✔️
HEAVY_CROSSMARK=$(printf "\xE2\x9D\x8C")  # ❌
INSTALL=$(printf "\xF0\x9F\x92\xBF")      # 💾

MSLEEP=15
PID_FILE="./gunicorn.pid"

# Set ENVIRONMENT variable, default to "develop" if not defined
ENVIRONMENT="${ENVIRONMENT:-develop}"

# Define configuration directories, with fallback defaults
CB_WORK_DIR="${CONFIGURATION_PATH:-/etc}/letsencrypt/work-dir"
CB_CONFIG_DIR="${CONFIGURATION_PATH:-/var/lib}/letsencrypt/config-dir"

# Aesthetic separators
DASHES="--------------------------------------------------------------------------------"
EQUALS="================================================================================"

HELP_MSG="[$APP_NAME] Please check ./log/install.txt for details.\n\
For further assistance, open a ticket at:\n\
https://github.com/donaldzou/WGDashboard/issues/new/choose\n\
I'm happy to help! :)"

help() {
  cat <<EOF
$EQUALS
 +         <WGDashboard> by Donald Zou - https://github.com/donaldzou         +
$EQUALS
 | Usage: ./wgd.sh <option>                                                   |
 |                                                                            |
 | Available options:                                                         |
 |    start:    Start WGDashboard.                                            |
 |    stop:     Stop WGDashboard.                                             |
 |    debug:    Start WGDashboard in debug mode (run in foreground).          |
 |    update:   Update WGDashboard to the newest version from GitHub.         |
 |    install:  Install WGDashboard.                                          |
 |                                                                            |
 | Thank you for using! Your support is my motivation! ;)                     |
$EQUALS
EOF
}

# Ensure the Python virtual environment exists
_check_and_set_venv() {
  if [[ ! -d $VENV_DIR ]]; then
    printf "[WGDashboard] %s Creating Python Virtual Environment at %s\n" "$INSTALL" "$VENV_DIR"
    { $PYTHON_EXECUTABLE -m venv "$VENV_DIR"; } >> ./log/install.txt
  fi

  if ! "$VENV_PYTHON" --version &>/dev/null; then
    printf "[WGDashboard] %s Failed to create Python Virtual Environment at %s. Halting.\n" "$HEAVY_CROSSMARK" "$VENV_DIR"
    kill "$TOP_PID"
  fi

  source "$VENV_DIR/bin/activate"
}

# Detect the operating system
_determineOS() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS="$ID"
  elif [[ -f /etc/redhat-release ]]; then
    OS="redhat"
  else
    printf "[WGDashboard] %s Unsupported OS detected.\n" "$HEAVY_CROSSMARK"
    printf "[WGDashboard] This script supports Debian-based, Red Hat-based OS, with experimental support for Alpine Linux.\n"
    printf "%b\n" "$HELP_MSG"
    kill "$TOP_PID"
  fi

  printf "[WGDashboard] OS detected: %s\n" "$OS"
}

_installPython() {
  # Log the start of Python installation
  printf "\n\n[Installing Python] [%s]\n\n" "$(date)" | tee -a ./log/install.txt

  printf "[WGDashboard] %s Installing Python...\n" "$INSTALL"

  case "$OS" in
    ubuntu|debian)
      sudo apt update && sudo apt-get install -y python3 net-tools | tee -a ./log/install.txt
      ;;
    centos|fedora|redhat|rhel|almalinux|rocky)
      PACKAGE_MANAGER=$(command -v dnf || command -v yum)
      sudo "$PACKAGE_MANAGER" install -y python3 net-tools | tee -a ./log/install.txt
      ;;
    alpine)
      sudo apk update && sudo apk add python3 net-tools --no-cache | tee -a ./log/install.txt
      ;;
    arch)
      sudo pacman -Syu python3 net-tools | tee -a ./log/install.txt
      ;;
    *)
      printf "[WGDashboard] %s Unsupported OS for Python installation.\n" "$HEAVY_CROSSMARK"
      exit 1
      ;;
  esac

  # Verify if Python is installed
  if ! command -v python3 &>/dev/null; then
    printf "[WGDashboard] %s Python installation failed! Stopping script.\n" "$HEAVY_CROSSMARK"
    printf "%s\n" "$HELP_MSG"
    kill "$TOP_PID"
  else
    printf "[WGDashboard] %s Python is successfully installed.\n" "$HEAVY_CHECKMARK"
  fi
}

_installPythonVenv() {
  # Log installation start
  printf "\n\n[Installing Python Venv] [%s]\n\n" "$(date)" | tee -a ./log/install.txt
  printf "[WGDashboard] %s Installing Python Virtual Environment...\n" "$INSTALL"

  case "$OS" in
    ubuntu|debian)
      sudo apt update && sudo apt-get install -y python3-venv | tee -a ./log/install.txt
      ;;
    centos|fedora|redhat|rhel|almalinux|rocky)
      PACKAGE_MANAGER=$(command -v dnf || command -v yum)
      sudo "$PACKAGE_MANAGER" install -y python3-virtualenv | tee -a ./log/install.txt
      ;;
    alpine)
      sudo apk update && sudo apk add py3-virtualenv --no-cache | tee -a ./log/install.txt
      ;;
    arch)
      echo "Python Virtual Environment is installed by default from version Python3.3" | tee -a ./log/install.txt # https://wiki.archlinux.org/title/Python/Virtual_environment
      ;;
    *)
      printf "[WGDashboard] %s Unsupported OS detected.\n" "$HEAVY_CROSSMARK"
      printf "[WGDashboard] This script only supports Debian-based, Red Hat-based OS, with experimental support for Alpine Linux.\n"
      printf "%b\n" "$HELP_MSG"
      kill "$TOP_PID"
      ;;
  esac

  # Verify if Python Virtual Environment is installed
  if ! "$PYTHON_EXECUTABLE" -m venv -h &>/dev/null; then
    printf "[WGDashboard] %s Python Virtual Environment installation failed! Stopping script.\n" "$HEAVY_CROSSMARK"
    printf "%s\n" "$HELP_MSG"
    kill "$TOP_PID"
  else
    printf "[WGDashboard] %s Python Virtual Environment is successfully installed.\n" "$HEAVY_CHECKMARK"
  fi
}

_installPythonPip() {
  # Log installation start
  printf "\n\n[Installing Python Pip] [%s]\n\n" "$(date)" | tee -a ./log/install.txt

  # Check if pip is already installed
  if ! "$PYTHON_EXECUTABLE" -m pip -h &>/dev/null; then
    printf "[WGDashboard] %s Installing Python Package Manager (PIP)...\n" "$INSTALL"

    case "$OS" in
      ubuntu|debian)
        sudo apt update

        # Install pip based on the Python version
        if [ "$PYTHON_EXECUTABLE" = "python3" ]; then
          sudo apt-get install -y python3-pip | tee -a ./log/install.txt
        else
          sudo apt-get install -y "${PYTHON_EXECUTABLE}-distutils" python3-pip | tee -a ./log/install.txt
        fi
        ;;
      centos|fedora|redhat|rhel|almalinux|rocky)
        PACKAGE_MANAGER=$(command -v dnf || command -v yum)
        sudo "$PACKAGE_MANAGER" install -y python3-pip | tee -a ./log/install.txt
        ;;
      alpine)
        sudo apk update && sudo apk add py3-pip --no-cache | tee -a ./log/install.txt
        ;;
      arch)
        sudo pacman -Syu python-pip | tee -a ./log/install.txt
        ;;
      *)
        printf "[WGDashboard] %s Unsupported OS detected.\n" "$HEAVY_CROSSMARK"
        printf "[WGDashboard] This script only supports Debian-based, Red Hat-based OS, with experimental support for Alpine Linux.\n"
        printf "%b\n" "$HELP_MSG"
        kill "$TOP_PID"
        ;;
    esac
  fi

  # Verify if pip was successfully installed
  if ! "$PYTHON_EXECUTABLE" -m pip -h &>/dev/null; then
    printf "[WGDashboard] %s Python Package Manager (PIP) installation failed! Stopping script.\n" "$HEAVY_CROSSMARK"
    printf "%s\n" "$HELP_MSG"
    kill "$TOP_PID"
  else
    printf "[WGDashboard] %s Python Package Manager (PIP) is successfully installed.\n" "$HEAVY_CHECKMARK"
  fi
}

_checkWireguard() {
  # Check if WireGuard is installed
  if ! command -v wg &>/dev/null || ! command -v wg-quick &>/dev/null; then
    printf "[WGDashboard] %s Installing WireGuard...\n" "$INSTALL"

    case "$OS" in
      ubuntu|debian)
        sudo apt update && sudo apt-get install -y wireguard | tee -a ./log/install.txt
        ;;
      centos|fedora|redhat|rhel|almalinux|rocky)
        PACKAGE_MANAGER=$(command -v dnf || command -v yum)
        sudo "$PACKAGE_MANAGER" install -y wireguard-tools | tee -a ./log/install.txt
        ;;
      alpine)
        sudo apk update && sudo apk add wireguard-tools --no-cache | tee -a ./log/install.txt
        ;;
      arch)
        sudo pacman -Syu wireguard-tools | tee -a ./log/install.txt
        ;;
      *)
        printf "[WGDashboard] %s Unsupported OS detected.\n" "$HEAVY_CROSSMARK"
        printf "[WGDashboard] This script supports Debian-based, Red Hat-based OS, and Alpine Linux.\n"
        printf "%b\n" "$HELP_MSG"
        kill "$TOP_PID"
        ;;
    esac

    # Confirm WireGuard installation
    if command -v wg &>/dev/null && command -v wg-quick &>/dev/null; then
      printf "[WGDashboard] %s WireGuard is successfully installed on %s.\n" "$HEAVY_CHECKMARK" "$OS"
    else
      printf "[WGDashboard] %s WireGuard installation failed! Stopping script.\n" "$HEAVY_CROSSMARK"
      printf "%s\n" "$HELP_MSG"
      kill "$TOP_PID"
    fi
  else
    printf "[WGDashboard] %s WireGuard is already installed.\n" "$HEAVY_CHECKMARK"
  fi
}

_checkPythonVersion() {
  # Get Python version
  PYTHON_VERSION=$($PYTHON_EXECUTABLE --version 2>/dev/null)
  
  # Check if the current Python version is compatible (>= 3.10)
  version_pass=$($PYTHON_EXECUTABLE -c 'import sys; print(int(sys.version_info >= (3, 10)))')

  if [[ "$version_pass" == "1" ]]; then
    printf "[WGDashboard] %s Found compatible Python version (%s). Using it to install WGDashboard.\n" "$HEAVY_CHECKMARK" "$PYTHON_VERSION"
    return 
  fi

  # Compatible Python versions list
  for ver in 3.12 3.11 3.10; do
    if command -v python$ver &>/dev/null; then
      PYTHON_EXECUTABLE="python$ver"
      printf "[WGDashboard] %s Found Python %s. Using it to install WGDashboard.\n" "$HEAVY_CHECKMARK" "$ver"
      return
    fi
  done

  # If no compatible Python version is found, exit with error
  printf "[WGDashboard] %s No compatible Python version found. Detected: %s\n" "$HEAVY_CROSSMARK" "$PYTHON_VERSION"
  printf "[WGDashboard] WGDashboard requires Python 3.10, 3.11, or 3.12. Halting installation.\n"
  kill "$TOP_PID"
}

_determinePypiMirror(){
	printf "[WGDashboard] %s Pinging list of recommended Python Package Index mirror\n" "$install"
	urls=(
		"https://pypi.org/simple/"
		"https://pypi.tuna.tsinghua.edu.cn/simple/"
		"https://pypi.mirrors.ustc.edu.cn/simple/"
		"https://mirrors.aliyun.com/pypi/simple/"
		"https://pypi.douban.com/simple/"
	)

	# Function to extract hostname and ping it
	index=1
	printf "              ---------------------------------------------------------\n"
	for url in "${urls[@]}"; do
		# Extract the hostname from the URL
		hostname=$(echo "$url" | awk -F/ '{print $3}')
		# Ping the hostname once and extract the RTT
		rtt=$(ping -c 1 -W 1 "$hostname" 2>/dev/null | grep 'time=' | awk -F'time=' '{print $2}' | awk '{print $1}')
		# Handle cases where the hostname is not reachable
		if [ -z "$rtt" ]; then
			rtt="9999"
			printf "              [%i] [FAILED] %s\n" "$index" "$url"
		else
			rtt=${rtt//.*/}
			printf "              [%i] %sms %s\n" "$index" "$rtt" "$url"
		fi
		rtthost[$index]=$rtt
		index=$((index+1))
	done

	for i in "${!rtthost[@]}"; do
		[[ -z ${rtthost[i]} ]] && continue  # Skip unset or empty values
		if [[ -z $min_val || ${rtthost[i]} -lt $min_val ]]; then
			min_val=${rtthost[i]}
			min_idx=$i
		fi
	done
	min_idx=$((min_idx - 1))
	
	printf "\n"
	printf "              Which mirror you would like to use (Hit enter or wait ${msleep} seconds to use default: ${urls[$min_idx]}): "
	read -t ${msleep} -r choice
	printf "\n"

	if [[ -z "$choice" ]]; then
		choice=${min_dix}
	fi

	if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#urls[@]} )); then
		selected_url="${urls[choice-1]}"
		printf "[WGDashboard] %s Will download Python packages from %s\n" "$heavy_checkmark" "$selected_url"
	else
		selected_url="${urls[0]}"
		printf "[WGDashboard] %s Will download Python packages from %s\n" "$heavy_checkmark" "${urls[0]}"
	fi
}

install_wgd(){
    printf "[WGDashboard] Starting to install WGDashboard\n"
    _determineOS
    
	if [ ! -d "log" ] 
	then 
			mkdir "log"
			printf "[WGDashboard] %s Created ./log folder\n" "$heavy_checkmark"
	else
		printf "[WGDashboard] %s Found existing ./log folder\n" "$heavy_checkmark"
	fi
	
	if [ ! -d "download" ]
	then 
		mkdir "download"
		printf "[WGDashboard] %s Created ./download folder\n" "$heavy_checkmark"
	else
		printf "[WGDashboard] %s Found existing ./download folder\n" "$heavy_checkmark"
	fi
    
    if [ ! -d "db" ] 
	then 
		mkdir "db"
		printf "[WGDashboard] %s Created ./db folder\n" "$heavy_checkmark"
	else
		printf "[WGDashboard] %s Found existing ./db folder\n" "$heavy_checkmark"
	fi
    
    if ! python3 --version > /dev/null 2>&1
    then
    	printf "[WGDashboard] Python is not installed, trying to install now\n"
    	_installPython
    else
    	printf "[WGDashboard] %s Python is installed\n" "$heavy_checkmark"
    fi
    
    _determinePypiMirror
    _checkPythonVersion
    _installPythonVenv
    _installPythonPip
	_checkWireguard
    sudo chmod -R 755 /etc/wireguard/
    
    _check_and_set_venv
    printf "[WGDashboard] %s Upgrading Python Package Manage (PIP)\n" "$install"
	{ date; python3 -m ensurepip --upgrade; printf "\n\n"; } >> ./log/install.txt
    { date; python3 -m pip install --upgrade pip -i "$selected_url"; printf "\n\n"; } >> ./log/install.txt
    printf "[WGDashboard] %s Installing latest Python dependencies\n" "$install"
	{ date; python3 -m pip install -r requirements.txt  -i "$selected_url"; printf "\n\n"; } >> ./log/install.txt #This all works on the default installation.
    
      
	if [ ! -f "ssl-tls.ini" ]
		then
			printf "[SSL/TLS]\ncertificate_path = \nprivate_key_path = \n" >> ssl-tls.ini
			printf "[WGDashboard] %s Created ssl-tls.ini\n" "$heavy_checkmark"
	else
			printf "[WGDashboard] %s Found existing ssl-tls.ini\n" "$heavy_checkmark"
	fi
    printf "[WGDashboard] %s WGDashboard installed successfully!\n" "$heavy_checkmark"
    printf "[WGDashboard] Enter ./wgd.sh start to start the dashboard\n"
}

check_wgd_status() {
  # Check if the PID file exists
  if [[ -f "$PID_FILE" ]]; then
    pid=$(<"$PID_FILE")  # Read PID without using `cat`
    
    # Check if the process exists
    if pgrep -F "$PID_FILE" &>/dev/null; then
      return 0  # Process is running
    fi
  fi

  # Fallback: Check if the APP_NAME process is running
  if pgrep -f "python3 $APP_NAME" &>/dev/null; then
    return 0  # Process is running
  fi

  return 1  # Process not running
}

certbot_create_ssl() {
  if ! command -v certbot &>/dev/null; then
    printf "[WGDashboard] %s Certbot is not installed. Please install it before running this command.\n" "$HEAVY_CROSSMARK"
    return 1
  fi

  certbot certonly --config ./certbot.ini --email "$EMAIL" --work-dir "$CB_WORK_DIR" --config-dir "$CB_CONFIG_DIR" --domain "$SERVERURL"
}

certbot_renew_ssl() {
  if ! command -v certbot &>/dev/null; then
    printf "[WGDashboard] %s Certbot is not installed. Please install it before running this command.\n" "$HEAVY_CROSSMARK"
    return 1
  fi

  certbot renew --work-dir "$CB_WORK_DIR" --config-dir "$CB_CONFIG_DIR"
}

gunicorn_start() {
  printf "%s\n" "$DASHES"
  printf "[WGDashboard] Starting WGDashboard with Gunicorn in the background...\n"

  # Ensure environment is correctly set for root users
  if [[ $USER == "root" ]]; then
    export PATH="$PATH:/usr/local/bin:$HOME/.local/bin"
  fi

  # Activate virtual environment and start Gunicorn
  _check_and_set_venv
  sudo "$VENV_GUNICORN" --config ./gunicorn.conf.py &  

  # Wait for Gunicorn to create the PID file
  for i in {1..10}; do
    if [[ -f "./gunicorn.pid" ]]; then
      printf "[WGDashboard] WGDashboard with Gunicorn started successfully\n"
      printf "%s\n" "$DASHES"
      return 0
    fi
    sleep 1
  done

  printf "[WGDashboard] %s Failed to start WGDashboard with Gunicorn!\n" "$HEAVY_CROSSMARK"
  return 1
}

gunicorn_stop() {
  if [[ -f "./gunicorn.pid" ]]; then
    sudo kill "$(cat ./gunicorn.pid)" && rm -f ./gunicorn.pid
    printf "[WGDashboard] %s Gunicorn stopped successfully.\n" "$HEAVY_CHECKMARK"
  else
    printf "[WGDashboard] %s Gunicorn is not running.\n" "$HEAVY_CROSSMARK"
    return 1
  fi
}

start_wgd() {
  _checkWireguard
  gunicorn_start
}

stop_wgd() {
  if [[ -f "$PID_FILE" ]]; then
    gunicorn_stop
  else
    if pkill -f "python3 $APP_NAME"; then
      printf "[WGDashboard] %s WGDashboard process stopped successfully.\n" "$HEAVY_CHECKMARK"
    else
      printf "[WGDashboard] %s No running WGDashboard process found.\n" "$HEAVY_CROSSMARK"
      return 1
    fi
  fi
}

# ============= Docker Functions =============

startwgd_docker() {
  _checkWireguard
  printf "[WGDashboard][Docker] WireGuard configuration started\n"
  
  # Log start operation
  { date; start_core; printf "\n\n"; } | tee -a ./log/install.txt
  
  gunicorn_start
}

start_core() {
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
  local wg_port_listen="$wg_port"
  local wg_addr_range="$wg_net"

  # Generate WireGuard keys
  local private_key public_key
  private_key=$(wg genkey)
  public_key=$(echo "$private_key" | wg pubkey)

  # Ensure WireGuard config directory exists
  if [[ ! -d "/etc/wireguard" ]]; then
    mkdir -p /etc/wireguard
    chmod 700 /etc/wireguard
  fi

  # Create WireGuard configuration
  cat <<EOF >"/etc/wireguard/wg0.conf"
[Interface]
PrivateKey = $private_key
Address = $wg_addr_range
ListenPort = $wg_port_listen
SaveConfig = true
PostUp = /opt/wireguarddashboard/src/iptable-rules/postup.sh
PreDown = /opt/wireguarddashboard/src/iptable-rules/postdown.sh
EOF

  chmod 600 /etc/wireguard/wg0.conf
  printf "[WGDashboard] %s New WireGuard configuration created: /etc/wireguard/wg0.conf\n" "$HEAVY_CHECKMARK"
}

# ============= Docker Functions =============

start_wgd_debug() {
  printf "%s\n" "$DASHES"
  _checkWireguard
  printf "[WGDashboard] Starting WGDashboard in the foreground...\n"
  sudo "$VENV_PYTHON" "$APP_NAME"
  printf "%s\n" "$DASHES"
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

	if [ "$commandConfirmed" = "true" ]; then
		printf "[WGDashboard] Confirmation granted.\n"
		up="Y"
	else
		printf "[WGDashboard] Are you sure you want to update to the %s? (Y/N): " "$new_ver"
		read up
	fi

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

if [ "$#" -lt 1 ]; then
	help
else
	if [ "$2" = "-y" ] || [ "$2" = "-Y" ]; then
		commandConfirmed="true"
	fi

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
		clear
		printf "=================================================================================\n"
	  	printf "+          <WGDashboard> by Donald Zou - https://github.com/donaldzou           +\n"
	  	printf "=================================================================================\n"
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
	elif [ "$1" = "os" ]; then
    		_determineOS
    elif [ "$1" = "ping" ]; then
        	_determinePypiMirror
	else
		help
	fi
fi
