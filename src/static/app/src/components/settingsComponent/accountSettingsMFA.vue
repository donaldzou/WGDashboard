<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "accountSettingsMFA",
	components: {LocaleText},
	setup(){
		const store = DashboardConfigurationStore();
		const uuid = `input_${v4()}`;
		return {store, uuid};
	},
	data(){
		return {
			status: false
		}
	},
	mounted() {
		this.status = this.store.Configuration.Account["enable_totp"]
	},
	methods: {
		async resetMFA(){
			await fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Account",
				key: "totp_verified",
				value: "false"
			}, async (res) => {
				await fetchPost("/api/updateDashboardConfigurationItem", {
					section: "Account",
					key: "enable_totp",
					value: "false"
				}, (res) => {
					if (res.status){
						this.$router.push("/2FASetup")
					}
				})
			}) 
		}
	}
}
</script>

<template>
<div>
	<div class="d-flex align-items-center">
		<strong>
			<LocaleText t="Multi-Factor Authentication (MFA)"></LocaleText>
		</strong>
		<div class="form-check form-switch ms-3">
			<input class="form-check-input" type="checkbox"
			       v-model="this.status"
			       role="switch" id="allowMFAKeysSwitch">
		</div>
		<button class="btn bg-warning-subtle text-warning-emphasis border-1 border-warning-subtle ms-auto rounded-3 shadow-sm" 
		        v-if="this.status" @click="this.resetMFA()">
			<i class="bi bi-shield-lock-fill me-2"></i>
			<LocaleText t="Reset" v-if='this.store.Configuration.Account["totp_verified"]'></LocaleText>
			<LocaleText t="Setup" v-else></LocaleText>
			MFA
		</button>
	</div>
</div>
</template>

<style scoped>

</style>