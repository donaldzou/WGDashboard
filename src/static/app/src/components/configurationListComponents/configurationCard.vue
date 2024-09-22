<script>
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "configurationCard",
	components: {LocaleText},
	props: {
		c: {
			Name: String,
			Status: Boolean,
			PublicKey: String,
			PrivateKey: String
		}
	},
	data(){
		return{
			configurationToggling: false
		}
	},
	setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore();
		return {dashboardConfigurationStore}
	},
	methods: {
		toggle(){
			this.configurationToggling = true;
			fetchGet("/api/toggleWireguardConfiguration/", {
				configurationName: this.c.Name
			}, (res) => {
				if (res.status){
					this.dashboardConfigurationStore.newMessage("Server",
						`${this.c.Name} ${res.data ? 'is on':'is off'}`)
				}else{
					this.dashboardConfigurationStore.newMessage("Server",
						res.message, 'danger')
				}
				this.c.Status = res.data
				this.configurationToggling = false;
			})
		}
	}
}
</script>

<template>
	<div class="card conf_card rounded-3 shadow text-decoration-none">
		<RouterLink :to="'/configuration/' + c.Name + '/peers'" class="card-body d-flex align-items-center gap-3 flex-wrap text-decoration-none">
			<h6 class="mb-0"><span class="dot" :class="{active: c.Status}"></span></h6>
			<h6 class="card-title mb-0"><samp>{{c.Name}}</samp></h6>
			<h6 class="mb-0 ms-auto">
				<i class="bi bi-chevron-right"></i>
			</h6>
		</RouterLink>
		<div class="card-footer d-flex gap-2 flex-column">
			<div class="row">
				<small class="col-6 col-md-3">
					<i class="bi bi-arrow-down-up me-2"></i>{{c.DataUsage.Total > 0 ? c.DataUsage.Total.toFixed(4) : 0}} GB
				</small>
				<small class="text-primary-emphasis col-6 col-md-3">
					<i class="bi bi-arrow-down me-2"></i>{{c.DataUsage.Receive > 0 ? c.DataUsage.Receive.toFixed(4) : 0}} GB
				</small>
				<small class="text-success-emphasis col-6 col-md-3">
					<i class="bi bi-arrow-up me-2"></i>{{c.DataUsage.Sent > 0 ? c.DataUsage.Sent.toFixed(4) : 0}} GB
				</small>
				<small class="text-md-end col-6 col-md-3">
					<span class="dot me-2" :class="{active: c.ConnectedPeers > 0}"></span>{{c.ConnectedPeers}}
					<LocaleText t="Peers"></LocaleText>
				</small>
			</div>
			<div class="d-flex align-items-center gap-2">
				<small class="text-muted">
					<strong style="word-break: keep-all">
						<LocaleText t="Public Key"></LocaleText>
					</strong>
				</small>
				<small class="mb-0 d-block d-lg-inline-block ">
					<samp style="line-break: anywhere">{{c.PublicKey}}</samp>
				</small>
				<div class="form-check form-switch ms-auto">
					<label class="form-check-label" style="cursor: pointer" :for="'switch' + c.PrivateKey">

						<LocaleText t="Turning Off..." v-if="!c.Status && this.configurationToggling"></LocaleText>
						<LocaleText t="Turning On..." v-else-if="c.Status && this.configurationToggling"></LocaleText>
						<LocaleText t="On" v-else-if="c.Status && !this.configurationToggling"></LocaleText>
						<LocaleText t="Off" v-else-if="!c.Status && !this.configurationToggling"></LocaleText>
						
						
						<span v-if="this.configurationToggling"
						      class="spinner-border spinner-border-sm ms-2" aria-hidden="true"></span>
					</label>
					<input class="form-check-input"
					       style="cursor: pointer"
					       :disabled="this.configurationToggling"
					       type="checkbox" role="switch" :id="'switch' + c.PrivateKey"
					       @change="this.toggle()"
					       v-model="c.Status"
					>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>