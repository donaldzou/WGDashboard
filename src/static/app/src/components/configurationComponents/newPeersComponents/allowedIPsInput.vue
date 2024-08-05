<script>
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "allowedIPsInput",
	props: {
		data: Object,
		saving: Boolean,
		bulk: Boolean,
		availableIp: undefined,
	},
	data(){
		return {
			allowedIp: [],
			availableIpSearchString: "",
			customAvailableIp: "",
			allowedIpFormatError: false
		}
	},
	setup(){
		const store = WireguardConfigurationsStore();
		const dashboardStore = DashboardConfigurationStore();
		return {store, dashboardStore}
	},
	computed: {
		searchAvailableIps(){
			return this.availableIpSearchString ?
				this.availableIp.filter(x =>
					x.includes(this.availableIpSearchString) && !this.data.allowed_ips.includes(x)) :
				this.availableIp.filter(x => !this.data.allowed_ips.includes(x))
		}
	},
	methods: {
		addAllowedIp(ip){
			if(this.store.checkCIDR(ip)){
				this.data.allowed_ips.push(ip);
				return true;
			}
			return false;
		}
	},
	watch: {
		customAvailableIp(){
			this.allowedIpFormatError = false;
		},
		availableIp(){
			if (this.availableIp !== undefined && this.availableIp.length > 0){
				this.addAllowedIp(this.availableIp[0])
			}
		}
	},
	mounted() {
		
	}
}
</script>

<template>
	<div :class="{inactiveField: this.bulk}">
		<label for="peer_allowed_ip_textbox" class="form-label">
			<small class="text-muted">Allowed IPs <code>(Required)</code></small>
		</label>
		<div class="d-flex gap-2 flex-wrap" :class="{'mb-2': this.data.allowed_ips.length > 0}">
			<TransitionGroup name="list">
				<span class="badge rounded-pill text-bg-success" v-for="(ip, index) in this.data.allowed_ips" :key="ip">
					{{ip}}
					<a role="button" @click="this.data.allowed_ips.splice(index, 1)">
						<i class="bi bi-x-circle-fill ms-1"></i></a>
				</span>
			</TransitionGroup>
		</div>
		<div class="d-flex gap-2 align-items-center">
			<div class="input-group">
				<input type="text" class="form-control form-control-sm rounded-start-3" 
				       placeholder="Enter IP Address/CIDR"
				       :class="{'is-invalid': this.allowedIpFormatError}"
				       v-model="customAvailableIp"
				       :disabled="bulk">
				<button class="btn btn-outline-success btn-sm rounded-end-3"
				        :disabled="bulk || !this.customAvailableIp"
				        @click="this.addAllowedIp(this.customAvailableIp) 
				            ? this.customAvailableIp = '' : 
				            this.allowedIpFormatError = true;
				            this.dashboardStore.newMessage('WGDashboard', 'Allowed IP is invalid', 'danger')"
				        type="button" id="button-addon2">
					<i class="bi bi-plus-lg"></i>
				</button>
			</div>
			<small class="text-muted">or</small>
			<div class="dropdown flex-grow-1">
				<button class="btn btn-outline-secondary btn-sm dropdown-toggle rounded-3 w-100"
				        :disabled="!availableIp || bulk"
				        data-bs-auto-close="outside"
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-filter-circle me-2"></i>
					Pick Available IP
				</button>
				<ul class="dropdown-menu mt-2 shadow w-100 dropdown-menu-end rounded-3"
				    v-if="this.availableIp"
				    style="overflow-y: scroll; max-height: 270px; width: 300px !important;">
					<li>
						<div class="px-3 pb-2 pt-1">
							<input class="form-control form-control-sm rounded-3"
							       v-model="this.availableIpSearchString"
							       placeholder="Search...">
						</div>
					</li>
					<li v-for="ip in this.searchAvailableIps" >
						<a class="dropdown-item d-flex" role="button" @click="this.addAllowedIp(ip)">
							<span class="me-auto"><small>{{ip}}</small></span>
						</a>
					</li>
					<li v-if="this.searchAvailableIps.length === 0">
						<small class="px-3 text-muted">No available IP containing "{{this.availableIpSearchString}}"</small>
					</li>
				</ul>
			</div>
		</div>
	</div>
</template>

<style scoped>
.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
	transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
	opacity: 0;
	transform: translateY(10px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
	position: absolute;
}
</style>