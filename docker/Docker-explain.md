# WG-Dashboard Docker Explanation:

Author: DaanSelen<br>

This document delves into how the WG-Dashboard Docker container has been built.<br>
Of course there are two stages, one before run-time and one at/after run-time.<br>
The `Dockerfile` describes how the container image is made, and the `entrypoint.sh` is executed after running the container. <br>
In this example, WireGuard is integrated into the container itself, so it should be a run-and-go.<br>
For more details on the source-code specific to this Docker image, refer to the source files, they have lots of comments.

I have tried to embed some new features such as `isolated_peers` and interface startup on container-start (through `enable_wg0`).

<img src="https://raw.githubusercontent.com/donaldzou/WGDashboard/main/img/logo.png" alt="WG-Dashboard Logo" title="WG-Dashboard Logo" width="150" height="150" /> 

## Getting the container running:

To get the container running you either pull the image from the repository, at the moment: `repo.nerthus.nl/app/wireguard-dashboard:latest`.<br>
From there either use the environment variables describe below as parameters or use the Docker Compose file: `compose.yaml`.

An example of a simple command to get the container running is show below:<br>

```shell
docker run -d \
  --name wireguard-dashboard \
  --restart unless-stopped \
  -e enable_wg0=true \
  -e isolated_peers=true \
  -p 10086:10086/tcp \
  -p 51820:51820/udp \
  --cap-add NET_ADMIN \
  repo.nerthus.nl/app/wireguard-dashboard:latest
```
<br>
If you want to use Compose instead of a raw Docker command, refer to the example in the `compose.yaml` or the one pasted below:
<br><br>

```yaml
services:
  wireguard-dashboard:
    image: repo.nerthus.nl/app/wireguard-dashboard:latest
    restart: unless-stopped
    container_name: wire-dash
    environment:
      #- tz=
      #- global_dns=
      - enable_wg0=true
      - isolated_peers=false
      #- public_ip=
    ports:
      - 10086:10086/tcp
      - 51820:51820/udp
    volumes:
      - conf:/etc/wireguard
      - app:/opt/wireguarddashboard/app
    cap_add:
      - NET_ADMIN

volumes:
  conf:
  app:

```

If you want to customize the yaml, make sure the core stays the same, but for example volume PATHs can be freely changed.<br>
This setup is just generic and will use the Docker volumes.

## Working with the container and environment variables:

Once the container is running, the installation process is essentially the same as running it on bare-metal.<br>
So go to the assign TCP port in this case HTTP, like the default 10086 one in the example and log into the WEB-GUI.<br>

| Environment variable    | Accepted arguments | Default value | Verbose |
| -------------- | ------- | ------- | ------- |
| tz             | Europe/Amsterdam or any confirming timezone notation. | Europe/Amsterdam | Sets the timezone of the Docker container. This is to timesync the container to any other processes which would need it. |
| global_dns     | Any IPv4 address, such as my personal recommendation: 9.9.9.9 (QUAD9) | 1.1.1.1 | Set the default DNS given to clients once they connect to the WireGuard tunnel (VPN).
| enable_wg0     | `true` or `false` | `false` | Enables or disables the starting of the WireGuard interface on container 'boot-up'.
| isolated_peers | `true` or `false` | `true` | For security the default is true, and it disables peers to ping or reach eachother, the WireGuard interface IS able to reach the peers (Done through `iptables`).
| public_ip      | Any IPv4 (public recommended) address, such as the one returned by default | Default uses the return of `curl ifconfig.me` | To reach your VPN from outside your own network, you need WG-Dashboard to know what your public IP-address is, otherwise it will generate faulty config files for clients.

## Closing remarks:

For feedback please submit an issue to the repository. Or message dselen@nerthus.nl.
