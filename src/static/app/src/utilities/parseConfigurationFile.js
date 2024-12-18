export const parseInterface = (conf) => {
	const lineSplit = conf.split("\n");
	const configuration = {};
	for(let line of lineSplit){
		if( line === "[Peer]") break
		if (line.length > 0){
			let l = line.replace(" = ", "=")
			if (l.indexOf('=') > -1){
				l = [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1)]
				if (l[0] === "ListenPort"){
					configuration[l[0]] = parseInt(l[1])
				}else{
					configuration[l[0]] = l[1]
				}
			}
		}
	}
	return configuration
}

export const parsePeers = (conf) => {
	const lineSplit = conf.split("\n");
	const peers = [];
	let pCounter = -1;
	const firstPeer = lineSplit.indexOf("[Peer]");
	if (firstPeer === -1) return false;
	
	for (let l = firstPeer; l < lineSplit.length; l++){
		if (lineSplit[l] === "[Peer]"){
			pCounter += 1;
			peers.push({})
			peers[pCounter]["name"] = ""
		}else{
			let line = lineSplit[l].replace(" = ", "=")
			if (line.indexOf('=') > -1){
				line = [line.slice(0, line.indexOf('=')), line.slice(line.indexOf('=') + 1)]
				peers[pCounter][line[0]] = line[1]
			}
		}
	}
	return peers;
}