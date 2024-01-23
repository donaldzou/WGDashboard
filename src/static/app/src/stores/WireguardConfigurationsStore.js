import {defineStore} from "pinia";
import {fetchGet} from "@/utilities/fetch.js";

export const WireguardConfigurationsStore = defineStore('WireguardConfigurationsStore', {
	state: () => ({
		Configurations: undefined
	}),
	actions: {
		async getConfigurations(){
			await fetchGet("/api/getWireguardConfigurations", {}, (res) => {
				if (res.status)  this.Configurations = res.data
			});
		}
	}
});