import {fetchPost} from "./fetch.js";

export default {
	data(){
		return {
			username: "",
			password: ""
		}
	},
	template: `
		<div class="container-fluid login-container-fluid h-100 d-flex">
	        <div class="login-box m-auto" style="width: 500px;">
	                <h1 class="text-center">Sign in</h1>
	                <h5 class="text-center">to WGDashboard</h5>
	                <div class="m-auto">
	                    <div class="alert alert-danger d-none" role="alert" style="margin-top: 1rem; margin-bottom: 0rem;"></div>
	                    <div class="form-group">
	                        <label for="username" class="text-left" style="font-size: 1rem"><i class="bi bi-person-circle"></i></label>
	                        <input type="text" v-model="username" class="form-control" id="username" name="username" placeholder="Username" required>
	                    </div>
	                    <div class="form-group">
	                        <label for="password" class="text-left" style="font-size: 1rem"><i class="bi bi-key-fill"></i></label>
	                        <input type="password" v-model="password" class="form-control" id="password" name="password" placeholder="Password" required>
	                    </div>
	                    <button class="btn btn-dark w-100 mt-4" @click="this.auth()">Sign In</button>
	                </div>
	          </div>
	    </div>
	`,
	methods: {
		async auth(){
			if (this.username && this.password){
				await fetchPost("/auth", {
					username: this.username,
					password: this.password
				}, (response) => {
					console.log(response)
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
				})
			}
		}
	}
}