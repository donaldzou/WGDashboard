<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "dashboardTheme",
	setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore();
		return {dashboardConfigurationStore}
	},
	methods: {
		async switchTheme(value){
			await fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Server",
				key: "dashboard_theme",
				value: value
			}, (res) => {
				if (res.status){
					this.dashboardConfigurationStore.Configuration.Server.dashboard_theme = value;
				}
			});
		}
	}
}
</script>

<template>
	<div class="card mb-4 shadow rounded-3">
		<p class="card-header">Dashboard Theme</p>
		<div class="card-body d-flex gap-2">
			<button class="btn btn-outline-primary flex-grow-1"
			        @click="this.switchTheme('light')"
			        :class="{active: this.dashboardConfigurationStore.Configuration.Server.dashboard_theme === 'light'}">
				<i class="bi bi-sun-fill"></i>
				Light
			</button>
			<button class="btn btn-outline-primary flex-grow-1"
			        @click="this.switchTheme('dark')"
			        :class="{active: this.dashboardConfigurationStore.Configuration.Server.dashboard_theme === 'dark'}">
				<i class="bi bi-moon-fill"></i>
				Dark
			</button>
		</div>
	</div>
</template>

<style scoped>

</style>