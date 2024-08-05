import dashboard
from datetime import datetime
global sqldb, cursor, DashboardConfig, WireguardConfigurations, AllPeerJobs, JobLogger
app_host, app_port = dashboard.gunicornConfig()
date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')


worker_class = 'gthread'
workers = 1
threads = 1
bind = f"{app_host}:{app_port}"
daemon = True
pidfile = './gunicorn.pid'
wsgi_app = "dashboard:app"
access_logfile = f"./log/access_{date}.log"
log_level = "debug"
capture_output = True
error_logfile = f"./log/error_{date}.log"
print(f"[WGDashboard] WGDashboard w/ Gunicorn will be running on {bind}", flush=True)
print(f"[WGDashboard] Access log file is at ./log/{access_logfile}", flush=True)
print(f"[WGDashboard] Error log file is at ./log/{error_logfile}", flush=True)
