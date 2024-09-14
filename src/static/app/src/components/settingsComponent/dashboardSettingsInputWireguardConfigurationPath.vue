<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "dashboardSettingsInputWireguardConfigurationPath",
	components: {LocaleText},
	props:{
		targetData: String,
		title: String,
		warning: false,
		warningText: ""
	},
	setup(){
		const store = DashboardConfigurationStore();
		const WireguardConfigurationStore = WireguardConfigurationsStore()
		const uuid = `input_${v4()}`;
		return {store, uuid, WireguardConfigurationStore};
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
				this.updating = true;
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
						this.WireguardConfigurationStore.getConfigurations()
						this.store.newMessage("Server", "WireGuard configuration path saved", "success")
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
	<div class="form-group">
		<label :for="this.uuid" class="text-muted mb-1">
			<strong><small>
				<LocaleText :t="this.title"></LocaleText>
			</small></strong>
		</label>
		<div class="d-flex gap-2 align-items-start">
			<div class="flex-grow-1">
				<input type="text" class="form-control rounded-3"
				       :class="{'is-invalid': this.showInvalidFeedback, 'is-valid': this.isValid}"
				       :id="this.uuid"
				       v-model="this.value"
				       @keydown="this.changed = true"
				       :disabled="this.updating"
				>
				<div class="invalid-feedback fw-bold">{{this.invalidFeedback}}</div>
			</div>
			<button
				@click="this.useValidation()"
				:disabled="!this.changed"
				class="ms-auto btn rounded-3 border-success-subtle bg-success-subtle text-success-emphasis">
				<i class="bi bi-save2-fill" v-if="!this.updating"></i>
				<span class="spinner-border spinner-border-sm" v-else></span>
			</button>
		</div>
		<div class="px-2 py-1 text-warning-emphasis bg-warning-subtle border border-warning-subtle rounded-2 d-inline-block mt-1 mb-2"
		     v-if="warning"
		>
			<small><i class="bi bi-exclamation-triangle-fill me-2"></i>
				<LocaleText :t="warningText"></LocaleText>
			</small>
		</div>
		
	</div>
</template>


<style scoped>

</style>