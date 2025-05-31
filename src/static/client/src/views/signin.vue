<script setup>
import {reactive} from "vue";

const formData = reactive({
	username: "",
	password: ""
})
</script>

<template>
	<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
		<div class="m-auto" style="width: 600px">
			<h4 class="mb-0">Welcome to</h4>
			<h1 class="fw-bold display-4">WGDashboard Client</h1>
			<div class="mt-4 d-flex flex-column gap-3">
				<div class="form-floating">
					<input type="text"
					       required
					       v-model="formData.username"
					       name="username"
					       autocomplete="username"
					       autofocus
					       class="form-control rounded-3" id="username" placeholder="Username">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-person-circle me-2"></i>
						Username
					</label>
				</div>
				<div class="form-floating">
					<input type="password"
					       required
					       v-model="formData.password"
					       name="username"
					       autocomplete="username"
					       autofocus
					       class="form-control rounded-3" id="username" placeholder="Username">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-key me-2"></i>
						Password
					</label>
				</div>
				<a href="#" class="text-body text-decoration-none">
					Forgot Password?
				</a>
				<button class="btn btn-primary rounded-3 btn-lg btn-brand w-100 fw-bold">Sign In</button>
			</div>
			
			<div>
				<hr class="my-4">
				<div class="d-flex align-items-center">
					<span class="text-muted">
						Don't have an account yet?
					</span>
					<RouterLink  to="/signup" class="text-body text-decoration-none ms-auto fw-bold">
						Sign Up
					</RouterLink>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>