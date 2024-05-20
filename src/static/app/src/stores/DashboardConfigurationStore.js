import {defineStore} from "pinia";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {v4} from "uuid";

export const DashboardConfigurationStore = defineStore('DashboardConfigurationStore', {
	state: () => ({
		Redirect: undefined,
		Configuration: undefined,
		Messages: [],
		Peers: {
			Selecting: false
		}
	}),
	actions: {
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