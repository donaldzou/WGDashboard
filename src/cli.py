import click

from dashboard import download_config, connect_db, get_dashboard_conf, _get_conf_list, _get_peers

class wgdCli:

    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option('-c','--config',required=True)
    @click.option('-p','--peerid',required=True)
    def get_peer_conf(config, peerid):
        print(download_config(config_name=config, peer_id=peerid, db=wgdCli.cur)["content"])

    @cli.command()
    @click.option('-c','--config',required=True)
    @click.option('-p','--peerid',required=True)
    def get_peer_conf_qr(config, peerid):
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(download_config(config_name=config, peer_id=peerid, db=wgdCli.cur)["content"])
        qr.print_ascii()

    def init():
        wgdCli.config = get_dashboard_conf()
        wgdCli.WG_CONF_PATH = wgdCli.config.get("Server", "wg_conf_path")
        wgdCli.db = connect_db()
        wgdCli.cur = wgdCli.db.cursor()

    @cli.command()
    def list_configs():
        cfgs = []
        try:
            cfgs.append(_get_conf_list(wgdCli.WG_CONF_PATH, wgdCli.cur))
        except Exception as e:
            print("error loading configuration files. Did you already configure a service?")
            print("Error:")
            print(e.with_traceback(e.__traceback__))
        
        if len(cfgs) <= 0:
            print("No configuration file found in",wgdCli.WG_CONF_PATH)
        else:
            print("Following configurations are registered:")
            for cfg in cfgs[0]:
                print(f'* {cfg["conf"]} ({cfg["status"]}), port {cfg["port"]}')

    @cli.command()
    @click.option('-c','--config',required=True)
    def list_peers(config):
        print("Peers for configuration",config,":")
        for peer in _get_peers(wgdCli.cur,config):
            print(f"* {peer['name']:>30} ({peer['allowed_ip']:>18}): id {peer['id']}")


if __name__ == '__main__':
    wgdCli.init()
    wgdCli.cli()

