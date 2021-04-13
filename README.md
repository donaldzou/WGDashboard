<h1 align="center"> Wireguard Dashboard</h1>


<p align="center">
  <img src="http://ForTheBadge.com/images/badges/made-with-python.svg">
</p>

<p align="center">
  <a href="https://github.com/donaldzou/wireguard-dashboard/releases/latest"><img src="https://img.shields.io/github/v/release/donaldzou/wireguard-dashboard"></a>
</p>
<p align="center">Monitoring Wireguard is not convinient, need to login into server and type <code>wg show</code>. That's why this platform is being created, to view all configurations in a more straight forward way.</p>

## 💡 Features

- Add peers in configuration
- Manage peer names
- Delete peers
- And many more coming up! Welcome to contribute to this project!

## 📝 Requirement

- Ubuntu 18.04.1 LTS, other OS might work, but haven't test yet.
- ‼️ Make sure you have **Wireguard** installed.‼️  <a href="https://www.wireguard.com/install/">How to install?</a>
- Configuration files under **/etc/wireguard**

  ***Example `.conf` file***
  ```
  [Interface]
  Address = 192.168.0.1/24
  SaveConfig = true
  PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
  ListenPort = 12345
  PrivateKey = ABCDEFGHIJKLMNOPQRSTUVWXYZ1234
  
  [Peer]
  PublicKey = HABCDEFGHIJKLMNOPQRSTUVWXYZ123123123123
  AllowedIPs = 192.168.0.2/32
  
  ...
  ```
  **Note: For peers, `PublicKey` & `AllowedIPs` is required.**
- Python 3.7+ & Pip3
  ```
  $ sudo apt-get install python3 python3-pip
  ```

## 🛠 Install

**1. Install Python Dependencies**

```
$ python3 -m pip install flask tinydb
```

**2. Install Wireguard Dashboard**

```
$ git clone https://github.com/donaldzou/Wireguard-Dashboard.git
$ cd Wireguard-Dashboard/src
$ python3 dashboard.py
```

Access your server with port `10086` ! e.g (http://your_server_ip:10086)

**3. Install with Production Mode (Optional), not tested yet. ‼️ Proceed with caution. ‼️**

```
$ cd Wireguard-Dashboard/src
$ export FLASK_APP=dashboard.py
$ export FLASK_RUN_HOST=0.0.0.0
$ export FLASK_ENV=development
$ export FLASK_DEBUG=0
$ flask run
```

## 🔍 Example
![Index Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/index.png)
![Conf Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/configuration.png)

## 🙌 Contributors
<a href="https://github.com/donaldzou/wireguard-dashboard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=donaldzou/wireguard-dashboard" />
</a>

## Contributors ✨

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/antonioag95"><img src="https://avatars.githubusercontent.com/u/30556866?v=4?s=100" width="100px;" alt=""/><br /><sub><b>antonioag95</b></sub></a><br /><a href="https://github.com/donaldzou/wireguard-dashboard/commits?author=antonioag95" title="Tests">⚠️</a> <a href="https://github.com/donaldzou/wireguard-dashboard/commits?author=antonioag95" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
