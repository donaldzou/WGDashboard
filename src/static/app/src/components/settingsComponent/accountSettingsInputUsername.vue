<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "accountSettingsInputUsername",
	components: {LocaleText},
	props:{
		targetData: String,
		title: String,
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
		this.value = this.store.Configuration.Account[this.targetData];
	},
	methods:{
		async useValidation(e){
			
			if (this.changed){
				this.updating = true
				await fetchPost("/api/updateDashboardConfigurationItem", {
					section: "Account",
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
					this.changed = false
					this.updating = false;
				})
			}
		}
	}
}
</script>

<template>
	<div class="form-group mb-2">
		<label :for="this.uuid" class="text-muted mb-1">
			<strong><small>
				<LocaleText :t="this.title"></LocaleText>
			</small></strong>
		</label>
		<input type="text" class="form-control"
		       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
		       :id="this.uuid"
		       v-model="this.value"
		       @keydown="this.changed = true"
		       @blur="useValidation()"
		       :disabled="this.updating"
		>
		<div class="invalid-feedback">{{this.invalidFeedback}}</div>
	</div>
</template>

<style scoped>

</style>