import re
import subprocess
import dashboard
"""
Helper Functions
"""


# Regex Match
def regex_match(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


# Check IP format
def check_IP(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}$"
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
    return ip.replace(' ', '')


# Clean IP with range
def clean_IP_with_range(ip):
    return clean_IP(ip).split(',')


# Check IP with range
def check_IP_with_range(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|\/)){4}([0-9]{1,2})(,|$)",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}\/([0-9]{1,3})(,|$)"
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
        if not check_IP_with_range(i): return False
    return True


# Check DNS
def check_DNS(dns):
    dns = dns.replace(' ', '').split(',')
    status = True
    for i in dns:
        if not (check_IP(i) or regex_match("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]", i)):
            return False
    return True


# Check remote endpoint
def check_remote_endpoint(address):
    return (check_IP(address) or regex_match("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]",
                                             address))


def deletePeers(config_name, delete_keys, cur, db):
    sql_command = []
    wg_command = ["wg", "set", config_name]
    for delete_key in delete_keys:
        if delete_key not in dashboard.get_conf_peer_key(config_name):
            return "This key does not exist"
        sql_command.append("DELETE FROM " + config_name + " WHERE id = '" + delete_key + "';")
        wg_command.append("peer")
        wg_command.append(delete_key)
        wg_command.append("remove")
    try:
        print("deleting...")
        remove_wg = subprocess.check_output(" ".join(wg_command),
                                            shell=True, stderr=subprocess.STDOUT)
        save_wg = subprocess.check_output(f"wg-quick save {config_name}", shell=True, stderr=subprocess.STDOUT)
        cur.executescript(' '.join(sql_command))
        db.commit()
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()
    return "true"

def checkJSONAllParameter(required, data):
    if len(data) == 0:
        return False
    for i in required:
        if i not in list(data.keys()):
            return False
    return True


