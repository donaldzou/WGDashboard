from flask import g
from dashboard import app
import sqlite3


def get_net_stats(interface_name: str) -> list[sqlite3.Row]:
    """
    Gets net stats for all peers of `interface_name` and returns a list of dicts
    """
    app.logger.debug(f"db.get_net_stats({interface_name})")
    data = g.cur.execute(
        f"SELECT total_sent, total_receive, cumu_sent, cumu_receive FROM {interface_name}"
    )
    return data.fetchall()


def get_net_stats_and_peer_status(interface_name: str, id: str) -> sqlite3.Row | None:
    """
    Gets net stats for a given peer of `interface_name` and the data as `dict`, `None` if not found.
    """
    app.logger.debug(f"db.get_net_stats_and_peer_status({interface_name})")
    data = g.cur.execute(
        """SELECT total_receive, total_sent, cumu_receive, cumu_sent, status 
           FROM %s WHERE id='%s'"""
        % (interface_name, id)
    )
    return data.fetchone()


def get_peer_count_by_allowed_ips(
    interface_name: str, ip: str, id: str
) -> sqlite3.Row | None:
    """
    Gets and returns the number of peers of `interface_name` that have allowed_ips similar to `ip`.
    """
    app.logger.debug(f"db.get_peer_count_by_allowed_ips({interface_name}, {ip}, {id})")
    data = g.cur.execute(
        f"""SELECT COUNT(*) FROM {interface_name} 
            WHERE id != :id AND allowed_ips LIKE :ip""",
        {"id": id, "ip": ip},
    )
    return data.fetchone()


def get_peers(interface_name: str, search: str = None) -> list[sqlite3.Row]:
    """Returns the list of records which name matches the search string, or all if no search is provided"""

    app.logger.debug(f"db.get_peers({interface_name}, {search})")
    sql = f"SELECT * FROM {interface_name}"
    if search:
        sql += f" WHERE name LIKE '%{search}%'"
    else:
        sql = "SELECT * FROM " + interface_name + " WHERE name LIKE '%" + search + "%'"
    data = g.cur.execute(sql)
    return data.fetchall()


def get_peer_by_id(interface_name: str, id: str) -> sqlite3.Row | None:
    """
    Returns the peer of `interface_name` matching `id` or None.
    """

    app.logger.debug(f"db.get_peer_by_id({interface_name}, {id})")
    sql = "SELECT * FROM %s WHERE id='%s'" % (interface_name, id)
    data = g.cur.execute(sql)
    return data.fetchone()


def get_peer_allowed_ips(interface_name: str) -> list[sqlite3.Row]:
    """
    Returns the `allowed_ips` of all peers of `interface_name`.
    """
    app.logger.debug(f"db.get_peer_allowed_ips({interface_name})")
    sql = f"SELECT allowed_ips FROM {interface_name}"
    data = g.cur.execute(sql)
    return data.fetchall()


def get_peer_ids(interface_name: str) -> list[sqlite3.Row]:
    """
    Returns the `id`s of all peers of `interface_name`.
    """
    app.logger.debug(f"db.get_peer_ids({interface_name})")
    data = g.cur.execute("SELECT id FROM %s" % interface_name)
    return data.fetchall()


def remove_stale_peers(interface_name: str, peer_data: dict):
    """
    Removes from the DB entries that are present there, but not in `peer_data`
    """

    app.logger.debug(f"db.remove_stale_peers({interface_name}, peer_data)")
    db_key = set(map(lambda a: a[0], get_peer_ids(interface_name)))
    wg_key = set(map(lambda a: a["PublicKey"], peer_data["Peers"]))
    app.logger.debug(f"db_key: {db_key}")
    app.logger.debug(f"wg_key: {wg_key}")
    for id in db_key - wg_key:
        delete_peer(interface_name, id)


def delete_peer(interface_name: str, id: str):
    """
    Removes a peer of `interface_name` with the given `id`
    """
    app.logger.debug(f"db.delete_peer({interface_name}, {id})")
    sql = "DELETE FROM %s WHERE id = '%s'" % (interface_name, id)
    g.cur.execute(sql)


def insert_peer(interface_name: str, data: dict):
    """
    Inserts a peer of `interface_name` with the given `data`
    """
    app.logger.debug(f"db.insert_peer({interface_name}, {data})")
    sql = f"""
    INSERT INTO {interface_name} 
        VALUES (:id, :private_key, :DNS, :endpoint_allowed_ips, :name, :total_receive, :total_sent, 
        :total_data, :endpoint, :status, :latest_handshake, :allowed_ips, :cumu_receive, :cumu_sent, 
        :cumu_data, :mtu, :keepalive, :remote_endpoint, :preshared_key);
    """
    g.cur.execute(sql, data)


def create_table_if_missing(interface_name: str):
    """
    Creates a table for `interface_name`, if missing.
    """
    app.logger.debug(f"db.create_table_if_missing({interface_name})")
    create_table = f"""
        CREATE TABLE IF NOT EXISTS {interface_name} (
            id VARCHAR NOT NULL PRIMARY KEY, private_key VARCHAR NULL, DNS VARCHAR NULL, 
            endpoint_allowed_ips VARCHAR NULL, name VARCHAR NULL, total_receive FLOAT NULL, 
            total_sent FLOAT NULL, total_data FLOAT NULL, endpoint VARCHAR NULL, 
            status VARCHAR NULL, latest_handshake VARCHAR NULL, allowed_ips VARCHAR NULL, 
            cumu_receive FLOAT NULL, cumu_sent FLOAT NULL, cumu_data FLOAT NULL, mtu INT NULL, 
            keepalive INT NULL, remote_endpoint VARCHAR NULL, preshared_key VARCHAR NULL
        )
    """
    g.cur.execute(create_table)


def update_peer(interface_name: str, data: dict):
    """
    Updates the peer of `interface_name` with the given `data`, if the peer record exists.
    """
    app.logger.debug(f"db.interface_name({data})")
    id = data["id"]
    db_peer = get_peer_by_id(interface_name, id)
    if db_peer:
        db_peer = dict(db_peer)
        db_peer.update(data)
        _update_peer(interface_name, db_peer)


def _update_peer(interface_name: str, data: dict):
    """
    Updates the peer of `interface_name` with the given `data`.
    `data` should contain the peer's `id` (public key), plus any other field to be updated.
    """
    app.logger.debug(f"db.update_peer({interface_name}, {data})")
    sql = f"""
    UPDATE {interface_name} SET     
    private_key=:private_key, DNS=:DNS, endpoint_allowed_ips=:endpoint_allowed_ips, name=:name, 
    total_receive=:total_receive, total_sent=:total_sent,  total_data=:total_data, endpoint=:endpoint, status=:status,
    latest_handshake=:latest_handshake, allowed_ips=:allowed_ips, cumu_receive=:cumu_receive, cumu_sent=:cumu_sent, 
    cumu_data=:cumu_data, mtu=:mtu, keepalive=:keepalive, remote_endpoint=:remote_endpoint, preshared_key=:preshared_key
    WHERE id = :id
    """
    g.cur.execute(sql, data)
