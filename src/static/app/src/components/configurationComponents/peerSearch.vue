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
			fetchPost(`${apiUrl}/updateDashboardConfigurationItem`, {
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
			fetchPost(`${apiUrl}/updateDashboardConfigurationItem`, {
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
			fetchGet(`${apiUrl}/downloadAllPeers/${this.configuration.Name}`, {}, (res) => {
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
			<button class="btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  shadow-sm"
			        @click="this.downloadAllPeer()">
				<i class="bi bi-download me-2"></i> Download All
			</button>
			<div class="flex-grow-1">
				<input class="form-control rounded-3 bg-secondary-subtle border-1 border-secondary-subtle shadow-sm w-100"
				       placeholder="Search..."
				       id="searchPeers"
				       @keyup="this.debounce()"
				       v-model="this.searchString">
			</div>
			<div class="dropdown dropup">
				<button class="btn text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm" 
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-filter-circle me-2"></i>
					Display
				</button>
				<ul class="dropdown-menu mt-2 shadow rounded-3 animate__animated animation__fadeInDropdown dropdown-menu-end">
					<li>
						<small class="dropdown-header">Sort by</small>
					</li>
					<li v-for="(value, key) in this.sort">
						<a class="dropdown-item d-flex align-items-center" role="button" @click="this.updateSort(key)">
							<small class="me-auto">{{value}}</small>
							<i class="bi bi-check text-primary"
							   v-if="store.Configuration.Server.dashboard_sort === key"></i>
						</a>
					</li>
					<li><hr class="dropdown-divider"></li>
					<li>
						<small class="dropdown-header">Refresh Interval</small>
					</li>
					<li v-for="(value, key) in this.interval">
						<a class="dropdown-item d-flex" role="button" @click="updateRefreshInterval(key)">
							<small class="me-auto">{{value}}</small>
							<i class="bi bi-check text-primary"
							   v-if="store.Configuration.Server.dashboard_refresh_interval === key"></i>
						</a>
					</li>
				</ul>
			</div>
			<div class="dropdown dropup">
				<button class="btn text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm"
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-three-dots"></i>
				</button>
				<ul class="dropdown-menu shadow mt-2 rounded-3 animate__animated animation__fadeInDropdown">
					<li>
						<h6 class="dropdown-header">Peer Jobs</h6>
					</li>
					<li>
						<a role="button" class="dropdown-item" @click="this.$emit('jobsAll')">
							Active Jobs
						</a>
					</li>
					<li>
						<a role="button" class="dropdown-item" @click="this.$emit('jobLogs')">
							Logs
						</a>
					</li>
				</ul>
			</div>
		</div>
	</div>
</template>

<style scoped>

.animation__fadeInDropdown{
	animation-name: fadeInDropdown;
	animation-duration: 0.2s;
	animation-timing-function: cubic-bezier(0.82, 0.58, 0.17, 0.9);
}

@keyframes fadeInDropdown{
	0%{
		opacity: 0;
		filter: blur(3px);
		transform: translateY(-60px);
	}
	100%{
		opacity: 1;
		filter: blur(0px);
		transform: translateY(-40px);
	}
	
}
</style>