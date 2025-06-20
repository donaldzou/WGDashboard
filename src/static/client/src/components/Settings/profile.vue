<script setup>
import {clientStore} from "@/stores/clientStore.js";
const store = clientStore()
const ProfileLabels = {
	Firstname: "First Name",
	Lastname: "Last Name"
}

</script>

<template>
	<div class="p-3">
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
</template>

<style scoped>

</style>