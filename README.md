<h1 align="center"> Wireguard Dashboard</h1>

<p align="center">
  <img src="http://ForTheBadge.com/images/badges/made-with-python.svg">
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/donaldzou/wireguard-dashboard">
</p>
<p align="center">Monitoring Wireguard is not convinient, need to login into server and type <code>wg show</code>. That's why this platform is being created, to view all configurations in a more straight forward way.</p>

## 💡Features

- Add peers in configuration
- Manage peer names
- Delete peers
- And many more coming up! Welcome to contribute to this project!

## 📝Requirement

- Ubuntu 18.04.1 LTS, other OS might work, but haven't test yet.
- ‼️ Make sure you have **Wireguard** installed.‼️  <a href="https://www.wireguard.com/install/">How to install?</a>
- Configuration files under **/etc/wireguard**
- Python 3.7

## 🛠Install



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

**3. Install with Production Mode (Optional)**

```
$ cd Wireguard-Dashboard/src
$ export FLASK_APP=dashboard.py
$ export FLASK_RUN_HOST=0.0.0.0
$ export FLASK_ENV=development
$ export FLASK_DEBUG=0
$ flask run
```

## 🔍Example
![Index Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/index.png)
![Conf Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/src/static/configuration.png)

## 🙌Contributors
<a href="https://github.com/donaldzou/wireguard-dashboard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=donaldzou/wireguard-dashboard" />
</a>
