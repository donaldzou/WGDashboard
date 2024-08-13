import {fetchGet} from "@/utilities/fetch.js";

export class WireguardConfigurations{
	Configurations = undefined;
	constructor() {
		this.Configurations = undefined
	}
	async initialization(){
		await this.getConfigurations()
	}
	

	async getConfigurations(){
		await fetchGet(`{apiUrl}/getWireguardConfigurations`, {}, (res) => {
			if (res.status)  this.Configurations = res.data
		});
	}
}