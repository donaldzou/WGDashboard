<script>
import {fetchPost} from "../utilities/fetch.js";

export default {
	name: "signin",
	data(){
		return {
			username: "",
			password: "",
			loginError: false,
			loginErrorMessage: ""
		}
	},
	methods: {
		async auth(){
			if (this.username && this.password){
				await fetchPost("/api/authenticate", {
					username: this.username,
					password: this.password
				}, (response) => {
					if (response.status){
						this.loginError = false;
						this.$router.push('/')
					}else{
						this.loginError = true;
						this.loginErrorMessage = response.message;
						document.querySelectorAll("input[required]").forEach(x => {
							x.classList.remove("is-valid")
							x.classList.add("is-invalid")
						});
					}
				})
			}else{
				document.querySelectorAll("input[required]").forEach(x => {
					if (x.value.length === 0){
						x.classList.remove("is-valid")
						x.classList.add("is-invalid")
					}else{
						x.classList.remove("is-invalid")
						x.classList.add("is-valid")
					}
				});
			}
		}
	}
}
</script>

<template>
	<div class="container-fluid login-container-fluid h-100 d-flex">
		<div class="login-box m-auto" style="width: 500px;">
			<h5 class="text-center">Welcome to</h5>
			<h1 class="text-center">WGDashboard</h1>
			<div class="m-auto">
				<div class="alert alert-danger mt-2 mb-0" role="alert" v-if="loginError">
					{{this.loginErrorMessage}}
				</div>
				<form @submit="(e) => {e.preventDefault(); this.auth();}">
					<div class="form-group">
						<label for="username" class="text-left" style="font-size: 1rem"><i class="bi bi-person-circle"></i></label>
						<input type="text" v-model="username" class="form-control" id="username" name="username" placeholder="Username" required>
					</div>
					<div class="form-group">
						<label for="password" class="text-left" style="font-size: 1rem"><i class="bi bi-key-fill"></i></label>
						<input type="password" v-model="password" class="form-control" id="password" name="password" placeholder="Password" required>
					</div>
					<button class="btn btn-dark ms-auto mt-4 w-100 d-flex">
						Sign In<i class="ms-auto bi bi-chevron-right"></i></button>
				</form>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>