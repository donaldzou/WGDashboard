# WG-Dashboard Docker Explanation:

  

Author: Noxcis<br>

  

This document delves into how the WG-Dashboard Docker container has been built.<br>
The Image is  two stage docker build based on alpine where psutil and bcrypt are compiled in the first stage before being copied to the final stage. This is done to maintain a small image footprint as bcrypt and psutil require gcc and supporting libraries.

The `Dockerfile` describes how the container image is made, and the `entrypoint.sh` is executed to run the container. <br>

In this example, WireGuard is integrated into the container itself, so it is a compose up and done.<br>

For more details on the source-code specific to this Docker image, refer to the source files, google, stackedit, reddit & ChatGPT until your curiosity is satisfied.

  


<img  src="https://raw.githubusercontent.com/donaldzou/WGDashboard/main/img/logo.png"  alt="WG-Dashboard Logo"  title="WG-Dashboard Logo"  width="150"  height="150"  />

  

## Getting the container running:

  

To get the container running you either pull the image from the repository, at the moment: `noxcis/wgdashboard:4.0.2`. **Check DockerHub For Updated Tags**<br>

From there either use the environment variables describe below as parameters or use the Docker Compose file: `compose.yaml`.

  

An example of a simple command to get the container running is show below:<br>

  

```shell

docker run -d \
  --name wg-dashboard \
  --cap-add NET_ADMIN \
  --cap-add SYS_MODULE \
  --restart unless-stopped \
  -e WGD_USER=admin \
  -e WGD_PASS=admin \
  -e WGD_NET=10.0.0.1/24 \
  -e WGD_PORT=51820 \
  -e WGD_APP_PORT=10086 \
  -e WGD_REMOTE_ENDPOINT=0.0.0.0 \
  -e WGD_DNS="1.1.1.1, 1.0.0.1" \
  -e WGD_PEER_ENDPOINT_ALLOWED_IP=0.0.0.0/0 \
  -e WGD_KEEP_ALIVE=21 \
  -e WGD_MTU=1420 \
  -e WGD_WELCOME_SESSION=false \
  -v wgd_configs:/etc/wireguard \
  -v wgd_app:/opt/wireguarddashboard/src \
  -p 10086:10086/tcp \
  -p 51820:51820/udp \
  --sysctl net.ipv4.ip_forward=1 \
  --sysctl net.ipv4.conf.all.src_valid_mark=1 \
  noxcis/wgdashboard:4.0.2

```

<br>

If you want to use Compose instead of a raw Docker command, refer to the example in the `compose.yaml` or the one pasted below:
<br><br>
```yaml

services:
wireguard-dashboard:
# build: ./ #Uncomment & comment out line below to build your own Image 
image: noxcis/wgdashboard:4.0.2
container_name: wg-dashboard
cap_add:
- NET_ADMIN
- SYS_MODULE
restart: unless-stopped
environment:
- WGD_USER=admin
- WGD_PASS=admin
- WGD_NET=10.0.0.1/24
- WGD_PORT=51820
- WGD_APP_PORT=10086
- WGD_REMOTE_ENDPOINT=0.0.0.0
- WGD_DNS="1.1.1.1, 1.0.0.1"
- WGD_PEER_ENDPOINT_ALLOWED_IP=0.0.0.0/0
- WGD_KEEP_ALIVE=21
- WGD_MTU=1420
- WGD_WELCOME_SESSION=false  #set to true for welcome setup
volumes:
- wgd_configs:/etc/wireguard
- wgd_app:/opt/wireguarddashboard/src
ports:
- 10086:10086/tcp
- 51820:51820/udp
# Add Port Map for New Configs and Restart Container to Apply
sysctls:
- net.ipv4.ip_forward=1
- net.ipv4.conf.all.src_valid_mark=1

  

volumes:
wgd_configs:
wgd_app:
  
```

  

If you want to customize the yaml, make sure to adjust your ports accordingly in respect to the dashboard and your wireguard configs. Your Wireguard & Dashboard Config will persist across container updates as long as the wgd_configs & wdg_app volumes are not deleted. 
**TIPS**
	

> The Dashboard can be reset by deleting the **wgd_app** volume while maintaining configs and peers in the **wgd_configs** volume.


This setup is meant to be persistent and can be made ephemeral for development purpose or etc, by commenting out the docker volume section.

  

## Working with the container and environment variables:
| Environment variable | Default value | Example |
| -------------- | ------- | ------- | 
|WGD_USER           											| 	admin						|	james		|
|WGD_PASS            											| 	admin						|  ScottsMan49	|
|WGD_NET              											|	10.0.0.1/24			|  10.0.2.0/24		|
|WGD_PORT           											|	51820						|   4201		|
|WGD_APP_PORT  											|	10086						|	8000		|
|WGD_REMOTE_ENDPOINT 							|	0.0.0.0					|   localhost		|
|WGD_DNS														|	"1.1.1.1, 1.0.0.1" 	|	"8.8.8.8, 8.8.4.4" |
|WGD_PEER_ENDPOINT_ALLOWED_IP		|	0.0.0.0/0 |192.168.15.0/24, 10.0.1.0/24		|
|WGD_KEEP_ALIVE											|	21							|	0						
|WGD_MTU														|	1420						|	1412
|WGD_WELCOME_SESSION							|	false						|	 true		

  

## Closing remarks:
For feedback please submit an issue to the repository. Or message dselen@nerthus.nl.