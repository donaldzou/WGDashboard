<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "dashboardSettingsInputWireguardConfigurationPath",
	props:{
		targetData: String,
		title: String,
		warning: false,
		warningText: ""
	},
	setup(){
		const store = DashboardConfigurationStore();
		const uuid = `input_${v4()}`;
		return {store, uuid};
	},
	data(){
		return{
			value:"",
			invalidFeedback: "",
			showInvalidFeedback: false,
			isValid: false,
			timeout: undefined,
			changed: false,
			updating: false,
		}
	},
	mounted() {
		this.value = this.store.Configuration.Server[this.targetData];
	},
	methods:{
		async useValidation(){
			if(this.changed){
				await fetchPost("/api/updateDashboardConfigurationItem", {
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
					this.changed = false;
					this.updating = false
				})
			}
		}
	}
}
</script>

<template>
	<div class="form-group mb-2">
		<label :for="this.uuid" class="text-muted mb-1">
			<strong><small>{{this.title}}</small></strong>
		</label>
		<input type="text" class="form-control"
		       :class="{'is-invalid': this.showInvalidFeedback, 'is-valid': this.isValid}"
		       :id="this.uuid"
		       v-model="this.value"
		       @keydown="this.changed = true"
		       @blur="this.useValidation()"
		       :disabled="this.updating"
		>
		<div class="invalid-feedback">{{this.invalidFeedback}}</div>
		<div class="px-2 py-1 text-warning-emphasis bg-warning-subtle border border-warning-subtle rounded-2 d-inline-block mt-1"
		     v-if="warning"
		>
			<small><i class="bi bi-exclamation-triangle-fill me-2"></i><span v-html="warningText"></span></small>
		</div>
	</div>
</template>


<style scoped>

</style>