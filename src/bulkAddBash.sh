for ((i = 0 ; i<$1 ; i++ ))
do
        privateKey=$(wg genkey)
        presharedKey=$(wg genkey)
        publicKey=$(wg pubkey <<< "$privateKey")
        echo "$privateKey,$publicKey,$presharedKey"
done