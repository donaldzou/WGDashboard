from dashboard import DASHBOARD_VERSION

dash_config = {
    "Account": {
        "username": "admin",
        "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
    },
    "Server": {
        "version": DASHBOARD_VERSION,
        "wg_conf_path": "/etc/wireguard",
        "auth_req": True,
        "dashboard_refresh_interval": 60000,
        "dashboard_sort": "status",
        "internal_subnet": "10.13.13.0",
        "app_ip": "0.0.0.0",
        "app_port": 10086,
    },
    "Peers": {
        "peer_global_dns": "10.13.13.1",
        "peer_endpoint_allowed_ips": "0.0.0.0/0",
        "peer_display_mode": "grid",
        "peer_mtu": "1420",
        "peer_keep_alive": "21",
    },
}
