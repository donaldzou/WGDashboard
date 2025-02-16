<script>
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";
import {GetLocale} from "@/utilities/locale.js";
import {ref} from "vue";

export default {
	name: "allowedIPsInput",
	components: {LocaleText},
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
	setup(props){
		const store = WireguardConfigurationsStore();
		const dashboardStore = DashboardConfigurationStore();
		const selectedSubnet = ref("")
		if(Object.keys(props.availableIp).length > 0){
			selectedSubnet.value = Object.keys(props.availableIp)[0]
		}
		
		
		return {store, dashboardStore, selectedSubnet}
	},
	computed: {
		searchAvailableIps(){
			return (this.availableIpSearchString ?
				this.availableIp[this.selectedSubnet].filter(x =>
					x.includes(this.availableIpSearchString) && !this.data.allowed_ips.includes(x)) :
				this.availableIp[this.selectedSubnet].filter(x => !this.data.allowed_ips.includes(x)))
		},
		inputGetLocale(){
			return GetLocale("Enter IP Address/CIDR")
		}
	},
	methods: {
		addAllowedIp(ip){
			let list = ip.split(',')
			for (let i = 0; i < list.length; i++){
				let ipaddress = list[i].trim();
				if(this.store.checkCIDR(ipaddress)){
					this.data.allowed_ips.push(ipaddress);
				}else{
					this.allowedIpFormatError = true;
					this.dashboardStore.newMessage('WGDashboard', 
						`This Allowed IP address is invalid: ${ipaddress}`, 'danger')
					return false;
				}
			}
			this.customAvailableIp = ''
			return true;
		}
	},
	watch: {
		customAvailableIp(){
			this.allowedIpFormatError = false;
		}
	},
	mounted() {
		if (this.availableIp !== undefined && 
			Object.keys(this.availableIp).length > 0 && this.data.allowed_ips.length === 0){
			for (let subnet in this.availableIp){
				if (this.availableIp[subnet].length > 0){
					this.addAllowedIp(this.availableIp[subnet][0])
				}
			}
		}
	}
}
</script>

<template>
	<div :class="{inactiveField: this.bulk}">
		<div class="d-flex flex-column flex-md-row mb-2">
			<label for="peer_allowed_ip_textbox" class="form-label mb-0">
				<small class="text-muted">
					<LocaleText t="Allowed IPs"></LocaleText> <code><LocaleText t="(Required)"></LocaleText></code>
				</small>
			</label>
			<div class="form-check form-switch ms-md-auto">
				<input class="form-check-input" type="checkbox" 
				       v-model="this.data.allowed_ips_validation"
				       role="switch" id="disableIPValidation">
				<label class="form-check-label" for="disableIPValidation">
					<small>
						<LocaleText t="Allowed IPs Validation"></LocaleText>
					</small>
				</label>
			</div>
		</div>
		<div class="d-flex">
			<div class="d-flex gap-2 flex-wrap" :class="{'mb-2': this.data.allowed_ips.length > 0}">
				<TransitionGroup name="list">
				<span class="badge rounded-pill text-bg-success" v-for="(ip, index) in this.data.allowed_ips" :key="ip">
					{{ip}}
					<a role="button" @click="this.data.allowed_ips.splice(index, 1)">
						<i class="bi bi-x-circle-fill ms-1"></i></a>
				</span>
				</TransitionGroup>
			</div>
		</div>
		<div class="d-flex gap-2 align-items-center">
			<div class="input-group">
				<input type="text" class="form-control form-control-sm rounded-start-3" 
				       :placeholder="this.inputGetLocale"
				       :class="{'is-invalid': this.allowedIpFormatError}"
				       @keyup.enter="this.customAvailableIp ? this.addAllowedIp(this.customAvailableIp) : undefined"
				       v-model="customAvailableIp"
				       id="peer_allowed_ip_textbox"
				       :disabled="bulk">
				<button class="btn btn-sm rounded-end-3"
				        :class="[this.customAvailableIp ? 'btn-success':'btn-outline-success']"
				        :disabled="bulk || !this.customAvailableIp"
				        @click="this.addAllowedIp(this.customAvailableIp)"
				        type="button" id="button-addon2">
					<i class="bi bi-plus-lg"></i>
				</button>
			</div>
			<small class="text-muted">
				<LocaleText t="or"></LocaleText>
			</small>
			<div class="dropdown flex-grow-1">
				<button class="btn btn-outline-secondary btn-sm dropdown-toggle rounded-3 w-100"
				        :disabled="!availableIp || bulk"
				        data-bs-auto-close="outside"
				        type="button" data-bs-toggle="dropdown" aria-expanded="false">
					<i class="bi bi-filter-circle me-2"></i>
					<LocaleText t="Pick Available IP"></LocaleText>
				</button>
				<ul class="dropdown-menu mt-2 shadow w-100 dropdown-menu-end rounded-3 pb-0"
				    v-if="this.availableIp"
				    style="width: 300px !important;">
					<li>
						<div class="px-3 d-flex gap-3 align-items-center">
							<label for="availableIpSearchString" class="text-muted">
								<i class="bi bi-search"></i>
							</label>
							<input 
								id="availableIpSearchString"
								class="form-control form-control-sm rounded-3"
							       v-model="this.availableIpSearchString">
						</div>
						<hr class="my-2">
						<div class="px-3 overflow-x-scroll d-flex overflow-x-scroll overflow-y-hidden align-items-center gap-2">
							<small class="text-muted">Subnet</small>
							<button 
								v-for="key in Object.keys(this.availableIp)"
								@click="this.selectedSubnet = key"
								:class="{'bg-primary-subtle': this.selectedSubnet === key}"
								class="btn btn-sm text-primary-emphasis rounded-3">
								{{key}}
							</button>
						</div>
						<hr class="mt-2 mb-0">
					</li>
					<li>
						<div class="overflow-y-scroll" style="height: 270px;">
							<div v-for="ip in this.searchAvailableIps" style="">
								<a class="dropdown-item d-flex" role="button" @click="this.addAllowedIp(ip)">
									<span class="me-auto"><small>{{ip}}</small></span>
								</a>
							</div>
							<div v-if="this.searchAvailableIps.length === 0" class="px-3 py-2">
								<small class="text-muted" v-if="this.availableIpSearchString"><LocaleText t="No available IP containing"></LocaleText>"{{this.availableIpSearchString}}"</small>
								<small class="text-muted" v-else><LocaleText t="No more IP address available in this subnet"></LocaleText></small>
							</div>
							
						</div>
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