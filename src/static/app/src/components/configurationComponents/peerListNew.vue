<script setup async>
import {computed, defineAsyncComponent, onBeforeUnmount, ref, watch} from "vue";
import {useRoute} from "vue-router";
import {fetchGet} from "@/utilities/fetch.js";
import ProtocolBadge from "@/components/protocolBadge.vue";
import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import PeerDataUsageCharts from "@/components/configurationComponents/peerListComponents/peerDataUsageCharts.vue";
import PeerSearch from "@/components/configurationComponents/peerSearch.vue";
import Peer from "@/components/configurationComponents/peer.vue";
import PeerListModals from "@/components/configurationComponents/peerListComponents/peerListModals.vue";

// Async Components
const PeerSearchBar = defineAsyncComponent(() => import("@/components/configurationComponents/peerSearchBar.vue"))

const dashboardStore = DashboardConfigurationStore()
const wireguardConfigurationStore = WireguardConfigurationsStore()
const route = useRoute()
const configurationInfo = ref({})
const configurationPeers = ref([])
const configurationToggling = ref(false)
const configurationModalSelectedPeer = ref({})
const configurationModals = ref({
	peerSetting: {
		modalOpen: false,
	},
	peerScheduleJobs:{
		modalOpen: false,
	},
	peerQRCode: {
		modalOpen: false,
	},
	peerConfigurationFile: {
		modalOpen: false,
	},
	peerCreate: {
		modalOpen: false
	},
	peerScheduleJobsAll: {
		modalOpen: false
	},
	peerScheduleJobsLogs: {
		modalOpen: false
	},
	peerShare:{
		modalOpen: false,
	},
	editConfiguration: {
		modalOpen: false
	},
	selectPeers: {
		modalOpen: false
	},
	backupRestore: {
		modalOpen: false
	},
	deleteConfiguration: {
		modalOpen: false
	},
	editRawConfigurationFile: {
		modalOpen: false
	}
})
const peerSearchBar = ref(false)

// Fetch Peer =====================================
const fetchPeerList = async () => {
	await fetchGet("/api/getWireguardConfigurationInfo", {
		configurationName: route.params.id
	}, (res) => {
		if (res.status){
			configurationInfo.value = res.data.configurationInfo;
			configurationPeers.value = res.data.configurationPeers;
			
			configurationPeers.value.forEach(p => {
				p.restricted = false
			})
			res.data.configurationRestrictedPeers.forEach(x => {
				x.restricted = true;
				configurationPeers.value.push(x)
			})
		}
	})
}
await fetchPeerList()

// Fetch Peer Interval =====================================
const fetchPeerListInterval = ref(undefined)
const setFetchPeerListInterval = () => {
	clearInterval(fetchPeerListInterval.value)
	fetchPeerListInterval.value = setInterval(async () => {
		await fetchPeerList()
	},  parseInt(dashboardStore.Configuration.Server.dashboard_refresh_interval))
}
setFetchPeerListInterval()
onBeforeUnmount(() => {
	clearInterval(fetchPeerListInterval.value);
	fetchPeerListInterval.value = undefined;
})

watch(() => {
	return dashboardStore.Configuration.Server.dashboard_refresh_interval
}, () => {
	setFetchPeerListInterval()
})

// Toggle Configuration Method =====================================
const toggleConfiguration = async () => {
	configurationToggling.value = true;
	await fetchGet("/api/toggleWireguardConfiguration/", {
		configurationName: configurationInfo.value.Name
	}, (res) => {
		if (res.status){
			dashboardStore.newMessage("Server", 
				`${configurationInfo.value.Name} ${res.data ? 'is on':'is off'}`, "success")
		}else{
			dashboardStore.newMessage("Server", res.message, 'danger')
		}
		wireguardConfigurationStore.Configurations
			.find(x => x.Name === configurationInfo.value.Name).Status = res.data
		configurationInfo.value.Status = res.data
		configurationToggling.value = false;
	})
}

// Configuration Summary =====================================
const configurationSummary = computed(() => {
	return {
		connectedPeers: configurationPeers.value.filter(x => x.status === "running").length,
		totalUsage: configurationPeers.value.length > 0 ?
			configurationPeers.value.filter(x => !x.restricted)
				.map(x => x.total_data + x.cumu_data).reduce((a, b) => a + b, 0).toFixed(4) : 0,
		totalReceive: configurationPeers.value.length > 0 ?
			configurationPeers.value.filter(x => !x.restricted)
				.map(x => x.total_receive + x.cumu_receive).reduce((a, b) => a + b, 0).toFixed(4) : 0,
		totalSent: configurationPeers.value.length > 0 ?
			configurationPeers.value.filter(x => !x.restricted)
				.map(x => x.total_sent + x.cumu_sent).reduce((a, b) => a + b, 0).toFixed(4) : 0
	}
})

const showPeersCount = ref(10)
const searchPeers = computed(() => {
	const result = wireguardConfigurationStore.searchString ?
		configurationPeers.value.filter(x => {
			return x.name.includes(wireguardConfigurationStore.searchString) ||
				x.id.includes(wireguardConfigurationStore.searchString) ||
				x.allowed_ip.includes(wireguardConfigurationStore.searchString)
		}) : configurationPeers.value;

	if (dashboardStore.Configuration.Server.dashboard_sort === "restricted"){
		return result.sort((a, b) => {
			if ( a[dashboardStore.Configuration.Server.dashboard_sort]
				< b[dashboardStore.Configuration.Server.dashboard_sort] ){
				return 1;
			}
			if ( a[dashboardStore.Configuration.Server.dashboard_sort]
				> b[dashboardStore.Configuration.Server.dashboard_sort]){
				return -1;
			}
			return 0;
		}).slice(0, showPeersCount.value);
	}

	return result.sort((a, b) => {
		if ( a[dashboardStore.Configuration.Server.dashboard_sort]
			< b[dashboardStore.Configuration.Server.dashboard_sort] ){
			return -1;
		}
		if ( a[dashboardStore.Configuration.Server.dashboard_sort]
			> b[dashboardStore.Configuration.Server.dashboard_sort]){
			return 1;
		}
		return 0;
	}).slice(0, showPeersCount.value)
})
</script>

<template>
<div class="container-fluid" >
	<div class="d-flex align-items-sm-center flex-column flex-sm-row gap-3">
		<div>
			<div class="text-muted d-flex align-items-center gap-2">
				<h5 class="mb-0">
					<ProtocolBadge :protocol="configurationInfo.Protocol"></ProtocolBadge>
				</h5>
			</div>
			<div class="d-flex align-items-center gap-3">
				<h1 class="mb-0 display-4"><samp>{{configurationInfo.Name}}</samp></h1>
			</div>
		</div>
		<div class="ms-sm-auto d-flex gap-2 flex-column">
			<div class="card rounded-3 bg-transparent ">
				<div class="card-body py-2 d-flex align-items-center">
					<small class="text-muted">
						<LocaleText t="Status"></LocaleText>
					</small>
					<div class="dot ms-2" :class="{active: configurationInfo.Status}"></div>
					<div class="form-check form-switch mb-0 ms-auto pe-0 me-0">
						<label class="form-check-label" style="cursor: pointer" :for="'switch' + configurationInfo.id">
							<LocaleText t="On" v-if="configurationInfo.Status && !configurationToggling"></LocaleText>
							<LocaleText t="Off" v-else-if="!configurationInfo.Status && !configurationToggling"></LocaleText>
							<span v-if="configurationToggling"
							      class="spinner-border spinner-border-sm ms-2" aria-hidden="true">
							</span>
						</label>
						<input class="form-check-input"
						       style="cursor: pointer"
						       :disabled="configurationToggling"
						       type="checkbox" role="switch" :id="'switch' + configurationInfo.id"
						       @change="toggleConfiguration()"
						       v-model="configurationInfo.Status">
					</div>

				</div>
			</div>
			<div class="d-flex gap-2">
				<RouterLink
					to="create"
					class="titleBtn py-2 text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle ">
					<i class="bi bi-plus-lg me-2"></i>
					<LocaleText t="Peer"></LocaleText>
				</RouterLink>
				<button class="titleBtn py-2 text-decoration-none btn text-primary-emphasis bg-primary-subtle rounded-3 border-1 border-primary-subtle "
				        @click="configurationModals.editConfiguration.modalOpen = true"
				        type="button" aria-expanded="false">
					<i class="bi bi-gear-fill me-2"></i>
					<LocaleText t="Configuration Settings"></LocaleText>
				</button>
			</div>
		</div>
	</div>
	<hr>
	<div class="row mt-3 gy-2 gx-2 mb-2">
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent  h-100">
				<div class="card-body py-2 d-flex flex-column justify-content-center">
					<p class="mb-0 text-muted"><small>
						<LocaleText t="Address"></LocaleText>
					</small></p>
					{{configurationInfo.Address}}
				</div>
			</div>
		</div>
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent h-100">
				<div class="card-body py-2 d-flex flex-column justify-content-center">
					<p class="mb-0 text-muted"><small>
						<LocaleText t="Listen Port"></LocaleText>
					</small></p>
					{{configurationInfo.ListenPort}}
				</div>
			</div>
		</div>
		<div style="word-break: break-all" class="col-12 col-lg-6">
			<div class="card rounded-3 bg-transparent h-100">
				<div class="card-body py-2 d-flex flex-column justify-content-center">
					<p class="mb-0 text-muted"><small>
						<LocaleText t="Public Key"></LocaleText>
					</small></p>
					<samp>{{configurationInfo.PublicKey}}</samp>
				</div>
			</div>
		</div>
	</div>
	<div class="row gx-2 gy-2 mb-2">
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent  h-100">
				<div class="card-body d-flex">
					<div>
						<p class="mb-0 text-muted"><small>
							<LocaleText t="Connected Peers"></LocaleText>
						</small></p>
						<strong class="h4">
							{{configurationSummary.connectedPeers}} / {{configurationPeers.length}}
						</strong>
					</div>
					<i class="bi bi-ethernet ms-auto h2 text-muted"></i>
				</div>
			</div>
		</div>
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent  h-100">
				<div class="card-body d-flex">
					<div>
						<p class="mb-0 text-muted"><small>
							<LocaleText t="Total Usage"></LocaleText>
						</small></p>
						<strong class="h4">{{configurationSummary.totalUsage}} GB</strong>
					</div>
					<i class="bi bi-arrow-down-up ms-auto h2 text-muted"></i>
				</div>
			</div>
		</div>
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent  h-100">
				<div class="card-body d-flex">
					<div>
						<p class="mb-0 text-muted"><small>
							<LocaleText t="Total Received"></LocaleText>
						</small></p>
						<strong class="h4 text-primary">{{configurationSummary.totalReceive}} GB</strong>
					</div>
					<i class="bi bi-arrow-down ms-auto h2 text-muted"></i>
				</div>
			</div>
		</div>
		<div class="col-12 col-lg-3">
			<div class="card rounded-3 bg-transparent  h-100">
				<div class="card-body d-flex">
					<div>
						<p class="mb-0 text-muted"><small>
							<LocaleText t="Total Sent"></LocaleText>
						</small></p>
						<strong class="h4 text-success">{{configurationSummary.totalSent}} GB</strong>
					</div>
					<i class="bi bi-arrow-up ms-auto h2 text-muted"></i>
				</div>
			</div>
		</div>
	</div>
	<PeerDataUsageCharts
		:configurationPeers="configurationPeers"
		:configurationInfo="configurationInfo"
	></PeerDataUsageCharts>
	<hr>
	<div style="margin-bottom: 80px">
		<PeerSearch
			@search="peerSearchBar = true"
			@jobsAll="configurationModals.peerScheduleJobsAll.modalOpen = true"
			@jobLogs="configurationModals.peerScheduleJobsLogs.modalOpen = true"
			@editConfiguration="configurationModals.editConfiguration.modalOpen = true"
			@selectPeers="configurationModals.selectPeers.modalOpen = true"
			@backupRestore="configurationModals.backupRestore.modalOpen = true"
			@deleteConfiguration="configurationModals.deleteConfiguration.modalOpen = true"
			:configuration="configurationInfo">
		</PeerSearch>
		<TransitionGroup name="peerList" tag="div" class="row gx-2 gy-2 z-0 position-relative">
			<div class="col-12 col-lg-6 col-xl-4"
			     :key="peer.id"
			     v-for="peer in searchPeers">
				<Peer :Peer="peer"
				      @share="configurationModals.peerShare.selectedPeer = peer.id; this.peerShare.modalOpen = true;"
				      @refresh="fetchPeerList()"
				      @jobs="configurationModals.peerScheduleJobs.modalOpen = true; configurationModals.peerScheduleJobs.selectedPeer = this.configurationPeers.find(x => x.id === peer.id)"
				      @setting="configurationModals.peerSetting.modalOpen = true; configurationModalSelectedPeer = peer"
				      @qrcode="(file) => {configurationModalSelectedPeer = peer; configurationModals.peerQRCode.modalOpen = true;}"
				      @configurationFile="(file) => {configurationModals.peerConfigurationFile.peerConfigData = file; configurationModals.peerConfigurationFile.modalOpen = true;}"
				></Peer>
			</div>
		</TransitionGroup>
	</div>
	<Transition name="slideUp">
		<PeerSearchBar @close="peerSearchBar = false" v-if="peerSearchBar"></PeerSearchBar>
	</Transition>
	<PeerListModals 
		:configurationModals="configurationModals"
		:configurationModalSelectedPeer="configurationModalSelectedPeer"
	></PeerListModals>
</div>
</template>

<style scoped>

</style>