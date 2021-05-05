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



## 📣 What's New: Version 2.0

### ⚠️ **Update from v1.x.x**

1. Stop the dashboard if it is running.
2. You can use `git pull https://github.com/donaldzou/Wireguard-Dashboard.git v2.0`  to get the new update inside `Wireguard-Dashboard` directory.
3. Proceed **Step 2 & 3** in the [Install](#-install) step down below.

<hr>

- Added login function to dashboard

  - ***I'm not using the most ideal way to store the username and password, feel free to provide a better way to do this if you any good idea!***

- Added a config file to the dashboard

- Dashboard config can be change within the **Setting** tab on the side bar 

- Adjusted UI

- And much more!

  

## 💡 Features

- Add peers for each WireGuard configuration

- Manage peer

- Delete peers

- And many more coming up! Welcome to contribute to this project!

  

## 📝 Requirement

- Ubuntu or Debian based OS, other might work, but haven't test yet. Tested on the following OS:
  - [x] Ubuntu 18.04.1 LTS
  - [ ] If you have tested on other OS and it works perfectly please provide it to me!

- ‼️ Make sure you have **Wireguard** and **Wireguard-Tools (`wg-quick`)** installed.‼️  <a href="https://www.wireguard.com/install/">How to install?</a>
- Configuration files under **/etc/wireguard**

  - **Note: For peers, `PublicKey` & `AllowedIPs` is required.**
- Python 3.7+ & Pip3
  ```
  $ sudo apt-get install python3 python3-pip
  ```



## 🛠 Install

1. Download Wireguard Dashboard

```
$ git clone -b v2.0 https://github.com/donaldzou/Wireguard-Dashboard.git
```

**2. Install Python Dependencies**

```
$ cd Wireguard-Dashboard/src
$ python3 -m pip install -r requirements.txt
```

**3. Install & run Wireguard Dashboard**

```
$ sudo sh wgd.sh start
```

Access your server with port `10086` ! e.g (http://your_server_ip:10086), continue to read to on how to change port and ip that dashboard is running with.



## 🪜 Usage

**1. Start/Stop/Restart Wireguard Dashboard**

```
$ cd Wireguard-Dashboard/src
$ sudo sh wgd.sh start    # Start the dashboard in background
$ sudo sh wgd.sh debug    # Start the dashboard in foreground (debug mode)
$ sudo sh wgd.sh stop     # Stop the dashboard
$ sudo sh wgd.sh restart  # Restart the dasboard
$ sudo sh wgd.sh update   # Update the dashboard
```

⚠️  **For first time user please also read the next section.**



## ✂️ Dashboard Configuration

Since version 2.0, Wireguard Dashboard will be using a configuration file called `wg-dashboard.ini`, (It will generate automatically after first time running the dashboard). More options will include in future versions, and for now it included the following config:

### `[Account]`

`username` - Username (Default: `admin`)

`password` - Password, will be hash with SHA256 (Default: `admin`).

### `[Server]`

`wg_conf_path` - The path of all the Wireguard configurations (Default: `/etc/wireguard`)

`app_ip` - IP address the flask will run with (Default: `0.0.0.0`)

`app_port` - Port the flask will run with (Default: `10086`)

`auth_req` - Does the dashboard need authentication  (Default: `true`)

- If `auth_req = false` , user will not be access the **Setting** tab due to security consideration. **User can only change the file directly in system**. 

`version` - Dashboard Version

All these settings will be able to configure within the dashboard in **Settings** on the sidebar, without changing the actual file. **Except `version` and `auth_req` due to security consideration.**



## ❓ How to update the dashboard?

```
$ cd wireguard-dashboard
$ sudo sh wgd.sh update  # Perform update
$ sudo sh wgd.sh start   # Start dashboard
```



## 🔍 Screenshot

![Index Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/index.png)

<p align=center>Index Page</p>

![Signin Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/signin.png)

<p align=center>Signin Page</p>

![Configuration Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/configuration.png)

<p align=center>Configuration Page</p>

![Settings Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/settings.png)

<p align=center>Settings Page</p>

## Contributors ✨

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

