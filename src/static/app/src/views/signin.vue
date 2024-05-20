<script>
import {fetchGet, fetchPost} from "../utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "signin",
	async setup(){
		const store = DashboardConfigurationStore()
		let theme = ""
		let totpEnabled = false;
		await fetchGet("/api/getDashboardTheme", {}, (res) => {
			theme = res.data
		});
		await fetchGet("/api/isTotpEnabled", {}, (res) => {
			totpEnabled = res.data
		}); 
		return {store, theme, totpEnabled}
	},
	data(){
		return {
			username: "",
			password: "",
			totp: "",
			loginError: false,
			loginErrorMessage: "",
			loading: false
		}
	},
	methods: {
		async auth(){
			if (this.username && this.password && ((this.totpEnabled && this.totp) || !this.totpEnabled)){
				this.loading = true
				await fetchPost("/api/authenticate", {
					username: this.username,
					password: this.password,
					totp: this.totp
				}, (response) => {
					if (response.status){
						this.loginError = false;
						this.$refs["signInBtn"].classList.add("signedIn")
						if (response.message){
							this.$router.push('/welcome')
						}else{
							if (this.store.Redirect !== undefined){
								this.$router.push(this.store.Redirect)
							}else{
								this.$router.push('/')
							}
						}
					}else{
						this.loginError = true;
						this.loginErrorMessage = response.message;
						document.querySelectorAll("input[required]").forEach(x => {
							x.classList.remove("is-valid")
							x.classList.add("is-invalid")
						});
						this.loading = false
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
	<div class="container-fluid login-container-fluid d-flex main flex-column" :data-bs-theme="this.theme">
		<div class="login-box m-auto" style="width: 500px;">
			<h4 class="mb-0 text-body">Welcome to</h4>
			<span class="dashboardLogo display-3">WGDashboard</span>
			<div class="m-auto">
				<div class="alert alert-danger mt-2 mb-0" role="alert" v-if="loginError">
					{{this.loginErrorMessage}}
				</div>
				<form @submit="(e) => {e.preventDefault(); this.auth();}">
					<div class="form-group text-body">
						<label for="username" class="text-left" style="font-size: 1rem">
							<i class="bi bi-person-circle"></i></label>
						<input type="text" v-model="username" class="form-control" id="username" name="username"
						       autocomplete="on"
						       placeholder="Username" required>
					</div>
					<div class="form-group text-body">
						<label for="password" class="text-left" style="font-size: 1rem"><i class="bi bi-key-fill"></i></label>
						<input type="password" 
						       v-model="password" class="form-control" id="password" name="password"
						       autocomplete="on"
						       placeholder="Password" required>
					</div>
					<div class="form-group text-body" v-if="totpEnabled">
						<label for="totp" class="text-left" style="font-size: 1rem"><i class="bi bi-lock-fill"></i></label>
						<input class="form-control totp"
						       required
						       id="totp" maxlength="6" type="text" inputmode="numeric" autocomplete="one-time-code"
						       placeholder="OTP from your authenticator"
						       v-model="this.totp"
						>
					</div>
					<button class="btn btn-lg btn-dark ms-auto mt-4 w-100 d-flex btn-brand shadow signInBtn" ref="signInBtn">
						<span v-if="!this.loading" class="d-flex w-100">
							Sign In<i class="ms-auto bi bi-chevron-right"></i>
						</span>
						<span v-else class="d-flex w-100 align-items-center">
							Signing In...
							<span class="spinner-border ms-auto spinner-border-sm" role="status">
							  <span class="visually-hidden">Loading...</span>
							</span>
						</span>
					</button>
				</form>
			</div>
		</div>
		<small class="text-muted pb-3 d-block w-100 text-center">
			WGDashboard v4.0 | Developed with ❤️ by 
			<a href="https://github.com/donaldzou" target="_blank"><strong>Donald Zou</strong></a>
		</small>
	</div>
</template>

<style scoped>

</style>