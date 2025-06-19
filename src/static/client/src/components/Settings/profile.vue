<script setup>
import {clientStore} from "@/stores/clientStore.js";
import {reactive} from "vue";
const store = clientStore()
const ProfileLabels = {
	Firstname: "First Name",
	Lastname: "Last Name"
}
const Password = reactive({
	CurrentPassword: "",
	NewPassword: "",
	RepeatNewPassword: ""
})

const ResetPasswordFields = () => {
	Password.CurrentPassword = ""
	Password.NewPassword = ""
	Password.RepeatNewPassword = ""
}

</script>

<template>
	<div class="d-flex flex-column gap-4 p-3">
		<div>
			<h5>
				Profile
			</h5>
			<div class="row g-2">
				<div class="col-sm-6" v-for="(val, key) in store.clientProfile.Profile">
					<label :for="key" class="text-muted form-label">
						<small>{{ ProfileLabels[key] }}</small>
					</label>
					<input :id="key" class="form-control rounded-3" v-model="store.clientProfile.Profile[key]">
				</div>
			</div>
		</div>
		<form @submit="undefined" @reset="ResetPasswordFields()">
			<h5>
				Update Password
			</h5>
			<div class="row g-2 mb-3">
				<div class="col-sm-12">
					<label class="text-muted form-label" for="CurrentPassword">
						<small>Current Password</small>
					</label>
					<input class="form-control rounded-3" type="password" autocomplete="current-password" id="CurrentPassword" v-model="Password.CurrentPassword">
				</div>
				<div class="col-sm-6">
					<label class="text-muted form-label" for="NewPassword">
						<small>New Password</small>
					</label>
					<input class="form-control rounded-3" type="password" id="NewPassword" autocomplete="new-password" v-model="Password.NewPassword">
				</div>
				<div class="col-sm-6">
					<label class="text-muted form-label" for="RepeatNewPassword">
						<small>Repeat New Password</small>
					</label>
					<input class="form-control rounded-3" type="password" id="RepeatNewPassword" autocomplete="new-password" v-model="Password.RepeatNewPassword">
				</div>
			</div>
			<div class="d-flex gap-2">
				<button class="btn btn-sm btn-secondary rounded-3 ms-auto" type="reset">Clear</button>
				<button class="btn btn-sm btn-danger rounded-3" type="submit">Update</button>
			</div>
		</form>
	</div>
</template>

<style scoped>

</style>