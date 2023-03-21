from dashboard import download_config, connect_db, get_dashboard_conf

config = get_dashboard_conf()
global WG_CONF_PATH
WG_CONF_PATH = config.get("Server", "wg_conf_path")

db = connect_db()
cur = db.cursor()
print(download_config(config_name="config", peer_id="peerid", db=cur)["content"])
