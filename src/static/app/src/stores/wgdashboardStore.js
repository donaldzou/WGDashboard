import {defineStore} from "pinia";
import {fetchGet} from "@/utilities/fetch.js";

export const wgdashboardStore = defineStore('WGDashboardStore', {
	state: () => ({ 
		WireguardConfigurations: undefined,
		DashboardConfiguration: undefined
	}),
	actions: {
		async getWireguardConfigurations(){
			await fetchGet("/api/getWireguardConfigurations", {}, (res) => {
				console.log(res.status)
				if (res.status)  this.WireguardConfigurations = res.data
			})
		},
		async getDashboardConfiguration(){
			await fetchGet("/api/getDashboardConfiguration", {}, (res) => {
				console.log(res.status)
				if (res.status)  this.DashboardConfiguration = res.data
			})
		}
	},
})