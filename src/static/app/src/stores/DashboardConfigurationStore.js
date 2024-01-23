import {defineStore} from "pinia";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {cookie} from "@/utilities/cookie.js";

export const DashboardConfigurationStore = defineStore('DashboardConfigurationStore', {
	state: () => ({
		Configuration: undefined
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
		}
	}
});