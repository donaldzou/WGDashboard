import re
import os
import wg, db
import sqlite3
import configparser
import time
import ipaddress
from __main__ import app
from operator import itemgetter
from flask import g

"""
Helper Functions
"""


def get_interface_file_path(interface_name: str, base_dir: str) -> str:
    return os.path.join(base_dir, f"{interface_name}.conf")


def adapt_for_rest(peer_dict: dict) -> dict:
    """
    Renames necessary entries and replaces falsy values. Returns the modified dict.
    """
    for i in ["latest_handshake", "endpoint", "allowed_ips"]:
        if not peer_dict[i]:
            peer_dict[i] = "(None)"
    return peer_dict


def connect_db(dashboard_configuration_dir: str):
    """
    Connect to the database
    @return: sqlite3.Connection
    """
    con = sqlite3.connect(
        os.path.join(dashboard_configuration_dir, "db", "wgdashboard.db")
    )
    con.row_factory = sqlite3.Row
    return con


def read_dashboard_conf(dashboard_conf_file_path: str):
    """
    Get dashboard configuration
    @return: configparser.ConfigParser
    """
    r_config = configparser.ConfigParser(strict=False)
    r_config.read(dashboard_conf_file_path)
    return r_config


def write_dashboard_conf(config: str, dashboard_conf_file_path: str):
    """
    Write to configuration
    @param config: Input configuration
    """
    with open(dashboard_conf_file_path, "w", encoding="utf-8") as conf_object:
        config.write(conf_object)


def wg_peer_data_to_db(
    interface_name: str, wg_conf_dir: str, dashboard_conf_file_path: str
):
    """
    Look for new peers from WireGuard
    @param interface_name: Configuration name
    @return: None
    """
    interface_and_peer_data = wg.read_interface_config_file(interface_name, wg_conf_dir)
    config = g.conf
    failed_index = []
    for i in range(len(interface_and_peer_data["Peers"])):
        wg_peer = interface_and_peer_data["Peers"][i]
        if "PublicKey" in wg_peer.keys():
            data = db.get_peer_by_id(
                interface_name, interface_and_peer_data["Peers"][i]["PublicKey"]
            )
            if not data:
                new_data = {
                    "id": interface_and_peer_data["Peers"][i]["PublicKey"],
                    "private_key": "",
                    "DNS": config.get("Peers", "peer_global_DNS"),
                    "endpoint_allowed_ips": config.get(
                        "Peers", "peer_endpoint_allowed_ips"
                    ),
                    "name": "",
                    "total_receive": 0,
                    "total_sent": 0,
                    "total_data": 0,
                    "endpoint": "N/A",
                    "status": "stopped",
                    "latest_handshake": "N/A",
                    "allowed_ips": "N/A",
                    "cumu_receive": 0,
                    "cumu_sent": 0,
                    "cumu_data": 0,
                    "traffic": [],
                    "mtu": config.get("Peers", "peer_mtu"),
                    "keepalive": config.get("Peers", "peer_keep_alive"),
                    "remote_endpoint": config.get("Peers", "remote_endpoint"),
                    "preshared_key": "",
                }
                if "PresharedKey" in interface_and_peer_data["Peers"][i].keys():
                    new_data["preshared_key"] = interface_and_peer_data["Peers"][i][
                        "PresharedKey"
                    ]
                db.insert_peer(interface_name, new_data)
        else:
            print("Trying to parse a peer doesn't have public key...")
            failed_index.append(i)
    for i in failed_index:
        interface_and_peer_data["Peers"].pop(i)

    db.remove_stale_peers(interface_name, interface_and_peer_data)

    handshakes = wg.get_interface_peers_latest_handshakes(interface_name)
    transfers = wg.get_interface_peers_net_stats(interface_name)
    endpoints = wg.get_interface_peers_endpoints(interface_name)
    allowed_ips = wg.get_interface_peers_allowed_ips(interface_and_peer_data)
    keys = set()
    for x in [handshakes, transfers, endpoints, allowed_ips]:
        keys.update(x.keys())
    for id in keys:
        data = {"id": id}
        for x in [handshakes, transfers, endpoints, allowed_ips]:
            try:
                data.update(x[id])
            except KeyError:
                pass
        db.update_peer(interface_name, data)


def update_db_and_get_peers(
    interface_name: str,
    search: str,
    sort_t: str,
    wg_conf_dir: str,
    dashboard_conf_file_path: str,
):
    """
    Get all peers.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @param search: Search string
    @type search: str
    @param sort_t: Sorting tag
    @type sort_t: str
    @return: list
    """
    tic = time.perf_counter()
    wg_peer_data_to_db(interface_name, wg_conf_dir, dashboard_conf_file_path)

    result = list(map(lambda x: dict(x), db.get_peers(interface_name, search)))

    if sort_t == "allowed_ips":
        result = sorted(
            result,
            key=lambda d: ipaddress.ip_network(
                "0.0.0.0/0"
                if d[sort_t].split(",")[0] == "(None)"
                else d[sort_t].split(",")[0]
            ),
        )
    else:
        result = sorted(result, key=lambda d: d[sort_t])

    result = list(map(adapt_for_rest, result))
    toc = time.perf_counter()
    app.logger.debug(f"Finish fetching peers in {toc - tic:0.4f} seconds")
    return result


def get_conf_list(wg_conf_dir: str):
    """Get all wireguard interfaces with status.
    @return: Return a list of dicts with interfaces and its statuses
    @rtype: list
    """

    conf = []
    for interface_name in os.listdir(wg_conf_dir):
        if regex_match("^(.{1,}).(conf)$", interface_name):
            interface_name = interface_name.split(".")[0]
            db.create_table_if_missing(interface_name)
            temp = {
                "conf": interface_name,
                "status": wg.get_interface_status(interface_name),
                "public_key": wg.get_interface_public_key(interface_name, wg_conf_dir),
            }
            if temp["status"] == "running":
                temp["checked"] = "checked"
            else:
                temp["checked"] = ""
            conf.append(temp)
    if len(conf) > 0:
        conf = sorted(conf, key=itemgetter("conf"))
    return conf


def f_check_key_match(private_key: str, public_key: str, interface_name: str):
    """
    Check if private key and public key match
    @param private_key: Private key
    @type private_key: str
    @param public_key: Public key
    @type public_key: str
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return dictionary with status
    @rtype: dict
    """

    result = wg.gen_public_key(private_key)
    if result["status"] == "failed":
        return result
    else:
        id = result["data"]
        db_peer = db.get_peer_by_id(interface_name, id)
        if not db_peer or id != public_key:
            return {
                "status": "failed",
                "msg": "Please check your private key, it does not match with the public key.",
            }
        else:
            return {"status": "success"}


def check_repeat_allowed_ips(public_key: str, ip: str, interface_name: str):
    """
    Check if there are repeated IPs
    @param public_key: Public key of the peer
    @param ip: IP of the peer
    @param interface_name: configuration name
    @return: a JSON object
    """
    db_peer = db.get_peer_by_id(interface_name, public_key)
    if not db_peer:
        return {"status": "failed", "msg": "Peer does not exist"}
    else:
        existing_ips = db.get_peer_count_by_allowed_ips(interface_name, ip, public_key)
        if not existing_ips:
            return {
                "status": "failed",
                "msg": "Allowed IP already taken by another peer.",
            }
        else:
            return {"status": "success"}


def f_available_ips(interface_name: str, wg_conf_dir: str):
    """
    Get a list of available IPs
    @param interface_name: Configuration Name
    @return: list
    """
    config_interface = wg.read_interface_section_from_config_file(
        interface_name, wg_conf_dir
    )
    if "Address" in config_interface:
        existing = set()
        conf_address = config_interface["Address"]
        address = list(map(lambda x: x.strip(), conf_address.split(",")))
        for i in address:
            add = strip_subnet(i)
            existing.add(ipaddress.ip_address(add))
        allowed_ips = db.get_peer_allowed_ips(interface_name)
        for i in allowed_ips:
            add = i[0].split(",")
            for k in add:
                a = strip_subnet(k)
                existing.add(ipaddress.ip_address(a.strip()))
        available = set(ipaddress.ip_network(ensure_subnet(address[0]), False).hosts())
        available -= existing
        available = list(map(lambda x: str(x), sorted(available)))
        return available
    else:
        return []


def strip_subnet(ipv4: str) -> str:
    ipv4 = ipv4.strip()
    try:
        tokens = ipv4.split("/")
        address = tokens[0]
    except:
        address = ipv4
    return address


def ensure_subnet(ipv4: str, default_subnet: str = "24") -> str:
    ipv4 = ipv4.strip()
    try:
        address, subnet = ipv4.split("/")
    except:
        address = ipv4
        subnet = default_subnet
    return f"{address}/{subnet}"


# Regex Match
def regex_match(regex: str, text: str):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


# Check IP format
def check_IP(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}$",
    )
    for match_pattern in ip_patterns:
        match_result = regex_match(match_pattern, ip)
        if match_result:
            result = match_result
            break
    else:
        result = None

    return result


# Clean IP
def clean_IP(ip):
    return ip.replace(" ", "")


# Clean IP with range
def clean_IP_with_range(ip):
    return clean_IP(ip).split(",")


# Check IP with range
def check_IP_with_range(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|\/)){4}([0-9]{1,2})(,|$)",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}\/([0-9]{1,3})(,|$)",
    )

    for match_pattern in ip_patterns:
        match_result = regex_match(match_pattern, ip)
        if match_result:
            result = match_result
            break
    else:
        result = None

    return result


# Check allowed ips list
def check_Allowed_IPs(ip):
    ip = clean_IP_with_range(ip)
    for i in ip:
        if not check_IP_with_range(i):
            return False
    return True


# Check DNS
def check_DNS(dns):
    dns = dns.replace(" ", "").split(",")
    status = True
    for i in dns:
        if not (
            check_IP(i)
            or regex_match(
                "(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]", i
            )
        ):
            return False
    return True


# Check remote endpoint
def check_remote_endpoint(address):
    return check_IP(address) or regex_match(
        "(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]", address
    )
