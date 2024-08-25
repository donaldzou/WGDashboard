venv_python="./venv/bin/python3"
venv_gunicorn="./venv/bin/gunicorn"
pythonExecutable="python3"


_check_and_set_venv(){
    VIRTUAL_ENV="./venv"
    if [ ! -d $VIRTUAL_ENV ]; then
    	printf "[WGDashboard] Creating Python Virtual Environment under ./venv\n"
        { $pythonExecutable -m venv  $VIRTUAL_ENV; } >> ./log/install.txt
    fi
    
    if ! $venv_python --version > /dev/null 2>&1
    then
    	printf "[WGDashboard] %s Python Virtual Environment under ./venv failed to create. Halting now.\n" "$heavy_crossmark"	
    	kill  $TOP_PID
    fi
    
    source ${VIRTUAL_ENV}/bin/activate

}

build_core () {
    if [ ! -d "log" ]
	  then 
		printf "[WGDashboard] Creating ./log folder\n"
		mkdir "log"
	fi


    apk add --no-cache python3 net-tools python3-dev py3-virtualenv
    _check_and_set_venv
    printf "[WGDashboard] Upgrading Python Package Manage (PIP)\n"
    { date; python3 -m pip install --upgrade pip; printf "\n\n"; } >> ./log/install.txt
    printf "[WGDashboard] Building Bcrypt & Psutil\n"
    { date; python3 -m pip install -r requirements.txt ; printf "\n\n"; } >> ./log/install.txt
    printf "[WGDashboard] Build Successfull!\n"
    printf "[WGDashboard] Clean Up Pip!\n"
    { date; rm -rf /opt/wireguarddashboard/src/venv/lib/python3.12/site-packages/pip* ; printf "\n\n"; } >> ./log/install.txt

}

build_core
