<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "dashboardSettingsInputIPAddressAndPort",
	props:{
		// targetData: String,
		// title: String,
		// warning: false,
		// warningText: ""
	},
	setup(){
		const store = DashboardConfigurationStore();
		const uuid = `input_${v4()}`;
		return {store, uuid};
	},
	data(){
		return{
			app_ip:"",
			app_port:"",
			invalidFeedback: "",
			showInvalidFeedback: false,
			isValid: false,
			timeout: undefined,
			changed: false,
			updating: false,
		}
	},
	mounted() {
		this.app_ip = this.store.Configuration.Server.app_ip;
		this.app_port = this.store.Configuration.Server.app_port;
	},
	methods:{
		async useValidation(){
			if(this.changed){
				await fetchPost(`${apiUrl}/updateDashboardConfigurationItem`, {
					section: "Server",
					key: this.targetData,
					value: this.value
				}, (res) => {
					if (res.status){
						this.isValid = true;
						this.showInvalidFeedback = false;
						this.store.Configuration.Account[this.targetData] = this.value
						clearTimeout(this.timeout)
						this.timeout = setTimeout(() => this.isValid = false, 5000);
					}else{
						this.isValid = false;
						this.showInvalidFeedback = true;
						this.invalidFeedback = res.message
					}
				})
			}
		}
	}
}
</script>

<template>
	<div>
		<div class="invalid-feedback d-block mt-0">{{this.invalidFeedback}}</div>
		<div class="row">
			<div class="form-group mb-2 col-sm">
				<label :for="'app_ip_' + this.uuid" class="text-muted mb-1">
					<strong><small>Dashboard IP Address</small></strong>
				</label>
				<input type="text" class="form-control mb-2" :id="'app_ip_' + this.uuid" v-model="this.app_ip">
				<div class="px-2 py-1 text-warning-emphasis bg-warning-subtle border border-warning-subtle rounded-2 d-inline-block">
					<small><i class="bi bi-exclamation-triangle-fill me-2"></i><code>0.0.0.0</code> means it can be access by anyone with your server
						IP Address.</small>
				</div>
			</div>
			<div class="form-group col-sm">
				<label :for="'app_port_' + this.uuid" class="text-muted mb-1">
					<strong><small>Dashboard Port</small></strong>
				</label>
				<input type="text" class="form-control mb-2" :id="'app_port_' + this.uuid" v-model="this.app_port">
			</div>
		</div>
		<button class="btn btn-success btn-sm fw-bold rounded-3">
			<i class="bi bi-floppy-fill me-2"></i>Update Dashboard Settings & Restart
		</button>
	</div>
</template>


<style scoped>

</style>