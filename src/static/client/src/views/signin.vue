<script setup>
import {reactive} from "vue";

const formData = reactive({
	email: "",
	password: ""
});

const submit = (e) => {
	e.preventDefault();
	for (let key in formData){
		if (formData[key].length === 0){
			
			break
		}
	}
}
</script>

<template>
	<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
		<div class="m-auto" style="width: 600px">
			<h1>Sign In</h1>
			<p>to your WGDashboard Client account</p>
			<form class="mt-4 d-flex flex-column gap-3" @submit="e => submit(e)">
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
					       class="form-control rounded-3" id="password" placeholder="Password">
					<label for="floatingInput" class="d-flex">
						<i class="bi bi-key me-2"></i>
						Password
					</label>
				</div>
				<a href="#" class="text-body text-decoration-none">
					Forgot Password?
				</a>
				<div class="d-flex">
					<button class="ms-auto btn btn-primary rounded-3 btn-brand px-3 py-2">
						Continue
						<i class="ms-2 bi bi-arrow-right"></i>
					</button>
				</div>
			</form>
			
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