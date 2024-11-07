# WGDashboard Docker Explanation:
Author: DaanSelen<br>

This document delves into how the WGDashboard Docker container has been built.<br>
Of course there are two stages, one before run-time and one at/after run-time.<br>
The `Dockerfile` describes how the container image is made, and the `entrypoint.sh` is executed after running the container. <br>
In this example, WireGuard is integrated into the container itself, so it should be a run-and-go/out-of-the-box.<br>
For more details on the source-code specific to this Docker image, refer to the source files, they have lots of comments.

I have tried to embed some new features such as `isolate` and interface startup on container-start (through `enable`). I hope you enjoy!

<img src="https://raw.githubusercontent.com/donaldzou/WGDashboard/main/src/static/img/logo.png" alt="WG-Dashboard Logo" title="WG-Dashboard Logo" width="150" height="150" /> 

## Getting the container running:

To get the container running you either pull the image from the repository, `donaldzou/wgdashboard:latest`.<br>
From there either use the environment variables describe below as parameters or use the Docker Compose file: `compose.yaml`.<br>
Be careful, the default generated WireGuard configuration file uses port 51820/udp. So use this port if you want to use it out of the box.<br>
Otherwise edit the configuration file in `/etc/wireguard/wg0.conf`.

An example of a simple command to get the container running is show below:<br>

```shell
docker run -d \
  --name wgdashboard \
  --restart unless-stopped \
  -e enable=wg0 \
  -e isolate=wg0 \
  -p 10086:10086/tcp \
  -p 51820:51820/udp \
  --cap-add NET_ADMIN \
  donaldzou/wgdashboard:latest
```
<br>
If you want to use Compose instead of a raw Docker command, refer to the example in the `compose.yaml` or the one pasted below:
<br><br>

```yaml
services:
  wgdashboard:
    image: donaldzou/wgdashboard:latest
    restart: unless-stopped
    container_name: wgdashboard
    environment:
      #- tz= 
      #- global_dns=
      #- enable=
      #- isolate=
      #- public_ip=
    ports:
      - 10086:10086/tcp
      - 51820:51820/udp
    volumes:
      - conf:/etc/wireguard
      - data:/data
    cap_add:
      - NET_ADMIN

volumes:
  conf:
  data:

```

If you want to customize the yaml, make sure the core stays the same, but for example volume PATHs (ON THE HOST) can be freely changed.<br>
This setup is just generic and will use the Docker volumes.

## Updating the container:

Updating is right now in Alpha stage. I have got it to work, testing methods.

## Working with the container and environment variables:

Once the container is running, the installation process is essentially the same as running it on bare-metal.<br>
So go to the assign TCP port in this case HTTP, like the default 10086 one in the example and log into the WEB-GUI.<br>

| Environment variable    | Accepted arguments | Default value | Example value | Verbose |
| -------------- | ------- | ------- | ------- | ------- |
| tz             | Europe/Amsterdam or any confirming timezone notation. | `Europe/Amsterdam` | `America/New_York` | Sets the timezone of the Docker container. This is to timesync the container to any other processes which would need it. |
| global_dns     | Any IPv4 address, such as my personal recommendation: 9.9.9.9 (QUAD9). | `1.1.1.1` | `8.8.8.8` or any IP-Address that resolves DNS-names, and of course is reachable | Set the default DNS given to clients once they connect to the WireGuard tunnel, and for new peers, set to Cloudflare DNS for reliability.
| enable         | Anything, preferably an existing WireGuard interface name. | `none` | `wg0,wg2,wg13` | Enables or disables the starting of the WireGuard interface on container 'boot-up'.
| isolate        | Anything, preferably an existing WireGuard interface name. | `none` | `wg1,wg0` | The Wireguard interface itself IS able to reach the peers (Done through the `iptables` package).
| public_ip      | Any IPv4 (public recommended) address, such as the one returned by default | Default uses the return of `curl ifconfig.me` | `89.20.83.118` | To reach your VPN from outside your own network, you need WG-Dashboard to know what your public IP-address is, otherwise it will generate faulty config files for clients. This happends because it is inside a Docker/Kubernetes container. In or outside of NAT is not relevant as long as the given IP-address is reachable from the internet or the target network.

## Be careful with:

When you are going to work with multiple WireGuard interfaces, you need to also open them up to the Docker host. This done by either adding the port mappings like: `51821:51821/udp` in the Docker Compose file, or to open a range like: `51820-51830:51820-51830/udp`<br>
The latter opens up UDP ports from 51820 to 51830, so all ports in between as well! Be careful, it is good security practise to open only needed ports!

## Building the image yourself:

To build the image yourself, you need to do a couple things:<br>
1. Clone the Github repository containing the source code of WGDashboard including the docker directory. For example do: `git clone https://github.com/donaldzou/WGDashboard.git`
1. Navigate into the cloned repository.
1. (Make sure you have Docker correctly installed, if not: [Click here](https://docs.docker.com/engine/install/)) and run: `docker build . -t <Image name>:<Image tag>` as an example: `docker build . -t dselen/wgdashboard:latest`.<br>
   This will make Docker compile the image from the resources in the directory you mention, in this case the source/root one. Let it compile, it takes only a couple seconds with a minute at most.
1. If all went well, see your image with `docker images`. Example below:

```shell
dselen@dev-mach:~/development/WGDashboard/docker$ docker images
REPOSITORY           TAG       IMAGE ID       CREATED             SIZE
dselen/wgdashboard   latest       c96fd96ee3b3   42 minutes ago      314MB
```

## Closing remarks:

For feedback please submit an issue to the repository. Or message dselen@nerthus.nl.
