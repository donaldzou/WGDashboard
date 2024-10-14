<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import LocaleText from "@/components/text/localeText.vue";
import {GetLocale} from "@/utilities/locale.js";


export default {
	name: "peerSearch",
	components: {LocaleText},
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
				status: GetLocale("Status"),
				name: GetLocale("Name"),
				allowed_ip: GetLocale("Allowed IPs"),
				restricted: GetLocale("Restricted")
			},
			interval: {
				'5000': GetLocale('5 Seconds'),
				'10000': GetLocale('10 Seconds'),
				'30000': GetLocale('30 Seconds'),
				'60000': GetLocale('1 Minutes')
			},
			searchString: "",
			searchStringTimeout: undefined,
			showDisplaySettings: false,
			showMoreSettings: false
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
	computed: {
		searchBarPlaceholder(){
			return GetLocale("Search Peers...")
		}
	}
}
</script>

<template>
	<div class="mb-3">
		<div class="d-flex gap-2 z-3 peerSearchContainer">
			<RouterLink
				to="create"
				class="text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle shadow-sm">
				<i class="bi bi-plus-lg me-2"></i>
				<LocaleText t="Peer"></LocaleText>
			</RouterLink>
			<button class="btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  shadow-sm"
			        @click="this.downloadAllPeer()">
				<i class="bi bi-download me-2"></i>
				<LocaleText t="Download All"></LocaleText>
			</button>
			<div class="mt-3 mt-md-0 flex-grow-1">

				<input class="form-control rounded-3 bg-secondary-subtle border-1 border-secondary-subtle shadow-sm w-100"
				       :placeholder="searchBarPlaceholder"
				       id="searchPeers"
				       @keyup="this.debounce()"
				       v-model="this.searchString">
			</div>
			<button
				@click="this.showDisplaySettings = true"
				class="btn text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm"
				type="button" aria-expanded="false">
				<i class="bi bi-filter-circle me-2"></i>
				<LocaleText t="Display"></LocaleText>
			</button>
			<button class="btn text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm"
			        @click="this.$emit('editConfiguration')"
			        type="button" aria-expanded="false">
				<i class="bi bi-gear-fill"></i>
			</button>
			<button class="btn text-secondary-emphasis bg-secondary-subtle rounded-3 border-1 border-secondary-subtle shadow-sm"
			        @click="this.showMoreSettings = true"
			        type="button" aria-expanded="false">
				<i class="bi bi-three-dots"></i>
			</button>
			<Transition name="zoom">
				<div
					v-if="this.showDisplaySettings"
					class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll displayModal">
					<div class="container-md d-flex h-100 w-100">
						<div class="m-auto modal-dialog-centered dashboardModal">
							<div class="card rounded-3 shadow w-100">
								<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-2">
									<h4 class="mb-0 fw-normal"><LocaleText t="Display"></LocaleText>
									</h4>
									<button type="button" class="btn-close ms-auto" @click="this.showDisplaySettings = false"></button>
								</div>
								<div class="card-body px-4 pb-4 d-flex gap-3 flex-column">
									<div>
										<p class="text-muted fw-bold mb-2"><small>
											<LocaleText t="Sort by"></LocaleText>
										</small></p>
										<div class="list-group">
											<a v-for="(value, key) in this.sort" class="list-group-item list-group-item-action d-flex" 
											   role="button" 
											   @click="this.updateSort(key)">
												<span class="me-auto">{{value}}</span>
												<i class="bi bi-check text-primary"
												   v-if="store.Configuration.Server.dashboard_sort === key"></i>
											</a>
										</div>
									</div>
									<div>
										<p class="text-muted fw-bold mb-2"><small>
											<LocaleText t="Refresh Interval"></LocaleText>
										</small></p>
										<div class="list-group">
											<a v-for="(value, key) in this.interval"
											   class="list-group-item list-group-item-action d-flex" role="button"
											   @click="this.updateRefreshInterval(key)">
												<span class="me-auto">{{value}}</span>
												<i class="bi bi-check text-primary"
												   v-if="store.Configuration.Server.dashboard_refresh_interval === key"></i>
											</a>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</Transition>
			<Transition name="zoom">
				<div
					v-if="this.showMoreSettings"
					class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll displayModal">
					<div class="container-md d-flex h-100 w-100">
						<div class="m-auto modal-dialog-centered dashboardModal">
							<div class="card rounded-3 shadow w-100">
								<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4">
									<h4 class="mb-0">
										<LocaleText t="Other Settings"></LocaleText>
									</h4>
									<button type="button" class="btn-close ms-auto" @click="this.showMoreSettings = false"></button>
								</div>
								<div class="card-body px-4 pb-4 d-flex gap-3 flex-column pt-0">
									<div>
										<p class="text-muted fw-bold mb-2"><small>
											<LocaleText t="Manage Peers"></LocaleText>
										</small></p>
										<div class="list-group">
											<a class="list-group-item list-group-item-action d-flex" role="button"
											   @click="this.$emit('selectPeers')">
												<LocaleText t="Select Peers"></LocaleText>
											</a>
										</div>
									</div>
									<div>
										<p class="text-muted fw-bold mb-2"><small>
											<LocaleText t="Peer Jobs"></LocaleText>
										</small></p>
										<div class="list-group">
											<a class="list-group-item list-group-item-action d-flex" role="button" 
											   @click="this.$emit('jobsAll')">
												<LocaleText t="Active Jobs"></LocaleText>
											</a>
											<a class="list-group-item list-group-item-action d-flex" role="button"
											   @click="this.$emit('jobLogs')">
												<LocaleText t="Logs"></LocaleText>
											</a>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</Transition>
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

.displayModal .dashboardModal{
	width: 400px !important;
}

@media screen and (max-width: 768px) {
	.peerSearchContainer{
		flex-direction: column;
	}
	
	.peerSettingContainer .dashboardModal{
		width: 100% !important;
	}
}
</style>