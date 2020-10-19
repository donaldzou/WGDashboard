# Wireguard Dashboard
## Intro
Monitoring Wireguard is not convinient, need to login into server and type wg show. That's why this platform is being created, to view all configurations in a more straight forward way.
## Installation
**Requirement:**
- Wireguard
- Configuration files under **/etc/wireguard**
- Python 3.7
  - Flask

**Install:**
1. `git clone https://github.com/donaldzou/Wireguard-Dashboard.git`
2. `cd Wireguard-Dashboard`
3. `python3 dashboard.py`
4. Access your server! e.g (http://your_server_ip:10086)

## Example
![Index Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/static/index.png)
![Conf Image](https://github.com/donaldzou/Wireguard-Dashboard/raw/main/static/configuration.png)
