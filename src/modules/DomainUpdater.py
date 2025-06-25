"""Domain and IP update utilities"""
import os
import socket
import sqlite3
from typing import List

def update_domains(db_path: str):
    """Update domain IP list and database endpoint_allowed_ip field."""
    os.makedirs(db_path, exist_ok=True)
    domain_file = os.path.join(db_path, 'list_domains.txt')
    ip_file = os.path.join(db_path, 'list_ip.txt')
    combined_file = os.path.join(db_path, 'list.txt')
    target_ip_file = os.path.join(db_path, 'target_ip.txt')
    database = os.path.join(db_path, 'wgdashboard.db')

    # Read domains
    domains: List[str] = []
    if os.path.isfile(domain_file):
        with open(domain_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    domains.append(line)

    # Resolve IPs for domains
    ips: List[str] = []
    for d in domains:
        ip = ''
        try:
            ip = socket.gethostbyname(d)
        except Exception:
            pass
        ips.append(ip)

    # Write IP list
    with open(ip_file, 'w', encoding='utf-8') as f:
        for idx, ip in enumerate(ips, start=1):
            f.write(f"{idx}.{ip}\n")

    # Write combined list
    with open(combined_file, 'w', encoding='utf-8') as f:
        for idx, (d, ip) in enumerate(zip(domains, ips), start=1):
            f.write(f"{idx}.{d} - {ip}\n")

    # Build target IP list from database
    all_ips: List[str] = []
    if os.path.isfile(database):
        try:
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            rows = cur.execute("SELECT endpoint_allowed_ip FROM wg0").fetchall()
            for r in rows:
                if r[0]:
                    parts = [p.strip() for p in r[0].split(',') if p.strip()]
                    all_ips.extend(parts)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    all_ips.extend([ip for ip in ips if ip])

    # Deduplicate
    unique_ips: List[str] = []
    for ip in all_ips:
        if ip not in unique_ips:
            unique_ips.append(ip)

    final_ips = ','.join(unique_ips)

    # Write target_ip.txt
    with open(target_ip_file, 'w', encoding='utf-8') as f:
        f.write(final_ips)

    # Update database
    if os.path.isfile(database):
        try:
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute("UPDATE wg0 SET endpoint_allowed_ip = ?", (final_ips,))
            conn.commit()
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
