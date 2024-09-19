<script>
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "dnsInput",
	components: {LocaleText},
	props: {
		
		data: Object,
		saving: Boolean,
	},
	data(){
		return {
			error: false,
			dns: JSON.parse(JSON.stringify(this.data.DNS)),
		}
	},
	setup(){
		const store = WireguardConfigurationsStore();
		const dashboardStore = DashboardConfigurationStore();
		return {store, dashboardStore}
	},
	methods:{
		checkDNS(){
			if(this.dns){
				let i = this.dns.split(',').map(x => x.replaceAll(' ', ''));
				for(let ip in i){
					if (!this.store.regexCheckIP(i[ip])){
						if (!this.error){
							this.dashboardStore.newMessage("WGDashboard", "DNS is invalid", "danger");
						}
						this.error = true;
						this.data.DNS = "";
						return;
					}
				}
				this.error = false;
				this.data.DNS = this.dns;
			}
		}
	},
	watch: {
		'dns'(){
			this.checkDNS();
		}
	}
}
</script>

<template>
	<div>
		<label for="peer_DNS_textbox" class="form-label">
			<small class="text-muted">
				<LocaleText t="DNS"></LocaleText>
			</small>
		</label>
		<input type="text" class="form-control form-control-sm rounded-3"
		       :class="{'is-invalid': this.error}"
		       :disabled="this.saving"
		       v-model="this.dns"
		       
		       id="peer_DNS_textbox">
	</div>
</template>

<style scoped>

</style>