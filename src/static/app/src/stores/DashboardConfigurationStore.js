import {defineStore} from "pinia";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {v4} from "uuid";

export const DashboardConfigurationStore = defineStore('DashboardConfigurationStore', {
	state: () => ({
		Redirect: undefined,
		Configuration: undefined,
		Messages: [],
		Peers: {
			Selecting: false,
			RefreshInterval: undefined
		},
		CrossServerConfiguration:{
			Enable: false,
			ServerList: {}
		},
		ActiveServerConfiguration: undefined,
		IsElectronApp: false,
		ShowNavBar: false
	}),
	actions: {
		initCrossServerConfiguration(){
			const currentConfiguration = localStorage.getItem('CrossServerConfiguration');
			if (localStorage.getItem("ActiveCrossServerConfiguration") !== null){
				this.ActiveServerConfiguration = localStorage.getItem("ActiveCrossServerConfiguration");
			}
			if (currentConfiguration === null){
				localStorage.setItem('CrossServerConfiguration', JSON.stringify(this.CrossServerConfiguration))
			}else{
				this.CrossServerConfiguration = JSON.parse(currentConfiguration)
			}
			
			
		},
		syncCrossServerConfiguration(){
			localStorage.setItem('CrossServerConfiguration', JSON.stringify(this.CrossServerConfiguration))
		},
		addCrossServerConfiguration(){
			this.CrossServerConfiguration.ServerList[v4().toString()] = {host: "", apiKey: "", active: false}
		},
		deleteCrossServerConfiguration(key){
			delete this.CrossServerConfiguration.ServerList[key];
		},
		getActiveCrossServer(){
			const key = localStorage.getItem('ActiveCrossServerConfiguration');
			if (key !== null){
				return this.CrossServerConfiguration.ServerList[key]
			}
			return undefined
		},
		setActiveCrossServer(key){
			this.ActiveServerConfiguration = key;
			localStorage.setItem('ActiveCrossServerConfiguration', key)
		},
		removeActiveCrossServer(){
			this.ActiveServerConfiguration = undefined;
			localStorage.removeItem('ActiveCrossServerConfiguration')
		},
		
		async getConfiguration(){
			await fetchGet("/api/getDashboardConfiguration", {}, (res) => {
				if (res.status) this.Configuration = res.data
			});
		},
		async updateConfiguration(){
			await fetchPost("/api/updateDashboardConfiguration", {
				DashboardConfiguration: this.Configuration
			}, (res) => {
				console.log(res)
			})
		},
		async signOut(){
			await fetchGet("/api/signout", {}, (res) => {
				this.removeActiveCrossServer();
				this.$router.go('/signin')
			});
		},
		newMessage(from, content, type){
			this.Messages.push({
				id: v4(),
				from: from,
				content: content,
				type: type,
				show: true
			})
		}
	}
});