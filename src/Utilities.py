import re

def RegexMatch(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None

def GetRemoteEndpoint():
    # Thanks, @NOXICS
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("1.1.1.1", 80))  # Connecting to a public IP
        wgd_remote_endpoint = s.getsockname()[0]
        return str(wgd_remote_endpoint)
    
def ValidateDNSAddress(dns) -> tuple[bool, str]:
    dns = dns.replace(' ', '').split(',')
    for i in dns:
        if not ValidateIPAddress(i) and not RegexMatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]", i):
            return False, f"{i} does not appear to be an valid DNS address"
    return True, ""

def ValidateIPAddress(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}$"
    )
    for match_pattern in ip_patterns:
        match_result = RegexMatch(match_pattern, ip)
        if match_result:
            result = match_result
            break
    else:
        result = None
    return result