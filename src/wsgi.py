from dashboard import app, get_host_bind

if __name__ == "__main__":
    app_host, app_port = get_host_bind()
    app.run(host=app_host, debug=False, port=app_port)
