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
	<div class="d-flex flex-column gap-2 my-4">
<!--		<div class="d-flex gap-3 align-items-center">-->
<!--			<h6 class="mb-0 ms-auto">-->
<!--				<label for="searchPeers">-->
<!--					<i class="bi bi-search"></i>-->
<!--				</label>-->
<!--			</h6>-->
<!--			<input class="form-control form-control-sm rounded-3 bg-secondary-subtle border-1 border-secondary-subtle "-->
<!--			       :placeholder="searchBarPlaceholder"-->
<!--			       id="searchPeers"-->
<!--			       @keyup="this.debounce()"-->
<!--			       v-model="this.searchString">-->
<!--		</div>-->
		<div class="d-flex gap-2 peerSearchContainer">
			
			<div class="dropdown">
				<button
					data-bs-toggle="dropdown"
					class="btn w-100 btn-sm text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  position-relative">
					<i class="bi bi-sort-up me-2"></i>
					<LocaleText t="Sort By"></LocaleText>
					<span class="badge text-bg-primary ms-2">{{this.sort[store.Configuration.Server.dashboard_sort]}}</span>
				</button>
				<ul class="dropdown-menu rounded-3 ">
					<li v-for="(value, key) in this.sort" >
						<button class="dropdown-item d-flex align-items-center" @click="this.updateSort(key)">
							<small>
								{{ value }}
							</small>
							<small class="ms-auto">
								<i class="bi bi-check-circle-fill"
								   v-if="store.Configuration.Server.dashboard_sort === key"></i>
							</small>
						</button>
					</li>
				</ul>
			</div>
			<div class="dropdown">
				<button
					data-bs-toggle="dropdown"
					class="btn btn-sm w-100 text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  position-relative">
					<i class="bi bi-arrow-repeat me-2"></i>
					<LocaleText t="Refresh Interval"></LocaleText>
					<span class="badge text-bg-primary ms-2">{{this.interval[store.Configuration.Server.dashboard_refresh_interval]}}</span>
				</button>
				<ul class="dropdown-menu rounded-3 ">
					<li v-for="(value, key) in this.interval" >
						<button class="dropdown-item d-flex align-items-center" @click="this.updateRefreshInterval(key)">
							<small>
								{{ value }}
							</small>
							<small class="ms-auto">
								<i class="bi bi-check-circle-fill"
								   v-if="store.Configuration.Server.dashboard_refresh_interval === key"></i>
							</small>
						</button>
					</li>

				</ul>
			</div>
			<button class="btn btn-sm text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle  ms-lg-auto"
			        @click="this.downloadAllPeer()">
				<i class="bi bi-download me-2"></i>
				<LocaleText t="Download All"></LocaleText>
			</button>
			<button class="btn btn-sm text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle "
			        @click="this.$emit('selectPeers')">
				<i class="bi bi-check2-all me-2"></i>
				<LocaleText t="Select Peers"></LocaleText>
			</button>
			<button class="btn btn-sm text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle "
			        @click="this.$emit('jobsAll')"
			        type="button" aria-expanded="false">
				<i class="bi bi-person-walking me-2"></i>
				<LocaleText t="Active Jobs"></LocaleText>
			</button>
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

@media screen and (max-width: 992px) {
	.peerSearchContainer{
		flex-direction: column;
	}
	
	.peerSettingContainer .dashboardModal{
		width: 100% !important;
	}
}


.peerSearchContainer > button, .peerSearchContainer .dropdown > button{
	text-align: left;
	display: flex;
	align-items: center;
	
	i{
		margin-right: 1rem !important;
	}
}
</style>