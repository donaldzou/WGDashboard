<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "endpointAllowedIps",
	components: {LocaleText},
	props: {
		data: Object,
		saving: Boolean
	},
	setup(){
		const store = WireguardConfigurationsStore();
		const dashboardStore = DashboardConfigurationStore()
		return {store, dashboardStore}
	},
	data(){
		return {
			endpointAllowedIps: JSON.parse(JSON.stringify(this.data.endpoint_allowed_ip)),
			error: false
		}
	},
	methods: {
		checkAllowedIP(){
			let i = this.endpointAllowedIps.split(",").map(x => x.replaceAll(' ', ''));
			for (let ip in i){
				if (!this.store.checkCIDR(i[ip])){
					if (!this.error){
						this.dashboardStore.newMessage("WGDashboard", "Endpoint Allowed IP is invalid.", "danger")
					}
					this.data.endpoint_allowed_ip = "";
					this.error = true;
					return;
				}
			}
			this.error = false;
			this.data.endpoint_allowed_ip = this.endpointAllowedIps;
		}
	},
	watch: {
		'endpointAllowedIps'(){
			this.checkAllowedIP();
		}
	}
}
</script>

<template>
	<div>
		<label for="peer_endpoint_allowed_ips" class="form-label">
			<small class="text-muted">
				<LocaleText t="Endpoint Allowed IPs"></LocaleText>
				<code>
					<LocaleText t="(Required)"></LocaleText>
				</code></small>
		</label>
		<input type="text" class="form-control form-control-sm rounded-3"
		       :class="{'is-invalid': error}"
		       :disabled="this.saving"
		       v-model="this.endpointAllowedIps"
		       @blur="this.checkAllowedIP()"
		       id="peer_endpoint_allowed_ips">
	</div>
</template>

<style scoped>

</style>