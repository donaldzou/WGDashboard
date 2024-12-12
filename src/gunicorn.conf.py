import os.path

import dashboard, configparser
from datetime import datetime

global sqldb, cursor, DashboardConfig, WireguardConfigurations, AllPeerJobs, JobLogger
app_host, app_port = dashboard.gunicornConfig()
date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')

def post_worker_init(worker):
    dashboard.startThreads()

worker_class = 'gthread'
workers = 1
threads = 1
bind = f"{app_host}:{app_port}"
daemon = True
pidfile = './gunicorn.pid'
wsgi_app = "dashboard:app"
accesslog = f"./log/access_{date}.log"
log_level = "debug"
capture_output = True
errorlog = f"./log/error_{date}.log"

if os.path.exists("./ssl-tls.ini"):
    sslConfig = configparser.ConfigParser()
    sslConfig.read_file(open('./ssl-tls.ini', 'r'))
    if sslConfig.has_section('SSL/TLS'):
        cert = sslConfig.get('SSL/TLS', 'certificate_path')
        pem = sslConfig.get('SSL/TLS', 'private_key_path')
        if cert and pem and len(cert) > 0 and len(pem) > 0:
            certfile = cert
            keyfile = pem
            print(f"[Gunicorn][HTTPS] Found certificate and private key file", flush=True)
            print(f"[Gunicorn][HTTPS] Certificate: ${certfile}", flush=True)
            print(f"[Gunicorn][HTTPS] Private Key: ${keyfile}", flush=True)
       

print(f"[Gunicorn] WGDashboard w/ Gunicorn will be running on {bind}", flush=True)
print(f"[Gunicorn] Access log file is at {accesslog}", flush=True)
print(f"[Gunicorn] Error log file is at {errorlog}", flush=True)
