<script>
// import {Popover, Dropdown} from "bootstrap";
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import NameInput from "@/components/configurationComponents/newPeersComponents/nameInput.vue";
import PrivatePublicKeyInput from "@/components/configurationComponents/newPeersComponents/privatePublicKeyInput.vue";
import AllowedIPsInput from "@/components/configurationComponents/newPeersComponents/allowedIPsInput.vue";
import DnsInput from "@/components/configurationComponents/newPeersComponents/dnsInput.vue";
import EndpointAllowedIps from "@/components/configurationComponents/newPeersComponents/endpointAllowedIps.vue";
import PresharedKeyInput from "@/components/configurationComponents/newPeersComponents/presharedKeyInput.vue";
import MtuInput from "@/components/configurationComponents/newPeersComponents/mtuInput.vue";
import PersistentKeepAliveInput
	from "@/components/configurationComponents/newPeersComponents/persistentKeepAliveInput.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import BulkAdd from "@/components/configurationComponents/newPeersComponents/bulkAdd.vue";

export default {
	name: "peerCreate",
	components: {
		BulkAdd,
		PersistentKeepAliveInput,
		MtuInput,
		PresharedKeyInput, EndpointAllowedIps, DnsInput, AllowedIPsInput, PrivatePublicKeyInput, NameInput},
	data(){
		return{
			
			data: {
				bulkAdd: false,
				bulkAddAmount: "",
				name: "",
				allowed_ip: [],
				private_key: "",
				public_key: "",
				DNS: this.dashboardStore.Configuration.Peers.peer_global_dns,
				endpoint_allowed_ip: this.dashboardStore.Configuration.Peers.peer_endpoint_allowed_ip,
				keepalive: parseInt(this.dashboardStore.Configuration.Peers.peer_keep_alive),
				mtu: parseInt(this.dashboardStore.Configuration.Peers.peer_mtu),
				preshared_key: ""
			},
			availableIp: undefined,
			availableIpSearchString: "",
			saving: false,
			allowedIpDropdown: undefined
		}
	},
	mounted() {
		fetchGet("/api/getAvailableIPs/" + this.$route.params.id, {}, (res) => {
			if (res.status){
				this.availableIp = res.data;
			}
		})
	},
	setup(){
		const store = WireguardConfigurationsStore();
		const dashboardStore = DashboardConfigurationStore();
		return {store, dashboardStore}
	}, 
	computed:{
		allRequireFieldsFilled(){
			let status = true;
			if (this.data.bulkAdd){
				if(this.data.bulkAddAmount.length === 0 || this.data.bulkAddAmount > this.availableIp.length){
					status = false;
				}
			}else{
				let requireFields =
					["allowed_ip", "private_key", "public_key", "DNS", "endpoint_allowed_ip", "keepalive", "mtu"]

				requireFields.forEach(x => {
					if (this.data[x].length === 0) status = false;
				});
			}
			return status;
		}
	},
	watch: {
		bulkAdd(newVal){
			if(!newVal){
				this.data.bulkAddAmount = "";
			}
		},
		'data.bulkAddAmount'(){
			if (this.data.bulkAddAmount > this.availableIp.length){
				this.data.bulkAddAmount = this.availableIp.length;
			}
		}
	}
}
</script>

<template>
	<div class="modal fade" id="peerCreateModal" data-bs-backdrop="static">
		<div class="modal-dialog " style="max-width: 700px !important;">
			<div class="modal-content rounded-3 border-0 shadow">
				<div class="modal-header border-0 pb-0">
					<h1 class="modal-title fs-5" id="staticBackdropLabel">Add Peer</h1>
					<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
				</div>
				<div class="modal-body">
					<div class="d-flex flex-column gap-2">
						<BulkAdd :saving="saving" :data="this.data" :availableIp="this.availableIp"></BulkAdd>
						<hr class="mb-0 mt-2">
						<NameInput :saving="saving" :data="this.data" v-if="!this.data.bulkAdd"></NameInput>
						<PrivatePublicKeyInput :saving="saving" :data="data" v-if="!this.data.bulkAdd"></PrivatePublicKeyInput>
						<AllowedIPsInput :availableIp="this.availableIp" :saving="saving" :data="data" v-if="!this.data.bulkAdd"></AllowedIPsInput>
						<DnsInput :saving="saving" :data="data"></DnsInput>
						<EndpointAllowedIps :saving="saving" :data="data"></EndpointAllowedIps>
						<hr class="mb-0 mt-2">
						<div class="row">
							<div class="col-sm" v-if="!this.data.bulkAdd">
								<PresharedKeyInput :saving="saving" :data="data" :bulk="this.data.bulkAdd"></PresharedKeyInput>
							</div>
							<div class="col-sm">
								<MtuInput :saving="saving" :data="data"></MtuInput>
							</div>
							<div class="col-sm">
								<PersistentKeepAliveInput :saving="saving" :data="data"></PersistentKeepAliveInput>
							</div>
						</div>
						<div class="d-flex mt-2">
							<button class="ms-auto btn btn-dark btn-brand rounded-3 px-3 py-2 shadow"
							        :disabled="!this.allRequireFieldsFilled"
							>
								<i class="bi bi-plus-circle-fill me-2"></i>Add
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.peerSettingContainer {
	background-color: #00000060;
	z-index: 9998;
}

div{
	transition: 0.2s ease-in-out;
}

.inactiveField{
	opacity: 0.4;
}

.card{
	max-height: 100%;
}
</style>