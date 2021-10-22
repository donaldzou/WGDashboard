import dashboard

app_host, app_port = dashboard.get_host_bind()
bind = f"{app_host}:{app_port}"
daemon = True
pidfile = './gunicorn.pid'
