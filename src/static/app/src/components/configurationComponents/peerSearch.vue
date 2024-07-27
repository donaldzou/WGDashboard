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
			},
			searchString: "",
			searchStringTimeout: undefined
		}
	},
	methods: {
		debounce(){
			if (!this.searchStringTimeout){
				this.searchStringTimeout = setTimeout(() => {
					this.wireguardConfigurationStore.searchString = this.searchString;
				}, 300)
			}else{
				clearTimeout(this.searchStringTimeout)
				this.searchStringTimeout = setTimeout(() => {
					this.wireguardConfigurationStore.searchString = this.searchString;
				}, 300)
			}
		},
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
	<div class="mb-3">
		<div class="d-flex gap-2 z-3">
			<RouterLink
				to="create"
				class="text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle shadow-sm">
				<i class="bi bi-plus-lg me-2"></i>Peer
			</RouterLink>

			<!--			<RouterLink-->
			<!--				to="jobs"-->
			<!--				class="text-decoration-none btn btn-primary rounded-3 btn-sm">-->
			<!--				<i class="bi bi-app-indicator me-2"></i>Jobs-->
			<!--			</RouterLink>-->
			<button class="btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  shadow-sm"
			        @click="this.downloadAllPeer()">
				<i class="bi bi-download me-2"></i> Download All
			</button>
			<div class="d-flex align-items-center  ms-auto">
				<!--			<label class="d-flex me-2 text-muted" for="searchPeers"><i class="bi bi-search me-1"></i></label>-->
				<input class="form-control rounded-3 bg-secondary-subtle border-1 border-secondary-subtle shadow-sm"
				       placeholder="Search..."
				       id="searchPeers"
				       @keyup="this.debounce()"
				       v-model="this.searchString">
			</div>
			<div class="dropdown">
				<button class="btn dropdown-toggle text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm" 
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
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
				<button class="btn dropdown-toggle text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm"
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
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
		</div>
	</div>
</template>

<style scoped>

</style>