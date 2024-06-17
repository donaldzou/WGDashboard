<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";


export default {
	name: "peerSearch",
	setup(){
		const store = DashboardConfigurationStore();
		const wireguardConfigurationStore = WireguardConfigurationsStore()
		return {store, wireguardConfigurationStore}
	},
	props: {
		searchString: String,
		configuration: Object
	},
	data(){
		return {
			sort: {
				status: "Status",
				name: "Name",
				allowed_ip: "Allowed IP",
				restricted: "Restricted"
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
		},
		downloadAllPeer(){
			fetchGet(`/api/downloadAllPeers/${this.configuration.Name}`, {}, (res) => {
				console.log(res);
				window.wireguard.generateZipFiles(res, this.configuration.Name)
			})
		}
	},
	mounted() {
		
	}
}
</script>

<template>
	<div>
		<div class="d-flex gap-2 mb-3 z-3">
			<RouterLink
				to="create"
				class="text-decoration-none btn btn-primary rounded-3 btn-sm">
				<i class="bi bi-plus-lg me-2"></i>Peers
			</RouterLink>
			
<!--			<RouterLink-->
<!--				to="jobs"-->
<!--				class="text-decoration-none btn btn-primary rounded-3 btn-sm">-->
<!--				<i class="bi bi-app-indicator me-2"></i>Jobs-->
<!--			</RouterLink>-->
			<button class="btn btn-sm btn-primary rounded-3" @click="this.downloadAllPeer()">
				<i class="bi bi-download me-2"></i> Download All
			</button>
			
			<div class="dropdown ms-auto">
				<button class="btn btn-secondary btn-sm dropdown-toggle rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-filter-circle me-2"></i>
					Sort
				</button>
				<ul class="dropdown-menu mt-2 shadow rounded-3">
					<li v-for="(value, key) in this.sort">
						<a class="dropdown-item d-flex" role="button" @click="this.updateSort(key)">
							<span class="me-auto">{{value}}</span>
							<i class="bi bi-check text-primary"
							   v-if="store.Configuration.Server.dashboard_sort === key"></i>
						</a>
					</li>
				</ul>
			</div>
			<div class="dropdown">
				<button class="btn btn-secondary btn-sm dropdown-toggle rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-arrow-repeat me-2"></i>Refresh Interval
				</button>
				<ul class="dropdown-menu shadow mt-2 rounded-3">
					<li v-for="(value, key) in this.interval">
						<a class="dropdown-item d-flex" role="button" @click="updateRefreshInterval(key)">
							<span class="me-auto">{{value}}</span>
							<i class="bi bi-check text-primary"
							   v-if="store.Configuration.Server.dashboard_refresh_interval === key"></i>
						</a></li>
				</ul>
			</div>

			<!--		<button class="btn btn-outline-secondary btn-sm rounded-3" type="button"-->
			<!--			@click="this.store.Peers.Selecting = !this.store.Peers.Selecting"-->
			<!--		>-->
			<!--			<i class="bi bi-app-indicator me-2"></i>-->
			<!--			Select-->
			<!--		</button>-->

			<div class="d-flex align-items-center">
				<!--			<label class="d-flex me-2 text-muted" for="searchPeers"><i class="bi bi-search me-1"></i></label>-->
				<input class="form-control form-control-sm rounded-3"
				       placeholder="Search..."
				       id="searchPeers"
				       v-model="this.wireguardConfigurationStore.searchString">
			</div>

		</div>
		
	</div>
</template>

<style scoped>

</style>