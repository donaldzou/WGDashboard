from dashboard import app
import subprocess
from datetime import datetime, timedelta
import configparser
import db
import os
import ifcfg
import re
import util


def _is_comment_line(line: str) -> bool:
    """
    Returns true if the passed string is a comment in an INI style file.
    """
    line = line.strip()
    return line.startswith("#") or line.startswith(";")


def _parse_peer_or_interface(lines: list[str], i: int, limit: int) -> dict:
    """
    Parses a [Peer] or [Interface] section of an interface config file into a `dict`.
    """
    data = {}
    while i < limit:
        line = lines[i].strip()
        if line.startswith("[Peer]") or line.startswith("[Interface]"):
            break
        if not _is_comment_line(line):
            tmp = re.split(r"\s*=\s*", line, 1)
            if len(tmp) == 2:
                data[tmp[0]] = tmp[1]
        i += 1
    return data, i - 1


def set_peer_options(
    interface_name: str,
    public_key: str,
    allowed_ips: str,
    preshared_key_filename: str = None,
):
    """
    Sets the given options for the specified `interface_name` and peer (`public_key`)
    """
    if preshared_key_filename:
        subprocess.check_output(
            f"wg set {interface_name} peer {public_key} allowed-ips {allowed_ips} preshared-key {preshared_key_filename}",
            shell=True,
            stderr=subprocess.STDOUT,
        )
    else:
        subprocess.check_output(
            f"wg set {interface_name} peer {public_key} allowed-ips {allowed_ips}",
            shell=True,
            stderr=subprocess.STDOUT,
        )


def remove_peer_from_interface(interface_name: str, public_key: str):
    """
    Removes the specified peer (`public_key`) from `interface_name`
    """
    subprocess.check_output(
        f"wg set {interface_name} peer {public_key} remove",
        shell=True,
        stderr=subprocess.STDOUT,
    )


def get_interface_listen_port(interface_name: str, base_dir: str) -> str:
    """
    Get listen port number.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return number of port or empty string
    @rtype: str
    """

    conf = configparser.ConfigParser(strict=False)
    conf.read(base_dir + "/" + interface_name + ".conf")
    port = ""
    try:
        port = conf.get("Interface", "ListenPort")
    except (configparser.NoSectionError, configparser.NoOptionError):
        if get_interface_status(interface_name) == "running":
            port = subprocess.check_output(
                f"wg show {interface_name} listen-port",
                shell=True,
                stderr=subprocess.STDOUT,
            )
            port = port.decode("UTF-8")
    conf.clear()
    return port


def get_interface_public_key(interface_name: str, base_dir: str) -> str:
    """
    Get public key for configuration.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return public key or empty string
    @rtype: str
    """

    try:
        conf = configparser.ConfigParser(strict=False)
        conf.read(base_dir + "/" + interface_name + ".conf")
        pri = conf["Interface"]["PrivateKey"]
        pub = subprocess.check_output(
            f"echo '{pri}' | wg pubkey", shell=True, stderr=subprocess.STDOUT
        )
        conf.clear()
        return pub.decode().strip("\n")
    except configparser.NoSectionError:
        return ""


def get_interface_total_net_stats(interface_name):
    """
    Get configuration's total amount of data
    @param interface_name: Configuration name
    @return: list
    """
    data = db.get_net_stats(interface_name)
    upload_total = 0
    download_total = 0
    for i in data:
        upload_total += i["total_sent"]
        download_total += i["total_receive"]
        upload_total += i["cumu_sent"]
        download_total += i["cumu_receive"]
    total = round(upload_total + download_total, 4)
    upload_total = round(upload_total, 4)
    download_total = round(download_total, 4)
    return [total, upload_total, download_total]


def get_interface_status(interface_name: str) -> str:
    """
    Check if the configuration is running or not
    @param interface_name:
    @return: Return a string indicate the running status
    """
    ifconfig = dict(ifcfg.interfaces().items())
    return "running" if interface_name in ifconfig.keys() else "stopped"


def get_interface_running_peer_count(interface_name: str) -> int | str:
    """
    Get number of running peers on wireguard interface.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Number of running peers, or test if configuration not running
    @rtype: int, str
    """

    running = 0
    # Get latest handshakes
    try:
        data_usage = subprocess.check_output(
            f"wg show {interface_name} latest-handshakes",
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    time_delta = timedelta(minutes=2)
    for _ in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < time_delta:
            running += 1
        count += 2
    return running


# Get all keys from a configuration
def get_interface_peer_public_keys(interface_name) -> list | str:
    """
    Get the peers keys of wireguard interface.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return list of peers keys or text if configuration not running
    @rtype: list, str
    """

    try:
        peers_keys = subprocess.check_output(
            f"wg show {interface_name} peers", shell=True, stderr=subprocess.STDOUT
        )
        peers_keys = peers_keys.decode("UTF-8").split()
        return peers_keys
    except subprocess.CalledProcessError:
        return interface_name + " is not running."


def read_interface_section_from_config_file(interface_name: str, base_dir: str) -> dict:
    """
    Get interface settings.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Dictionary with interface settings
    @rtype: dict
    """

    result = read_interface_config_file(interface_name, base_dir)
    return result["Interface"]


def read_interface_config_file(interface_name: str, base_dir: str) -> dict:
    """
    Get configurations from file of wireguard interface.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Dictionary with interface and peers settings
    @rtype: dict
    """
    app.logger.debug(f"read_conf_file({interface_name})")

    config_file = util.get_interface_file_path(interface_name, base_dir)
    with open(config_file, "r", encoding="utf-8") as file_object:
        file = list(file_object.readlines())
    result = {"Interface": {}, "Peers": []}
    i = 0
    limit = len(file)
    while i < limit:
        line = file[i].strip()
        if line.startswith("[Peer]"):
            app.logger.debug("Found a [Peer]")
            peer, x = _parse_peer_or_interface(file, i + 1, limit)
            result["Peers"].append(peer)
        elif line.startswith("[Interface]"):
            app.logger.debug("Found an [Interface]")
            interface, x = _parse_peer_or_interface(file, i + 1, limit)
            result["Interface"] = interface
        i += 1

    # Read Configuration File End
    return result


def switch_interface(interface_name: str, base_dir: str):
    """
    Switches `interface_name` around (up if it is down, down if it is up)
    """
    config_file = util.get_interface_file_path(interface_name, base_dir)
    status = get_interface_status(interface_name)
    if status == "running":
        check = subprocess.check_output(
            "wg-quick down " + config_file, shell=True, stderr=subprocess.STDOUT
        )
    elif status == "stopped":
        subprocess.check_output(
            "wg-quick up " + config_file, shell=True, stderr=subprocess.STDOUT
        )


def enable_interface(interface_name: str, base_dir: str):
    """
    Brings `interface_name` up (enables it)
    """
    config_file = util.get_interface_file_path(interface_name, base_dir)
    check = subprocess.check_output(
        "wg-quick up " + config_file, shell=True, stderr=subprocess.STDOUT
    )


def disable_interface(interface_name: str, base_dir: str):
    """
    Brings `interface_name` down (disables it)
    """
    config_file = util.get_interface_file_path(interface_name, base_dir)
    check = subprocess.check_output(
        "wg-quick down " + config_file, shell=True, stderr=subprocess.STDOUT
    )


def get_interface_peers_latest_handshakes(interface_name) -> dict:
    """
    Get the latest handshake from all peers of a configuration
    @param interface_name: Configuration name
    @return: str
    """

    result = {}

    # Get latest handshakes
    try:
        data_usage = subprocess.check_output(
            f"wg show {interface_name} latest-handshakes",
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        return result
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    time_delta = timedelta(minutes=2)
    for _ in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < time_delta:
            status = "running"
        else:
            status = "stopped"
        if int(data_usage[count + 1]) > 0:
            peer_id = data_usage[count]
            result[peer_id] = {
                "latest_handshake": str(minus).split(".", maxsplit=1)[0],
                "status": status,
            }
        else:
            peer_id = data_usage[count]
            result[peer_id] = {"latest_handshake": None, "status": status}
        count += 2

    return result


def get_interface_peers_net_stats(interface_name: str) -> dict:
    """
    Get transfer from all peers of a configuration
    @param interface_name: Configuration name
    @return: str
    """

    result = {}
    # Get transfer
    try:
        data_usage = subprocess.check_output(
            f"wg show {interface_name} transfer", shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return result
    data_usage = data_usage.decode("UTF-8").split("\n")
    final = []
    for i in data_usage:
        final.append(i.split("\t"))
    data_usage = final
    for i in range(len(data_usage)):
        peer_id = data_usage[i][0]
        result[peer_id] = {}
        peer_stats = db.get_net_stats_and_peer_status(interface_name, peer_id)
        if peer_stats:
            total_sent = peer_stats["total_sent"]
            total_receive = peer_stats["total_receive"]
            cur_total_sent = round(int(data_usage[i][2]) / (1024**3), 4)
            cur_total_receive = round(int(data_usage[i][1]) / (1024**3), 4)
            if peer_stats["status"] == "running":
                if total_sent <= cur_total_sent and total_receive <= cur_total_receive:
                    total_sent = cur_total_sent
                    total_receive = cur_total_receive
                else:
                    cumulative_receive = peer_stats["cumu_receive"] + total_receive
                    cumulative_sent = peer_stats["cumu_sent"] + total_sent
                    result[peer_id].update(
                        {
                            "cumu_receive": round(cumulative_receive, 4),
                            "cumu_sent": round(cumulative_sent, 4),
                            "cumu_data": round(cumulative_sent + cumulative_receive, 4),
                        }
                    )

                result[peer_id].update(
                    {
                        "total_receive": round(total_receive, 4),
                        "total_sent": round(total_sent, 4),
                        "total_data": round(total_receive + total_sent, 4),
                    }
                )

                total_sent = 0
                total_receive = 0
    return result


def quick_save_interface_config(interface_name: str, base_dir: str):
    """
    Executes `wg-quick save` for `interface_name`
    """
    config_file = util.get_interface_file_path(interface_name, base_dir)
    status = subprocess.check_output(
        "wg-quick save " + config_file, shell=True, stderr=subprocess.STDOUT
    )


def gen_public_key(private_key: str):
    """Generate the public key.

    @param private_key: Private key
    @type private_key: str
    @return: Return dict with public key or error message
    @rtype: dict
    """

    with open("private_key.txt", "w", encoding="utf-8") as file_object:
        file_object.write(private_key)
    try:
        subprocess.check_output(
            "wg pubkey < private_key.txt > public_key.txt", shell=True
        )
        with open("public_key.txt", encoding="utf-8") as file_object:
            public_key = file_object.readline().strip()
        os.remove("private_key.txt")
        os.remove("public_key.txt")
        return {"status": "success", "msg": "", "data": public_key}
    except subprocess.CalledProcessError:
        os.remove("private_key.txt")
        return {
            "status": "failed",
            "msg": "Key is not the correct length or format",
            "data": "",
        }


def get_interface_peers_endpoints(interface_name: str) -> dict:
    """
    Get endpoint from all peers of a configuration
    @param interface_name: Configuration name
    @return: str
    """
    result = {}

    # Get endpoint
    try:
        data_usage = subprocess.check_output(
            f"wg show {interface_name} endpoints", shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return result
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for _ in range(int(len(data_usage) / 2)):
        peer_id = data_usage[count]
        result[peer_id] = {"endpoint": data_usage[count + 1]}
        count += 2
    return result


def get_interface_peers_allowed_ips(conf_peer_data: str) -> dict:
    """
    Get allowed ips from all peers of a configuration
    @param conf_peer_data: Configuration peer data
    @param interface_name: Configuration name
    @return: None
    """
    # Get allowed ip
    data = {}
    for i in conf_peer_data["Peers"]:
        peer_id = i["PublicKey"]
        data[peer_id] = {"allowed_ips": i.get("AllowedIPs", "(None)")}
    return data
