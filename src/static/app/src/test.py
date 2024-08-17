import subprocess


def _generateKeyPairs(amount: int) -> list[list[str]] | None:
    try:
        pairs = subprocess.check_output(
            f'''for ((i = 0 ; i<{amount} ; i++ ));do privateKey=$(wg genkey) presharedKey=$(wg genkey) publicKey=$(wg pubkey <<< "$privateKey") echo "$privateKey,$publicKey,$presharedKey"; done''', shell=True, stderr=subprocess.STDOUT
        )
        pairs = pairs.decode().split("\n")
        print(pairs)
        return [x.split(",") for x in pairs]
    except subprocess.CalledProcessError as exp:
        print(str(exp))
        return []


_generateKeyPairs(20)