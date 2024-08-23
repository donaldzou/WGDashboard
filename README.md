> [!WARNING]
> For users who installed the Docker solution under `./docker`, please view this important message: https://github.com/donaldzou/WGDashboard/issues/333
<hr>

<p align="center">
  <img alt="WGDashboard" src="./src/static/img/logo.png" width="128">
</p>
<h1 align="center">WGDashboard</h1>


<p align="center">
    <img src="https://forthebadge.com/images/badges/made-with-python.svg">
    <img src="https://forthebadge.com/images/badges/made-with-javascript.svg">
    <img src="https://forthebadge.com/images/badges/license-mit.svg">
</p>
<p align="center">
    <img src="https://forthebadge.com/images/badges/built-with-love.svg">
</p>
<p align="center">
  <a href="https://github.com/donaldzou/wireguard-dashboard/releases/latest"><img src="https://img.shields.io/github/v/release/donaldzou/wireguard-dashboard"></a>
  <a href="https://wakatime.com/badge/github/donaldzou/WGDashboard"><img src="https://wakatime.com/badge/github/donaldzou/WGDashboard.svg" alt="wakatime"></a>
  <a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fdonaldzou%2FWGDashboard&count_bg=%2379C83D&title_bg=%23555555&icon=github.svg&icon_color=%23E7E7E7&title=Visitor&edge_flat=false"/></a>
</p>
<p align="center">Monitoring WireGuard is not convenient, need to remote access to server and type <code>wg show</code>. That's why this project is being created, to view all configurations and manage them in a easy way.</p>
<p align="center">With all these awesome features, while keeping it <b>simple</b>, <b>easy to install and use</b></p>

<p align="center"><b><i>This project is not affiliate to the official WireGuard Project</i></b></p>

## 📣 What's New: v4.0

### 🎉 New Features

- **Updated dashboard design**: Re-designed some of the section with more modern style and layout, the UI is faster and more responsive, it also uses less memory. But overall is still the same dashboard you're familiarized.
- **Docker Solution**: We now have 2 docker solutions! Thanks to @DaanSelen & @shuricksumy for providing them. For more information, please see the [Docker](#-docker-solutions) section below.
- **Peer Job Scheduler**: Now you can schedule jobs for each peer to either **restrict** or **delete** the peer if the peer's total / upload / download data usage exceeded a limit, or you can set a specific datetime to restrict or delete the peer.
- **Share Peer's QR Code with Public Link**: You can share a peer's QR code and `.conf` file without the need to loging in.
- **WGDashboard's REST API**: You can now request all the api endpoint used in the dashboard. For more details please review the [API Documentation](./docs/api-documents.md).
- **Logging**: Dashboard will now log all activity on the dashboard and API requests.
- **Time-Based One-Time Password (TOTP)**: You can enable this function to add one more layer of security, and generate the TOTP with your choice of authenticator.
- **Designs**
  - **Real-time Graphs**: You can view real-time data changes with graphs in each configuration.
  - **Night mode**: You know what that means, it avoids bugs ;)
- **Enforce Python Virtual Environment**: I noticed newer Python version (3.12) does not allow to install packages globally, and plus I think is a good idea to use venv.
 
### 🧐 Other Changes
- **Deprecated jQuery from the project, and migrated and rewrote the whole front-end with Vue.js. This allows the dashboard is future proofed, and potential cross server access with a desktop app.**
- Rewrote the backend into a REST API structure
- Improved SQL query efficient
- Removed all templates, except for `index.html` where it will load the Vue.js app.
- Parsing names in `.conf`
- Minimized the need to read `.conf`, only when any `.conf` is modified

### 🥘 New Experimental Features
  - **Cross-Server Access**: Now you can access other servers that installed `v4` of WGDashboard through API key.
  - **Desktop App**: Thanks to **Cross-Server Access**, you can now download an ElectronJS based desktop app of WGDashboard, and use that to access WGDashboard on different servers.
  - > For more information, please scroll down to [🥘 Experimental Functions](#-experimental-functions)

> I can't thank enough for all of you who wait for this release, and for those who are new to this project, welcome :)
> Also, huge thanks to who contributed to this major release:
> @bolgovrussia, @eduardorosabales, @Profik, @airgapper, @tokon2000, @bkeenke, @kontorskiy777, @bugsse, @Johnnykson, @DaanSelen, @shuricksumy and many others!

<hr>

## 📋  Table of Content

<!-- TOC -->
  * [📣 What's New: v4.0](#-whats-new-v40)
    * [🎉 New Features](#-new-features)
    * [🧐 Other Changes](#-other-changes)
    * [🥘 New Experimental Features](#-new-experimental-features)
  * [📋  Table of Content](#-table-of-content)
  * [💡 Features](#-features)
  * [📝 Requirements](#-requirements)
    * [Supported Operating Systems](#supported-operating-systems)
    * [Existing WireGuard Configurations](#existing-wireguard-configurations)
  * [🛠 Install](#-install)
    * [Install Commands](#install-commands)
      * [Ubuntu 20.04 LTS](#ubuntu-2004-lts)
      * [Ubuntu 22.04 LTS & Ubuntu 24.02 LTS](#ubuntu-2204-lts--ubuntu-2402-lts)
      * [Debian 12.6](#debian-126)
      * [Debian 11.10](#debian-1110)
      * [Red Hat Enterprise Linux 9.4 & CentOS 9-Stream](#red-hat-enterprise-linux-94--centos-9-stream)
      * [Fedora 40 & Fedora 39 & Fedora 38](#fedora-40--fedora-39--fedora-38)
    * [Manual Installation](#manual-installation)
  * [🪜 Usage](#-usage)
      * [Start/Stop/Restart WGDashboard](#startstoprestart-wgdashboard)
      * [Autostart WGDashboard on boot (>= v2.2)](#autostart-wgdashboard-on-boot--v22)
  * [✂️ Dashboard Configuration](#-dashboard-configuration)
      * [Dashboard Configuration file](#dashboard-configuration-file)
      * [Generating QR code and peer configuration file (.conf)](#generating-qr-code-and-peer-configuration-file-conf)
  * [❓ How to update the dashboard?](#-how-to-update-the-dashboard)
      * [**Please note for users who are using `v3 - v3.0.6` want to update to `v4.0`**](#please-note-for-users-who-are-using-v3---v306-want-to-update-to-v40)
      * [**Please note for users who are using `v2.3.1` or below**](#please-note-for-users-who-are-using-v231-or-below)
  * [🐬 Docker Solutions](#-docker-solutions)
    * [Solution 1 from @DaanSelen](#solution-1-from-daanselen)
    * [Solution 2 from @shuricksumy](#solution-2-from-shuricksumy)
  * [📖 WGDashboard REST API Documentation & How to use API Key](#-wgdashboard-rest-api-documentation--how-to-use-api-key)
  * [🥘 Experimental Features](#-experimental-features)
    * [Cross-Server Access](#cross-server-access)
    * [Desktop App](#desktop-app)
  * [🔍 Screenshot](#-screenshot)
  * [🕰️ Changelogs](#-changelogs)
<!-- TOC -->

## 💡 Features

- Automatically look for existing WireGuard configuration under `/etc/wireguard`
- Easy to use interface, provided credential and TOTP protection to the dashboard
- Manage peers and configuration
  - Add Peers or by bulk with auto-generated information
  - Edit peer information
  - Delete peers with ease
  - Restrict peers
  - Generate QR Code and `.conf` file for peers, share it through a public link
  - Schedule jobs to delete / restrict peer when conditions are met
- View real time peer status
- Testing tool: Ping and Traceroute to your peer


## 📝 Requirements

1. Supported operating systems. Please view the list below.
2. WireGuard & WireGuard-Tools (`wg-quick`)
3. Python 3.10 / 3.11 / 3.12
4. `git`, `net-tools`, `sudo` (_This should only apply to RHEL 9 & 8, interestingly it doesn't have it preinstalled)_

### Supported Operating Systems
> [!NOTE]
> All operating systems below are tested by myself. All are ARM64 ran in UTM Virtual Machine.

| Ubuntu    | Debian | Red Hat Enterprise Linux | CentOS   | Fedora |
|-----------|--------|--------------------------|----------|--------|
| 24.02 LTS | 12.6   | 9.4                      | 9-Stream | 40     |
| 22.04 LTS | 11.10  |                          |          | 39     |
| 20.04 LTS |        |                          |          | 38     |

> [!TIP] 
> If you installed WGDashboard on other systems without any issues, please let me know. Thank you!

### Existing WireGuard Configurations

> [!NOTE]
> This only applies to existing WireGuard Configuration under `/etc/wireguard`

```ini
[Interface]
...
SaveConfig = true
# Need to include this line to allow WireGuard Tool to save your configuration, 
# or if you just want it to monitor your WireGuard Interface and don't need to
# make any changes with the dashboard, you can set it to false.

[Peer]
#Name# = Donald's iPhone
PublicKey = abcd1234
AllowedIPs = 1.2.3.4/32
```
> [!TIP]
> With `v4`, WGDashboard will look for entry with `#Name# = abc...` in each peer and use that for the name.

## 🛠 Install

### Install Commands

These commands are tested by myself in each OS. It contains commands to install WireGuard, Git, Net Tools, and even Python on some OS.

> [!WARNING]
> Please make sure you understand these commands before you run them.

#### Ubuntu 20.04 LTS

```shell
sudo add-apt-repository ppa:deadsnakes/ppa -y && \
sudo apt-get update -y && \
sudo apt-get install python3.10 python3.10-distutils wireguard-tools net-tools --no-install-recommends -y && \
git clone https://github.com/donaldzou/WGDashboard.git && \
cd WGDashboard/src && \
chmod +x ./wgd.sh && \
./wgd.sh install && \
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p
```
#### Ubuntu 22.04 LTS & Ubuntu 24.02 LTS

```shell
sudo apt-get update -y && \
sudo apt install wireguard-tools net-tools --no-install-recommends -y && \
git clone https://github.com/donaldzou/WGDashboard.git && \
cd ./WGDashboard/src && \
chmod +x ./wgd.sh && \
./wgd.sh install && \
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p /etc/sysctl.conf
```
#### Debian 12.6

```shell
apt-get install sudo git iptables -y && \ 
sudo apt-get update && \
sudo apt install wireguard-tools net-tools && \
git clone https://github.com/donaldzou/WGDashboard.git && \
cd ./WGDashboard/src && \
chmod +x ./wgd.sh && \
./wgd.sh install && \
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p /etc/sysctl.conf
```

#### Debian 11.10

> [!WARNING]
> This commands will download Python 3.10's source code and build from it, since Debian 11.10 doesn't comes with Python 3.10

```shell
apt-get install sudo -y && \ 
sudo apt-get update && \ 
sudo apt install -y git iptables build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev wireguard-tools net-tools && \ 
wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \ 
tar -xvf Python-3.10.0.tgz && \ 
cd Python-3.10.0 && \ 
sudo ./configure --enable-optimizations && \ 
sudo make && \ 
sudo make altinstall && \ 
cd .. && \ 
git clone https://github.com/donaldzou/WGDashboard.git && \ 
cd ./WGDashboard/src && \ 
chmod +x ./wgd.sh && \ 
./wgd.sh install && \ 
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p /etc/sysctl.conf
```

#### Red Hat Enterprise Linux 9.4 & CentOS 9-Stream

```shell
sudo yum install wireguard-tools net-tools git python3.11 -y && \
git clone https://github.com/donaldzou/WGDashboard.git && \
cd ./WGDashboard/src && \
chmod +x ./wgd.sh && \
./wgd.sh install && \
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p /etc/sysctl.conf && \
firewall-cmd --add-port=10086/tcp --permanent && \
firewall-cmd --add-port=51820/udp --permanent && \
firewall-cmd --reload
```

#### Fedora 40 & Fedora 39 & Fedora 38

```shell
sudo yum install wireguard-tools net-tools git -y && \
git clone https://github.com/donaldzou/WGDashboard.git && \
cd ./WGDashboard/src && \
chmod +x ./wgd.sh && \
./wgd.sh install && \
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && \
sudo sysctl -p /etc/sysctl.conf && \
firewall-cmd --add-port=10086/tcp --permanent && \
firewall-cmd --add-port=51820/udp --permanent && \
firewall-cmd --reload
```

### Manual Installation

> [!NOTE]
> To ensure a smooth installation process, please make sure Python 3.10/3.11/3.12, `git`, `wireguard-tools` and `net-tools` are installed :)

1. Download WGDashboard

   ```shell
   git clone https://github.com/donaldzou/WGDashboard.git wgdashboard
   
2. Open the WGDashboard folder

   ```shell
   cd wgdashboard/src
   ```
   
3. Install WGDashboard

   ```shell
   sudo chmod u+x wgd.sh && \
   sudo ./wgd.sh install
   ```

4. Give read and execute permission to root of the WireGuard configuration folder, you can change the path if your configuration files are not stored in `/etc/wireguard`

   ```shell
   sudo chmod -R 755 /etc/wireguard
   ```

5. Run WGDashboard

   ```shell
   sudo ./wgd.sh start
   ```

6. Access dashboard

   Access your server with port `10086` (e.g. http://your_server_ip:10086), using username `admin` and password `admin`. See below how to change port and ip that the dashboard is running with.



## 🪜 Usage

#### Start/Stop/Restart WGDashboard


```shell
cd wgdashboard/src
-----------------------------
./wgd.sh start    # Start the dashboard in background
-----------------------------
./wgd.sh debug    # Start the dashboard in foreground (debug mode)
-----------------------------
./wgd.sh stop     # Stop the dashboard
-----------------------------
./wgd.sh restart  # Restart the dasboard
```

#### Autostart WGDashboard on boot (>= v2.2)

In the `src` folder, it contained a file called `wg-dashboard.service`, we can use this file to let our system to autostart the dashboard after reboot. The following guide has tested on **Ubuntu**, most **Debian** based OS might be the same, but some might not. Please don't hesitate to provide your system if you have tested the autostart on another system.

1. Changing the directory to the dashboard's directory

   ```shell
   cd wgdashboard/src
   ```

2. Get the full path of the dashboard's directory

   ```shell
   pwd
   #Output: /root/wgdashboard/src
   ```

   For this example, the output is `/root/wireguard-dashboard/src`, your path might be different since it depends on where you downloaded the dashboard in the first place. **Copy the the output to somewhere, we will need this in the next step.**

3. Edit the service file, the service file is located in `wireguard-dashboard/src`, you can use other editor you like, here will be using `nano`

   ```shell
   nano wg-dashboard.service
   ```

   You will see something like this:

   ```ini
   [Unit]
   After=syslog.target network-online.target
   Wants=wg-quick.target
   ConditionPathIsDirectory=/etc/wireguard
   
   [Service]
   Type=forking
   PIDFile=<absolute_path_of_wgdashboard_src>/gunicorn.pid
   WorkingDirectory=<absolute_path_of_wgdashboard_src>
   ExecStart=<absolute_path_of_wgdashboard_src>/wgd.sh start
   ExecStop=<absolute_path_of_wgdashboard_src>/wgd.sh stop
   ExecReload=<absolute_path_of_wgdashboard_src>/wgd.sh restart
   TimeoutSec=120
   PrivateTmp=yes
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   Now, we need to replace all `<absolute_path_of_wgdashboard_src>` to the one you just copied from step 2. After doing this, the file will become something like this, your file might be different:

   **Be aware that after the value of `WorkingDirectory`, it does not have  a `/` (slash).** And then save the file after you edited it

4. Copy the service file to systemd folder

   ```bash
   $ sudo cp wg-dashboard.service /etc/systemd/system/wg-dashboard.service
   ```

   To make sure you copy the file successfully, you can use this command `cat /etc/systemd/system/wg-dashboard.service` to see if it will output the file you just edited.

5. Enable the service

   ```bash
   $ sudo chmod 664 /etc/systemd/system/wg-dashboard.service
   $ sudo systemctl daemon-reload
   $ sudo systemctl enable wg-dashboard.service
   $ sudo systemctl start wg-dashboard.service  # <-- To start the service
   ```

6. Check if the service run correctly

   ```bash
   $ sudo systemctl status wg-dashboard.service
   ```
   And you should see something like this

   ```shell
    ● wg-dashboard.service
    Loaded: loaded (/etc/systemd/system/wg-dashboard.service; enabled; vendor preset: enabled)
    Active: active (running) since Wed 2024-08-14 22:21:47 EDT; 55s ago
    Process: 494968 ExecStart=/home/donaldzou/Wireguard-Dashboard/src/wgd.sh start (code=exited, status=0/SUCCESS)
    Main PID: 495005 (gunicorn)
    Tasks: 5 (limit: 4523)
    Memory: 36.8M
    CPU: 789ms
    CGroup: /system.slice/wg-dashboard.service
    ├─495005 /home/donaldzou/Wireguard-Dashboard/src/venv/bin/python3 ./venv/bin/gunicorn --config ./gunicorn.conf.py
    └─495007 /home/donaldzou/Wireguard-Dashboard/src/venv/bin/python3 ./venv/bin/gunicorn --config ./gunicorn.conf.py
    
    Aug 14 22:21:40 wg sudo[494978]:     root : PWD=/home/donaldzou/Wireguard-Dashboard/src ; USER=root ; COMMAND=./venv/bin/gunicorn --config ./gunicorn.conf.py
    Aug 14 22:21:40 wg sudo[494978]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=0)
    Aug 14 22:21:40 wg wgd.sh[494979]: [WGDashboard] WGDashboard w/ Gunicorn will be running on 0.0.0.0:10086
    Aug 14 22:21:40 wg wgd.sh[494979]: [WGDashboard] Access log file is at ./log/access_2024_08_14_22_21_40.log
    Aug 14 22:21:40 wg wgd.sh[494979]: [WGDashboard] Error log file is at ./log/error_2024_08_14_22_21_40.log
    Aug 14 22:21:40 wg sudo[494978]: pam_unix(sudo:session): session closed for user root
    Aug 14 22:21:45 wg wgd.sh[494968]: [WGDashboard] Checking if WGDashboard w/ Gunicorn started successfully
    Aug 14 22:21:47 wg wgd.sh[494968]: [WGDashboard] WGDashboard w/ Gunicorn started successfully
    Aug 14 22:21:47 wg wgd.sh[494968]: ------------------------------------------------------------
    Aug 14 22:21:47 wg systemd[1]: Started wg-dashboard.service.
   ```

   If you see `Active:` followed by `active (running) since...` then it means it run correctly. 

7. Stop/Start/Restart the service

   ```bash
   sudo systemctl stop wg-dashboard.service      # <-- To stop the service
   sudo systemctl start wg-dashboard.service     # <-- To start the service
   sudo systemctl restart wg-dashboard.service   # <-- To restart the service
   ```

8. **And now you can reboot your system, and use the command at step 6 to see if it will auto start after the reboot, or just simply access the dashboard through your browser. If you have any questions or problem, please report it in the issue page.**

## ✂️ Dashboard Configuration

#### Dashboard Configuration file

Since version 2.0, WGDashboard will be using a configuration file called `wg-dashboard.ini`, (It will generate automatically after first time running the dashboard). More options will include in future versions, and for now it included the following configurations:

|                              | Description                                                                                                                                                                                              | Default                                              | Edit Available |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|----------------|
| **`[Account]`**              | *Configuration on account*                                                                                                                                                                               |                                                      |                |
| `username`                   | Dashboard login username                                                                                                                                                                                 | `admin`                                              | Yes            |
| `password`                   | Password, will be hash with SHA256                                                                                                                                                                       | `admin` hashed in SHA256                             | Yes            |
|                              |                                                                                                                                                                                                          |                                                      |                |
| **`[Server]`**               | *Configuration on dashboard*                                                                                                                                                                             |                                                      |                |
| `wg_conf_path`               | The path of all the Wireguard configurations                                                                                                                                                             | `/etc/wireguard`                                     | Yes            |
| `app_ip`                     | IP address the dashboard will run with                                                                                                                                                                   | `0.0.0.0`                                            | Yes            |
| `app_port`                   | Port the the dashboard will run with                                                                                                                                                                     | `10086`                                              | Yes            |
| `auth_req`                   | Does the dashboard need authentication to access, if `auth_req = false` , user will not be access the **Setting** tab due to security consideration. **User can only edit the file directly in system**. | `true`                                               | **No**         |
| `version`                    | Dashboard Version                                                                                                                                                                                        | `v4.0`                                               | **No**         |
| `dashboard_refresh_interval` | How frequent the dashboard will refresh on the configuration page                                                                                                                                        | `60000ms`                                            | Yes            |
| `dashboard_sort`             | How configuration is sorting                                                                                                                                                                             | `status`                                             | Yes            |
| `dashboard_theme`            | Dashboard Theme                                                                                                                                                                                          | `dark`                                               | Yes            |
|                              |                                                                                                                                                                                                          |                                                      |                |
| **`[Peers]`**                | *Default Settings on a new peer*                                                                                                                                                                         |                                                      |                |
| `peer_global_dns`            | DNS Server                                                                                                                                                                                               | `1.1.1.1`                                            | Yes            |
| `peer_endpoint_allowed_ip`   | Endpoint Allowed IP                                                                                                                                                                                      | `0.0.0.0/0`                                          | Yes            |
| `peer_display_mode`          | How peer will display                                                                                                                                                                                    | `grid`                                               | Yes            |
| `remote_endpoint`            | Remote Endpoint (i.e where your peers will connect to)                                                                                                                                                   | *depends on your server's default network interface* | Yes            |
| `peer_mtu`                   | Maximum Transmit Unit                                                                                                                                                                                    | `1420`                                               |                |
| `peer_keep_alive`            | Keep Alive                                                                                                                                                                                               | `21`                                                 | Yes            |

#### Generating QR code and peer configuration file (.conf)

Starting version 2.2, dashboard can now generate QR code and configuration file for each peer. Here is a template of what each QR code encoded with and the same content will be inside the file:

```ini
[Interface]
PrivateKey = QWERTYUIOPO234567890YUSDAKFH10E1B12JE129U21=
Address = 0.0.0.0/32
DNS = 1.1.1.1

[Peer]
PublicKey = QWERTYUIOPO234567890YUSDAKFH10E1B12JE129U21=
AllowedIPs = 0.0.0.0/0
Endpoint = 0.0.0.0:51820
```

|                   | Description                                                  | Default Value                                                | Available in Peer setting |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------- |
| **`[Interface]`** |                                                              |                                                              |                           |
| `PrivateKey`      | The private key of this peer                                 | Private key generated by WireGuard (`wg genkey`) or provided by user | Yes                       |
| `Address`         | The `allowed_ips` of your peer                               | N/A                                                          | Yes                       |
| `DNS`             | The DNS server your peer will use                            | `1.1.1.1` - Cloud flare DNS, you can change it when you adding the peer or in the peer setting. | Yes                       |
| **`[Peer]`**      |                                                              |                                                              |                           |
| `PublicKey`       | The public key of your server                                | N/A                                                          | No                        |
| `AllowedIPs`      | IP ranges for which a peer will route traffic                | `0.0.0.0/0` - Indicated a default route to send all internet and VPN traffic through that peer. | Yes                       |
| `Endpoint`        | Your wireguard server ip and port, the dashboard will search for your server's default interface's ip. | `<your server default interface ip>:<listen port>`           | Yes                       |

## ❓ How to update the dashboard?

#### **Please note for users who are using `v3 - v3.0.6` want to update to `v4.0`**
- Although theoretically updating through `wgd.sh` should work, but I still suggest you to update the dashboard manually.

#### **Please note for users who are using `v2.3.1` or below**

- For user who is using `v2.3.1` or below, please notice that all data that stored in the current database will **not** transfer to the new database. This is hard decision to move from TinyDB to SQLite. But SQLite does provide a thread-safe access and TinyDB doesn't. I couldn't find a safe way to transfer the data, so you need to do them manually... Sorry about that :pensive:。 But I guess this would be a great start for future development :sunglasses:.


1. Change your directory to `wgdashboard` 
   
    ```shell
    cd wgdashboard/src
    ```
    
2. Update the dashboard
    ```shell
    git pull https://github.com/donaldzou/WGDashboard.git --force
    ```

3. Install

   ```shell
   sudo ./wgd.sh install
   ```

Starting with `v3.0`, you can simply do `sudo ./wgd.sh update` !! (I hope)

## 🐬 Docker Solutions

Current, we have 2 beloved contributors provided solutions for hosting WGDashboard with Docker

### Solution 1 from @DaanSelen

Please visit [Docker-explain.md](./docker/Docker-explain.md)

### Solution 2 from @shuricksumy

Please visit [shuricksumy/docker-wgdashboard](https://github.com/shuricksumy/docker-wgdashboard)

> For questions or issues related to Docker, please visit [#272](https://github.com/donaldzou/WGDashboard/issues/272)

## 📖 WGDashboard REST API Documentation & How to use API Key

Please visit the [API Documentation](./docs/api-documents.md)

## 🥘 Experimental Features

### Cross-Server Access

Starting with `v4.0`, you can access WGDashboards on other server through one WGDashboard with API Keys

![Cross Server Example](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/cross-server.gif)

### Desktop App

Since the major changes for `v4.0` is to move the whole front-end code to Vue.js. And with this change, we can take the
advantage of combining ElectronJS and Vue.js to create a Desktop version of WGDashboard. Currently, we provide an Universal macOS app and a Windows app.

To download the app, please visit the [latest release](https://github.com/donaldzou/WGDashboard/releases).

![ElectronJS App Demo](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/electronjs-app.gif)

## 🔍 Screenshot

![Sign In](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/sign-in.png)
![Cross Server](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/cross-server.png)
![Index](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/index.png)
![New Configuration](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/new-configuration.png)
![Settings](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/settings.png)
![Light-Dark Mode](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/light-dark.png)
![Configuration](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/configuration.png)
![Add Peers](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/add-peers.png)
![Ping](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/ping.png)
![Traceroute](https://donaldzou.nyc3.cdn.digitaloceanspaces.com/wgdashboard-images/traceroute.png)

## 🕰️ Changelogs

Please visit the [Changelogs.md](./docs/changelogs.md)
