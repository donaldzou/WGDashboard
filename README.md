<hr>
<p align=center>Please provide your OS name and version if you can run the dashboard on it perfectly in <a href="https://github.com/donaldzou/wireguard-dashboard/issues/31">#31</a>, since I only tested on Ubuntu. Thank you!</p>
<hr>


<p align="center">
  <img src="https://raw.githubusercontent.com/donaldzou/wireguard-dashboard/main/img/Group%202.png" width="128">
</p>
<h1 align="center"> Wireguard Dashboard</h1>

<p align="center">
  <img src="http://ForTheBadge.com/images/badges/made-with-python.svg">
</p>
<p align="center">
  <a href="https://github.com/donaldzou/wireguard-dashboard/releases/latest"><img src="https://img.shields.io/github/v/release/donaldzou/wireguard-dashboard"></a>
</p>
<p align="center">Monitoring WireGuard is not convinient, need to login into server and type <code>wg show</code>. That's why this platform is being created, to view all configurations and manage them in a easier way.</p>


## 📣 What's New: Version v2.2

- 🎉  **New Features**
  - **QR Code:** You can add the private key in peer setting of your existed peer to create a QR code. Or just create a new one, dashboard will now be able to auto generate a private key and public key ;) Don't worry, all keys will be generated on your machine, and **will delete all key files after they got generated**. [❤️ in [#29](https://github.com/donaldzou/wireguard-dashboard/issues/29)]  
  - **Peer configuration file download:** Same as QR code, you now can download the peer configuration file, so you don't need to manually input all the details on the peer machine! [❤️ in [#40](https://github.com/donaldzou/wireguard-dashboard/issues/40)]
  - **Autostart on boot:** Added a tutorial on how to start the dashboard to on boot! Please read the [tutorial below](#autostart-wireguard-dashboard-on-boot). [❤️ in [#29](https://github.com/donaldzou/wireguard-dashboard/issues/29)]  
- 🪚  **Bug Fixed**
  - When there are comments in the wireguard config file, will cause the dashboard to crash.
  - Used regex to search for config files.
<hr>


## Table of Content

- [💡  Features](#-features)
- [📝  Requirement](#-requirement)
- [🛠  Install](#-install)
- [🪜  Usage](#-usage)
  - [Start/Stop/Restart Wireguard Dashboard](#startstoprestart-wireguard-dashboard)
  - [Autostart Wireguard Dashboard on boot](#autostart-wireguard-dashboard-on-boot)
- [✂️  Dashboard Configuration](#%EF%B8%8F-dashboard-configuration)
  - [Dashboard Configuration file](#dashboard-configuration-file)
  - [Generating QR code](#generating-qr-code)
- [❓  How to update the dashboard?](#-how-to-update-the-dashboard)
  - [⚠️  Update from v1.x.x](#%EF%B8%8F--update-from-v1xx)
- [🔍  Screenshot](#-screenshot)
- [⏰  Changelog](#--changelog)
- [🛒  Dependencies](#-dependencies)
- [✨  Contributors](#-contributors)

## 💡 Features

- Add peers for each WireGuard configuration

- Manage peer

- Delete peers

- And many more coming up! Welcome to contribute to this project!


## 📝 Requirement

- Ubuntu or Debian based OS, other might work, but haven't test yet. Tested on the following OS:
  - [x] Ubuntu 18.04.1 LTS - 20.04.1 LTS
  - [x] Debian GNU/Linux 10 (buster) [❤️ @[robchez](https://github.com/robchez)]
  - [x] AlmaLinux 8.4 (Electric Cheetah) [❤️ @[barry-smithjr](https://github.com/)]
  - [x] CentOS 7 [❤️ @[PrzemekSkw](https://github.com/PrzemekSkw)]
  - [ ] If you have tested on other OS and it works perfectly please provide it to me in [#31](https://github.com/donaldzou/wireguard-dashboard/issues/31). Thank you!
  
- ‼️ Make sure you have **Wireguard** and **Wireguard-Tools (`wg-quick`)** installed.‼️  <a href="https://www.wireguard.com/install/">How to install?</a>
- Configuration files under **/etc/wireguard**

  - **Note**: 
    - **For `[Interface]` in the `.conf` file, please make sure you have `SaveConfig = true` under `[Interface]`** (Bug mentioned in [#9](https://github.com/donaldzou/wireguard-dashboard/issues/9#issuecomment-852346481))
    - **For peers, `PublicKey` & `AllowedIPs` is required.**
- Python 3.7+ & Pip3

## 🛠 Install
1. **Download Wireguard Dashboard**

   ```shell
   $ git clone -b v2.2 https://github.com/donaldzou/wireguard-dashboard.git
2. **Install Python Dependencies**

   ```shell
   $ cd wireguard-dashboard/src
   $ python3 -m pip install -r requirements.txt
   ```

3. **Install & run Wireguard Dashboard**

   ```shell
   $ sudo chmod -R 744 /etc/wireguard   # Add read and execute permission of the wireguard config folder
   $ sudo chmod u+x wgd.sh
   $ ./wgd.sh start
   ```

   **Note**:

   > For [`pivpn`](https://github.com/pivpn/pivpn) user, please use `sudo ./wgd.sh start` to run if your current account does not have the permission to run `wg show` and `wg-quick`.

4. **Access dashboard**

   Access your server with port `10086` ! e.g (http://your_server_ip:10086), continue to read to on how to change port and ip that dashboard is running with.

## 🪜 Usage

#### Start/Stop/Restart Wireguard Dashboard


```shell
$ cd Wireguard-Dashboard/src
-----------------------------
$ ./wgd.sh start    # Start the dashboard in background
-----------------------------
$ ./wgd.sh debug    # Start the dashboard in foreground (debug mode)
-----------------------------
$ ./wgd.sh stop     # Stop the dashboard
-----------------------------
$ ./wgd.sh restart  # Restart the dasboard
```

#### Autostart Wireguard Dashboard on boot

In the `src` folder, it contained a file called `wg-dashboard.service`, we can use this file to let our system to autostart the dashboard after reboot. The following has tested on Ubuntu 18.04.1 LTS, please don't hesitate to provide your system if you have tested the autostart on another system.

1. **Changing the directory to the dashboard's directory**

   ```bash
   $ cd wireguard-dashboard/src
   ```

2. **Get the full path of the dashboard's directory**

   ```bash
   $ pwd
   #Output: /root/wireguard-dashboard/src
   ```

   For me, my output is the one above, your's might be different since it depends on where you downloaded the dashboard. **Copy the the output to somewhere, we will need this in the next step.**

3. **Edit the service file**

   ```bash
   $ nano wg-dashboard.service
   ```

   You will see something like this:

   ```
   [Unit]
   After=netword.service
   
   [Service]
   WorkingDirectory=<your dashboard directory full path here>
   ExecStart=/usr/bin/python3 <your dashboard directory full path here>/dashboard.py
   Restart=always
   
   
   [Install]
   WantedBy=default.target
   ```

   Now, we need to replace both `<your dashboard directory full path here>` to the one you just copied from step 2. After doing this, the file will become something like this:

   ```
   [Unit]
   After=netword.service
   
   [Service]
   WorkingDirectory=/root/wireguard-dashboard/src
   ExecStart=/usr/bin/python3 /root/wireguard-dashboard/src/dashboard.py
   Restart=always
   
   
   [Install]
   WantedBy=default.target
   ```

   **Be aware that after the value of `WorkingDirectory`, it does not have  a `/` (slash).** You can save the file with `control+x` and press `Y`.

4. **Copy the service file to systemd folder**

   ```bash
   $ cp wg-dashboard.service /etc/systemd/system/wg-dashboard.service
   ```

   To make sure you copy the file successfully, you can use this command `cat /etc/systemd/system/wg-dashboard.service` to see if it will output the file you just edited.

5. **Enable the service**

   ```bash
   $ sudo chmod 664 /etc/systemd/system/wg-dashboard.service
   $ sudo systemctl daemon-reload
   $ sudo systemctl enable wg-dashboard.service
   $ sudo systemctl start wg-dashboard.service  # <-- To start the service
   ```

6. **Check if the service run correctly**

   ```bash
   $ sudo systemctl status wg-dashboard.service
   ```

   And you should see something like this

   ```bash
   ● wg-dashboard.service
        Loaded: loaded (/etc/systemd/system/wg-dashboard.service; enabled; vendor preset: enabled)
        Active: active (running) since Tue 2021-08-03 22:31:26 UTC; 4s ago
      Main PID: 6602 (python3)
         Tasks: 1 (limit: 453)
        Memory: 26.1M
        CGroup: /system.slice/wg-dashboard.service
                └─6602 /usr/bin/python3 /root/wireguard-dashboard/src/dashboard.py
   
   Aug 03 22:31:26 ubuntu-wg systemd[1]: Started wg-dashboard.service.
   Aug 03 22:31:27 ubuntu-wg python3[6602]:  * Serving Flask app "Wireguard Dashboard" (lazy loading)
   Aug 03 22:31:27 ubuntu-wg python3[6602]:  * Environment: production
   Aug 03 22:31:27 ubuntu-wg python3[6602]:    WARNING: This is a development server. Do not use it in a production deployment.
   Aug 03 22:31:27 ubuntu-wg python3[6602]:    Use a production WSGI server instead.
   Aug 03 22:31:27 ubuntu-wg python3[6602]:  * Debug mode: off
   Aug 03 22:31:27 ubuntu-wg python3[6602]:  * Running on all addresses.
   Aug 03 22:31:27 ubuntu-wg python3[6602]:    WARNING: This is a development server. Do not use it in a production deployment.
   Aug 03 22:31:27 ubuntu-wg python3[6602]:  * Running on http://0.0.0.0:10086/ (Press CTRL+C to quit)
   ```

   If you see `Active:` followed by `active (running) since...` then it means it run correctly.

7. **Stop/Start/Restart the service**

   ```bash
   $ sudo systemctl stop wg-dashboard.service # <-- To stop the service
   $ sudo systemctl start wg-dashboard.service # <-- To start the service
   $ sudo systemctl restart wg-dashboard.service # <-- To restart the service
   ```

8. **And now you can reboot your system, and use the command at step 6 to see if it will auto start after the reboot. If you have any questions or problem, please report a bug.**

## ✂️ Dashboard Configuration

#### Dashboard Configuration file

Since version 2.0, Wireguard Dashboard will be using a configuration file called `wg-dashboard.ini`, (It will generate automatically after first time running the dashboard). More options will include in future versions, and for now it included the following config:

|                 | Description                                                  | Default Value            |
| --------------- | ------------------------------------------------------------ | ------------------------ |
| **`[Account]`** |                                                              |                          |
| `username`      | Dashboard login username                                     | `admin`                  |
| `password`      | Password, will be hash with SHA256                           | `admin` hashed in SHA256 |
| **`[Server]`**  |                                                              |                          |
| `wg_conf_path`  | The path of all the Wireguard configurations                 | `/etc/wireguard`         |
| `app_ip`        | IP address the dashboard will run with                       | `0.0.0.0`                |
| `app_port`      | Port the the dashboard will run with                         | `10086`                  |
| `auth_req`      | Does the dashboard need authentication to access             | `true`                   |
|                 | If `auth_req = false` , user will not be access the **Setting** tab due to security consideration. **User can only change the file directly in system**. |                          |
| `version`       | Dashboard Version                                            | N/A                      |

<p align=center>Latest Version: V2.1</p>

All these settings will be able to configure within the dashboard in **Settings** on the sidebar, without changing the actual file. **Except `version` and `auth_req` due to security consideration.**

#### Generating QR code and peer configuration file (.conf)

Starting version 2.2, dashboard can now generate QR code and configuration file for each peer. Here is a template of what each QR code encoded with and the same content will be inside the file:

```
[Interface]
PrivateKey = QWERTYUIOPO234567890YUSDAKFH10E1B12JE129U21=
Address = 0.0.0.0/32
DNS = 1.1.1.1

[Peer]
PublicKey = QWERTYUIOPO234567890YUSDAKFH10E1B12JE129U21=
AllowedIPs = 0.0.0.0/0
Endpoint = 0.0.0.0:51820
```

|                   | Description                                                  | Default Value                                                |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **`[Interface]`** |                                                              |                                                              |
| `PrivateKey`      | The private key of this peer                                 | N/A                                                          |
| `Address`         | The `allowed_ips` of your peer                               | N/A                                                          |
| `DNS`             | The DNS server your peer will use                            | `1.1.1.1` - Cloud flare DNS, you can change it when you adding the peer or in the peer setting. |
| **`[Peer]`**      |                                                              |                                                              |
| `PublicKey`       | The public key of your server                                | N/A                                                          |
| `AllowedIPs`      | IP ranges for which a peer will route traffic                | `0.0.0.0/0` - Indicated a default route to send all internet and VPN traffic through that peer. |
| `Endpoint`        | Your wireguard server ip and port, the dashboard will search for your server's default interface's ip. | `<your server default interface ip>:<listen port>`           |

## ❓ How to update the dashboard?

1. Change your directory to `wireguard-dashboard` 
    ```
    $ cd wireguard-dashboard
    ```
2. Get the newest version
    ```
    $ sudo git pull https://github.com/donaldzou/wireguard-dashboard.git v2.2 --force
    ```
3. Update and install all python dependencies
   ```
   $ python3 -m pip install -r requirements.txt
   ```
4. Start the dashboard
    ```
   $ ./wgd.sh start
   ```
### ⚠️  **Update from v1.x.x**

1. Stop the dashboard if it is running.
2. You can use `git pull https://github.com/donaldzou/wireguard-dashboard.git v2.2`  to get the new update inside `Wireguard-Dashboard` directory.
3. Proceed **Step 2 & 3** in the [Install](#-install) step down below.

## 🔍 Screenshot

![Index Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/index.png)

<p align=center>Index Page</p>

![Signin Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/signin.png)

<p align=center>Signin Page</p>

![Configuration Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/configuration.png)

<p align=center>Configuration Page</p>

![Settings Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/settings.png)

<p align=center>Settings Page</p>



## ⏰  Changelog

#### v2.1 - Jul 2, 2021

- Added **Ping** and **Traceroute** tools!
- Adjusted the calculation of data usage on each peers
- Added refresh interval of the dashboard
- Bug fixed when no configuration on fresh install ([#23](https://github.com/donaldzou/wireguard-dashboard/issues/23))
- Fixed crash when too many peers ([#22](https://github.com/donaldzou/wireguard-dashboard/issues/22))

#### v2.0 - May 5, 2021

- Added login function to dashboard
  - ***I'm not using the most ideal way to store the username and password, feel free to provide a better way to do this if you any good idea!***
- Added a config file to the dashboard
- Dashboard config can be change within the **Setting** tab on the side bar
- Adjusted UI
- And much more!

#### v1.1.2 - Apr 3, 2021

- Resolved issue [#3](https://github.com/donaldzou/wireguard-dashboard/issues/3).

#### v1.1.1 - Apr 2, 2021

- Able to add a friendly name to each peer. Thanks [#2](https://github.com/donaldzou/wireguard-dashboard/issues/2) !

#### v1.0 - Dec 27, 2020

- Added the function to remove peers

## 🛒 Dependencies

- CSS/JS
  - [Bootstrap](https://getbootstrap.com/docs/4.6/getting-started/introduction/) `v4.6.0`
  - [Bootstrap Icon](https://icons.getbootstrap.com) `v1.4.0`
  - [jQuery](https://jquery.com) `v3.5.1`
- Python
  - [Flask](https://pypi.org/project/Flask/) `v1.1.2`
  - [TinyDB](https://pypi.org/project/tinydb/) `v4.3.0`
  - [ifcfg](https://pypi.org/project/ifcfg/) `v0.21`
  - [icmplib](https://pypi.org/project/icmplib/) `v2.1.1`

## ✨ Contributors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/antonioag95"><img src="https://avatars.githubusercontent.com/u/30556866?v=4?s=100" width="100px;" alt=""/><br /><sub><b>antonioag95</b></sub></a><br /><a href="https://github.com/donaldzou/wireguard-dashboard/commits?author=antonioag95" title="Tests">⚠️</a> <a href="https://github.com/donaldzou/wireguard-dashboard/commits?author=antonioag95" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/tonjo"><img src="https://avatars.githubusercontent.com/u/4726289?v=4?s=100" width="100px;" alt=""/><br /><sub><b>tonjo</b></sub></a><br /><a href="https://github.com/donaldzou/wireguard-dashboard/commits?author=tonjo" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

