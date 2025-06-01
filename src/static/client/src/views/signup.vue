<script setup>
import {reactive} from "vue";

const formData = reactive({
	email: "",
	password: "",
	confirmPassword: ""
})
</script>

<template>
	<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
		<div class="m-auto" style="width: 600px">
			<h1>Sign Up</h1>
			<p>to use WGDashboard Client</p>
			<div class="mt-4 d-flex flex-column gap-3">
				<div class="form-floating">
					<input type="text"
					       required
					       v-model="formData.email"
					       name="email"
					       autocomplete="email"
					       autofocus
					       class="form-control rounded-3" id="email" placeholder="email">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-person-circle me-2"></i>
						Email
					</label>
				</div>
				<div class="form-floating">
					<input type="password"
					       required
					       v-model="formData.password"
					       name="password"
					       autocomplete="password"
					       autofocus
					       class="form-control rounded-3" id="password" placeholder="password">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-key me-2"></i>
						Password
					</label>
				</div>
				<div class="form-floating">
					<input type="password"
					       required
					       v-model="formData.password"
					       name="confirm_password"
					       autocomplete="confirm_password"
					       autofocus
					       class="form-control rounded-3" id="confirm_password" placeholder="confirm_password">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-key me-2"></i>
						Confirm Password
					</label>
				</div>
				
				
				<div class="d-flex">
					<button class="ms-auto btn btn-primary rounded-3 btn-brand px-3 py-2">
						Continue
						<i class="ms-2 bi bi-arrow-right"></i>
					</button>
				</div>
			</div>
			<div>
				<hr class="my-4">
				<div class="d-flex align-items-center">
					<span class="text-muted">
						Already have an account?
					</span>
					<RouterLink  to="/signin" class="text-body text-decoration-none ms-auto fw-bold">
						Sign In
					</RouterLink>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>