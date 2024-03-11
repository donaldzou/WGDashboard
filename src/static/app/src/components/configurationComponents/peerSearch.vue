<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchPost} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";

export default {
	name: "peerSearch",
	setup(){
		const store = DashboardConfigurationStore();
		const wireguardConfigurationStore = WireguardConfigurationsStore()
		return {store, wireguardConfigurationStore}
	},
	props: {
		searchString: String	
	},
	data(){
		return {
			sort: {
				status: "Status",
				name: "Name",
				allowed_ip: "Allowed IP"
			},
			interval: {
				'5000': '5 Seconds',
				'10000': '10 Seconds',
				'30000': '30 Seconds',
				'60000': '1 Minutes'
			}
		}
	},
	methods: {
		updateSort(sort){
			fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Server",
				key: "dashboard_sort",
				value: sort
			}, (res) => {
				if (res.status){
					this.store.getConfiguration();
				}
			})
		},
		updateRefreshInterval(refreshInterval){
			fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Server",
				key: "dashboard_refresh_interval",
				value: refreshInterval
			}, (res) => {
				if (res.status){
					this.store.getConfiguration();
				}
			})
		}
	}
}
</script>

<template>
	<div class="d-flex gap-2 mb-3 z-3">
		<div class="dropdown">
			<button class="btn btn-outline-secondary btn-sm dropdown-toggle rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
				<i class="bi bi-filter-circle me-2"></i>
				Sort
			</button>
			<ul class="dropdown-menu mt-2 shadow-lg">
				<li v-for="(value, key) in this.sort">
					<a class="dropdown-item d-flex" role="button" @click="this.updateSort(key)">
						<span class="me-auto">{{value}}</span>
						<i class="bi bi-check" 
						   v-if="store.Configuration.Server.dashboard_sort === key"></i>
					</a></li>
			</ul>
		</div>
		<div class="dropdown">
			<button class="btn btn-outline-secondary btn-sm dropdown-toggle  rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
				<i class="bi bi-arrow-repeat me-2"></i>Refresh Interval
			</button>
			<ul class="dropdown-menu">
				<li v-for="(value, key) in this.interval">
					<a class="dropdown-item d-flex" role="button" @click="updateRefreshInterval(key)">
						<span class="me-auto">{{value}}</span>
						<i class="bi bi-check"
						   v-if="store.Configuration.Server.dashboard_refresh_interval === key"></i>
					</a></li>
			</ul>
		</div>

		<div class="ms-auto d-flex align-items-center">
			<label class="d-flex me-2 text-muted" for="searchPeers"><i class="bi bi-search me-1"></i></label>
			<input class="form-control form-control-sm rounded-3"
			       v-model="this.wireguardConfigurationStore.searchString">
		</div>
	</div>
</template>

<style scoped>

</style>