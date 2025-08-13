"""
Update this to fit your need, currently it is 300 seconds
"""
__INTERVAL = 10

def main(WireguardConfigurations: dict = None):
    import os.path
    from time import sleep, time
    import rrdtool

    while True:
        for c in WireguardConfigurations.keys():
            rrd_path = f"./plugins/rrd_data/{c}.rrd"

            if not os.path.exists(rrd_path):
                print(f"Creating RRD for {c}")
                rrdtool.create(
                    rrd_path,
                    '--step', str(__INTERVAL),
                    f'DS:in:COUNTER:{__INTERVAL * 2}:0:U',
                    f'DS:out:COUNTER:{__INTERVAL * 2}:0:U',
                    'RRA:AVERAGE:0.5:1:8640',
                    'RRA:AVERAGE:0.5:12:720',
                    'RRA:AVERAGE:0.5:288:365',
                    'RRA:AVERAGE:0.5:2016:52',
                    'RRA:AVERAGE:0.5:8640:1'
                )

            configuration = WireguardConfigurations[c]
            current_time = int(time())

            json_data = configuration.toJson()
            receive_gb = json_data["DataUsage"]["Receive"]
            sent_gb = json_data["DataUsage"]["Sent"]
            receive_bytes = int(receive_gb * (1024 ** 3))
            sent_bytes = int(sent_gb * (1024 ** 3))

            print(f"{c}: Receive={receive_gb}GB ({receive_bytes} bytes), Sent={sent_gb}GB ({sent_bytes} bytes)")

            update_string = f'{current_time}:{receive_bytes}:{sent_bytes}'
            print(f"Updating {c} with: {update_string}")

            try:
                rrdtool.update(rrd_path, update_string)
                print(f"Successfully updated {c}")
            except Exception as e:
                print(f"Error updating {c}: {e}")

        sleep(__INTERVAL)
    