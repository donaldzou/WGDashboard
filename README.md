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


## 📣 What's New: Version 2.1

- Added **Ping** and **Traceroute** tools!
- Adjusted the calculation of data usage on each peers
- Added refresh interval of the dashboard
- Bug fixed when no configuration on fresh install ([Bug report](https://github.com/donaldzou/wireguard-dashboard/issues/23#issuecomment-869189672))
- Fixed crash when too many peers ([Bug report](https://github.com/donaldzou/wireguard-dashboard/issues/22#issuecomment-868840564))
<hr>

## 💡 Features

- Add peers for each WireGuard configuration

- Manage peer

- Delete peers

- And many more coming up! Welcome to contribute to this project!

  

## 📝 Requirement

- Ubuntu or Debian based OS, other might work, but haven't test yet. Tested on the following OS:
  - [x] Ubuntu 18.04.1 LTS
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
   $ git clone -b v2.1 https://github.com/donaldzou/Wireguard-Dashboard.git
2. **Install Python Dependencies**

   ```shell
   $ cd Wireguard-Dashboard/src
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

**1. Start/Stop/Restart Wireguard Dashboard**


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

⚠️  **For first time user please also read the next section.**

## ✂️ Dashboard Configuration

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

## ❓ How to update the dashboard?

1. Change your directory to `wireguard-dashboard` 
    ```
    $ cd wireguard-dashboard
    ```
2. Get the newest version
    ```
    $ sudo git pull https://github.com/donaldzou/wireguard-dashboard.git v2.1 --force
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
2. You can use `git pull https://github.com/donaldzou/Wireguard-Dashboard.git v2.1`  to get the new update inside `Wireguard-Dashboard` directory.
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

