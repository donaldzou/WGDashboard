import multiprocessing
import dashboard

global sqldb, cursor, DashboardConfig, WireguardConfigurations, AllPeerJobs, JobLogger
app_host, app_port = dashboard.gunicornConfig()

worker_class = 'gthread'
workers = 1
threads = 1
bind = f"{app_host}:{app_port}"
print("[WGDashboard] Gunicorn app will be running at " + bind)
daemon = True
pidfile = './gunicorn.pid'
