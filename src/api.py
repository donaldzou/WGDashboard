import ipaddress, subprocess, datetime, os, util
from util import *

notEnoughParameter = {"status": False, "reason": "Please provide all required parameters."}
good = {"status": True, "reason": ""}


def togglePeerAccess(data, g):
    checkUnlock = g.cur.execute(f"SELECT * FROM {data['config']} WHERE id='{data['peerID']}'").fetchone()
    if checkUnlock:
        moveUnlockToLock = g.cur.execute(
            f"INSERT INTO {data['config']}_restrict_access SELECT * FROM {data['config']} WHERE id = '{data['peerID']}'")
        if g.cur.rowcount == 1:
            print(g.cur.rowcount)
            print(util.deletePeers(data['config'], [data['peerID']], g.cur, g.db))
    else:
        moveLockToUnlock = g.cur.execute(
            f"SELECT * FROM {data['config']}_restrict_access WHERE id = '{data['peerID']}'").fetchone()
        try:
            if len(moveLockToUnlock[-1]) == 0:
                status = subprocess.check_output(
                    f"wg set {data['config']} peer {moveLockToUnlock[0]} allowed-ips {moveLockToUnlock[11]}",
                    shell=True, stderr=subprocess.STDOUT)
            else:
                now = str(datetime.datetime.now().strftime("%m%d%Y%H%M%S"))
                f_name = now + "_tmp_psk.txt"
                f = open(f_name, "w+")
                f.write(moveLockToUnlock[-1])
                f.close()
                subprocess.check_output(
                    f"wg set {data['config']} peer {moveLockToUnlock[0]} allowed-ips {moveLockToUnlock[11]} preshared-key {f_name}",
                    shell=True, stderr=subprocess.STDOUT)
                os.remove(f_name)
            status = subprocess.check_output(f"wg-quick save {data['config']}", shell=True, stderr=subprocess.STDOUT)
            g.cur.execute(
                f"INSERT INTO {data['config']} SELECT * FROM {data['config']}_restrict_access WHERE id = '{data['peerID']}'")
            if g.cur.rowcount == 1:
                g.cur.execute(f"DELETE FROM {data['config']}_restrict_access WHERE id = '{data['peerID']}'")

        except subprocess.CalledProcessError as exc:
            return {"status": False, "reason": str(exc.output.strip())}
    return good


class addConfiguration:
    def AddressCheck(self, data):
        address = data['address']
        address = address.replace(" ", "")
        address = address.split(',')
        amount = 0
        for i in address:
            try:
                ips = ipaddress.ip_network(i, False)
                amount += ips.num_addresses
            except ValueError as e:
                return {"status": False, "reason": str(e)}
        if amount >= 1:
            return {"status": True, "reason": "", "data": f"Total of {amount} IPs"}
        else:
            return {"status": True, "reason": "", "data": f"0 available IPs"}

    def PortCheck(self, data, configs):
        port = data['port']
        if (not port.isdigit()) or int(port) < 1 or int(port) > 65535:
            return {"status": False, "reason": f"Invalid port."}
        for i in configs:
            if i['port'] == port:
                return {"status": False, "reason": f"{port} used by {i['conf']}."}
        checkSystem = subprocess.run(f'ss -tulpn | grep :{port} > /dev/null', shell=True)
        if checkSystem.returncode != 1:
            return {"status": False, "reason": f"Port {port} used by other process in your system."}
        return good

    def NameCheck(self, data, configs):
        name = data['name']
        name = name.replace(" ", "")
        for i in configs:
            if name == i['conf']:
                return {"status": False, "reason": f"{name} already existed."}
        illegal_filename = ["(Space)", " ", ".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2",
                            "com3",
                            "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                            "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
        for i in illegal_filename:
            name = name.replace(i, "")
        if len(name) == 0:
            return {"status": False, "reason": "Invalid name."}
        return good

    def addConfiguration(self, data, configs, WG_CONF_PATH):
        output = ["[Interface]", "SaveConfig = true"]
        required = ['addConfigurationPrivateKey', 'addConfigurationListenPort',
                    'addConfigurationAddress', 'addConfigurationPreUp', 'addConfigurationPreDown',
                    'addConfigurationPostUp', 'addConfigurationPostDown']
        for i in required:
            e = data[i]
            if len(e) != 0:
                key = i.replace("addConfiguration", "")
                o = f"{key} = {e}"
                output.append(o)
        name = data['addConfigurationName']
        illegal_filename = ["(Space)", " ", ".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2",
                            "com3",
                            "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                            "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
        for i in illegal_filename:
            name = name.replace(i, "")

        try:
            newFile = open(f"{WG_CONF_PATH}/{name}.conf", "w+")
            newFile.write("\n".join(output))
        except Exception as e:
            return {"status": False, "reason": str(e)}
        return {"status": True, "reason": "", "data": name}

    def deleteConfiguration(self, data, config, g, WG_CONF_PATH):
        confs = []
        for i in config:
            confs.append(i['conf'])
        print(confs)
        if data['name'] not in confs:
            return {"status": False, "reason": "Configuration does not exist", "data": ""}
        for i in config:
            if i['conf'] == data['name']:
                if i['status'] == "running":
                    try:
                        subprocess.check_output("wg-quick down " + data['name'], shell=True, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as exc:
                        return {"status": False, "reason": "Can't stop peer", "data": str(exc.output.strip().decode("utf-8"))}

            g.cur.execute(f'DROP TABLE {data["name"]}')
            g.cur.execute(f'DROP TABLE {data["name"]}_restrict_access')
            g.db.commit()

            try:
                os.remove(f'{WG_CONF_PATH}/{data["name"]}.conf')
            except Exception as e:
                return {"status": False, "reason": "Can't delete peer", "data": str(e)}

            return good