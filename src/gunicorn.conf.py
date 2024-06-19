import multiprocessing
import dashboard

app_host, app_port = dashboard.gunicornConfig()

worker_class = 'gthread'
workers = 4
threads = 2
bind = f"{app_host}:{app_port}"
daemon = True
pidfile = './gunicorn.pid'