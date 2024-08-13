<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "accountSettingsInputPassword",
	props:{
		targetData: String,
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
			value: {
				currentPassword: "",
				newPassword: "",
				repeatNewPassword: ""
			},
			invalidFeedback: "",
			showInvalidFeedback: false,
			isValid: false,
			timeout: undefined
		}
	},
	methods:{
		async useValidation(){
			if (Object.values(this.value).find(x => x.length === 0) === undefined){
				if (this.value.newPassword === this.value.repeatNewPassword){
					await fetchPost(`${apiUrl}/updateDashboardConfigurationItem`, {
						section: "Account",
						key: this.targetData,
						value: this.value
					}, (res) => {
						if (res.status){
							this.isValid = true;
							this.showInvalidFeedback = false;
							this.store.Configuration.Account[this.targetData] = this.value
							clearTimeout(this.timeout)
							this.timeout = setTimeout(() => {
								this.isValid = false;
								this.value = {
									currentPassword: "",
									newPassword: "",
									repeatNewPassword: ""
								}
							}, 5000);
						}else{
							this.isValid = false;
							this.showInvalidFeedback = true;
							this.invalidFeedback = res.message
						}
					})
				}else{
					this.showInvalidFeedback = true;
					this.invalidFeedback = "New passwords does not match"
				}
				
			}else{
				this.showInvalidFeedback = true;
				this.invalidFeedback = "Please fill in all required fields."
			}
		}
	}
}
</script>

<template>
	<div class="d-flex flex-column">
		<div class="row">
			<div class="col-sm">
				<div class="form-group mb-2">
					<label :for="'currentPassword_' + this.uuid" class="text-muted mb-1">
						<strong><small>Current Password</small></strong>
					</label>
					<input type="password" class="form-control mb-2"
					       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
					       v-model="this.value.currentPassword"
					       :id="'currentPassword_' + this.uuid">
					<div class="invalid-feedback d-block" v-if="showInvalidFeedback">{{this.invalidFeedback}}</div>
				</div>
			</div>
			<div class="col-sm">
				<div class="form-group mb-2">
					<label :for="'newPassword_' + this.uuid" class="text-muted mb-1">
						<strong><small>New Password</small></strong>
					</label>
					<input type="password" class="form-control mb-2"
					       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
					       v-model="this.value.newPassword"
					       :id="'newPassword_' + this.uuid">

				</div>
			</div>
			<div class="col-sm">
				<div class="form-group mb-2">
					<label :for="'repeatNewPassword_' + this.uuid" class="text-muted mb-1">
						<strong><small>Repeat New Password</small></strong>
					</label>
					<input type="password" class="form-control mb-2"
					       :class="{'is-invalid': showInvalidFeedback, 'is-valid': isValid}"
					       v-model="this.value.repeatNewPassword"
					       :id="'repeatNewPassword_' + this.uuid">
				</div>
			</div>
		</div>
		<button class="ms-auto btn bg-success-subtle text-success-emphasis border-1 border-success-subtle rounded-3 shadow-sm" @click="this.useValidation()">
			<i class="bi bi-save2-fill me-2"></i>Update Password
		</button>
	</div>
</template>

<style scoped>

</style>