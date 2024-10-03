<script>
import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "dashboardIPPortInput" ,
	components: {LocaleText},
	setup(){
		const store = DashboardConfigurationStore();
		return {store};
	},
	data(){
		return{
			ipAddress:"",
			port: 0,
			invalidFeedback: "",
			showInvalidFeedback: false,
			isValid: false,
			timeout: undefined,
			changed: false,
			updating: false,
		}
	},
	mounted() {
		this.ipAddress = this.store.Configuration.Server.app_ip
		this.port = this.store.Configuration.Server.app_port
	},
	methods: {
		async useValidation(e, targetData, value){
			if (this.changed){
				this.updating = true
				await fetchPost("/api/updateDashboardConfigurationItem", {
					section: "Server",
					key: targetData,
					value: value
				}, (res) => {
					if (res.status){
						e.target.classList.add("is-valid")
						this.showInvalidFeedback = false;
						this.store.Configuration.Server[targetData] = value
						clearTimeout(this.timeout)
						this.timeout = setTimeout(() => {
							e.target.classList.remove("is-valid")
						}, 5000);
					}else{
						this.isValid = false;
						this.showInvalidFeedback = true;
						this.invalidFeedback = res.message
					}
					this.changed = false
					this.updating = false;
				})
			}
		}
	}
}
</script>

<template>
<div class="card mb-4 shadow rounded-3">
	<p class="card-header">
		<LocaleText t="Dashboard IP Address & Listen Port"></LocaleText>
		
	</p>
	<div class="card-body">
		<div class="row gx-3">
			<div class="col-sm">
				<div class="form-group mb-2">
					<label for="input_dashboard_ip" class="text-muted mb-1">
						<strong><small>
							<LocaleText t="IP Address / Hostname"></LocaleText>
						</small></strong>
					</label>
					<input type="text" class="form-control"
					       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
					       id="input_dashboard_ip"
					       v-model="this.ipAddress"
					       @keydown="this.changed = true"
					       @blur="useValidation($event, 'app_ip', this.ipAddress)"
					       :disabled="this.updating"
					>
					<div class="invalid-feedback">{{this.invalidFeedback}}</div>
				</div>
			</div>
			<div class="col-sm">
				<div class="form-group mb-2">
					<label for="input_dashboard_ip" class="text-muted mb-1">
						<strong><small>
							<LocaleText t="Listen Port"></LocaleText>
						</small></strong>
					</label>
					<input type="number" class="form-control"
					       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
					       id="input_dashboard_ip"
					       v-model="this.port"
					       @keydown="this.changed = true"
					       @blur="useValidation($event, 'app_port', this.port)"
					       :disabled="this.updating"
					>
					<div class="invalid-feedback">{{this.invalidFeedback}}</div>
				</div>
			</div>
		</div>
		<div class="px-2 py-1 text-warning-emphasis bg-warning-subtle border border-warning-subtle rounded-2 d-inline-block mt-1 mb-2">
			<small><i class="bi bi-exclamation-triangle-fill me-2"></i>
				<LocaleText t="Manual restart of WGDashboard is needed to apply changes on IP Address and Listen Port"></LocaleText>
			</small>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>