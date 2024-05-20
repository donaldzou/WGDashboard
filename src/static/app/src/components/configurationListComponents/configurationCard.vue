<script>
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "configurationCard",
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
						`${this.c.Name} is ${res.data ? 'is on':'is off'}`)
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
		<div class="card-footer d-flex align-items-center">
			<small class="me-2 text-muted">
				<strong>PUBLIC KEY</strong>
			</small>
			<small class="mb-0 d-block d-lg-inline-block ">
				<samp style="line-break: anywhere">{{c.PublicKey}}</samp>
			</small>
			<div class="form-check form-switch ms-auto">
				<label class="form-check-label" style="cursor: pointer" :for="'switch' + c.PrivateKey">
					{{this.configurationToggling ? 'Turning ':''}}
					{{c.Status ? "On":"Off"}}
					<span v-if="this.configurationToggling" 
					      class="spinner-border spinner-border-sm" aria-hidden="true"></span>
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
</template>

<style scoped>

</style>