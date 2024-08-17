<script>
import {parse} from "cidr-tools";
import '@/utilities/wireguard.js'
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {fetchPost} from "@/utilities/fetch.js";

export default {
	name: "newConfiguration",
	setup(){
		const store = WireguardConfigurationsStore()
		return {store}
	},
	data(){
		return {
			newConfiguration: {
				ConfigurationName: "",
				Address: "",
				ListenPort: "",
				PrivateKey: "",
				PublicKey: "",
				PresharedKey: "",
				PreUp: "",
				PreDown: "",
				PostUp: "",
				PostDown: ""
			},
			numberOfAvailableIPs: "0",
			error: false,
			errorMessage: "",
			success: false,
			loading: false
		}
	},
	created() {
		this.wireguardGenerateKeypair();	
	},
	methods: {
		wireguardGenerateKeypair(){
			const wg = window.wireguard.generateKeypair();
			this.newConfiguration.PrivateKey = wg.privateKey;
			this.newConfiguration.PublicKey = wg.publicKey;
			this.newConfiguration.PresharedKey = wg.presharedKey;
		},
		async saveNewConfiguration(){
			if (this.goodToSubmit){
				this.loading = true;
				await fetchPost("/api/addWireguardConfiguration", this.newConfiguration, async (res) => {
					if (res.status){
						this.success = true
						await this.store.getConfigurations()
						setTimeout(() => {
							this.$router.push('/')
						}, 1000)
					}else{
						this.error = true;
						this.errorMessage = res.message;
						document.querySelector(`#${res.data}`).classList.remove("is-valid")
						document.querySelector(`#${res.data}`).classList.add("is-invalid")
						this.loading = false;
					}
				})
			}
		}
	},
	computed: {
		goodToSubmit(){
			let requirements = ["ConfigurationName", "Address", "ListenPort", "PrivateKey"]
			let elements = [...document.querySelectorAll("input[required]")];
			return requirements.find(x => {
				return this.newConfiguration[x].length === 0
			}) === undefined && elements.find(x => {
				return x.classList.contains("is-invalid")
			}) === undefined
		}	
	},
	watch: {
		'newConfiguration.Address'(newVal){
			let ele = document.querySelector("#Address");
			ele.classList.remove("is-invalid", "is-valid")
			try{
				if (newVal.trim().split("/").filter(x => x.length > 0).length !== 2){
					throw Error()
				}
				let p = parse(newVal);
				let i = p.end - p.start;
				this.numberOfAvailableIPs = i.toLocaleString();
				ele.classList.add("is-valid")
			}catch (e) {
				this.numberOfAvailableIPs = "0";
				ele.classList.add("is-invalid")
			}
		},
		'newConfiguration.ListenPort'(newVal){
			let ele = document.querySelector("#ListenPort");
			ele.classList.remove("is-invalid", "is-valid")
			
			if (newVal < 0 || newVal > 65353 || !Number.isInteger(newVal)){
				ele.classList.add("is-invalid")
			}else{
				ele.classList.add("is-valid")
			}
		},
		'newConfiguration.ConfigurationName'(newVal){
			
			let ele = document.querySelector("#ConfigurationName");
			ele.classList.remove("is-invalid", "is-valid")
			if (!/^[a-zA-Z0-9_=+.-]{1,15}$/.test(newVal) || newVal.length === 0 || this.store.Configurations.find(x => x.Name === newVal)){
				ele.classList.add("is-invalid")
			}else{
				ele.classList.add("is-valid")
			}
		},
		'newConfiguration.PrivateKey'(newVal){
			let ele = document.querySelector("#PrivateKey");
			ele.classList.remove("is-invalid", "is-valid")
			
			try{
				wireguard.generatePublicKey(newVal)
				ele.classList.add("is-valid")
			}catch (e) {
				ele.classList.add("is-invalid")
			}
		}
	}
}
</script>

<template>
	<div class="mt-5">
		<div class="container mb-4">
			<div class="mb-4 d-flex align-items-center gap-4">
				<RouterLink to="/" class="text-decoration-none">
					<h3 class="mb-0 text-body">
						<i class="bi bi-chevron-left me-4"></i> New Configuration
					</h3>
				</RouterLink>
			</div>
			
			<form class="text-body d-flex flex-column gap-3"
				@submit="(e) => {e.preventDefault(); this.saveNewConfiguration();}"
			>
				<div class="card rounded-3 shadow">
					<div class="card-header">Configuration Name</div>
					<div class="card-body">
						<input type="text" class="form-control" placeholder="ex. wg1" id="ConfigurationName" 
						       v-model="this.newConfiguration.ConfigurationName"
						       :disabled="this.loading"
						       required>
						<div class="invalid-feedback">
							<div v-if="this.error">{{this.errorMessage}}</div>
							<div v-else>
								Configuration name is invalid. Possible reasons:
								<ul class="mb-0">
									<li>Configuration name already exist.</li>
									<li>Configuration name can only contain 15 lower/uppercase alphabet, numbers, "_"(underscore), "="(equal), "+"(plus), "."(period/dot), "-"(dash/hyphen)</li>
								</ul>
							</div>
							
						</div>
					</div>
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header">Private Key / Public Key / Pre-Shared Key</div>
					<div class="card-body" style="font-family: var(--bs-font-monospace)">
						<div class="mb-2">
							<label class="text-muted fw-bold mb-1"><small>PRIVATE KEY</small></label>
							<div class="input-group">
								<input type="text" class="form-control" id="PrivateKey" required
								       :disabled="this.loading"
								       v-model="this.newConfiguration.PrivateKey" disabled
								>
								<button class="btn btn-outline-primary" type="button"
								        title="Regenerate Private Key"
								        @click="wireguardGenerateKeypair()"
								>
									<i class="bi bi-arrow-repeat"></i>
								</button>
							</div>
						</div>
						<div>
							<label class="text-muted fw-bold mb-1"><small>PUBLIC KEY</small></label>
							<input type="text" class="form-control" id="PublicKey"
							       v-model="this.newConfiguration.PublicKey" disabled
							>
						</div>
						
					</div>
					
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header">Listen Port</div>
					<div class="card-body">
						<input type="number" class="form-control" placeholder="0-65353" id="ListenPort" 
						       min="1"
						       max="65353"
						       v-model="this.newConfiguration.ListenPort"
						       :disabled="this.loading"
						       required>
						<div class="invalid-feedback">
							<div v-if="this.error">{{this.errorMessage}}</div>
							<div v-else>
								Invalid port
							</div>
						</div>
					</div>
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header d-flex align-items-center">
						IP Address & Range
						<span class="badge rounded-pill text-bg-success ms-auto">{{ numberOfAvailableIPs }} Available IPs</span>
					</div>
					<div class="card-body">
						<input type="text" class="form-control" 
						       placeholder="Ex: 10.0.0.1/24" id="Address" 
						       v-model="this.newConfiguration.Address"
						       :disabled="this.loading"
						       required>
						<div class="invalid-feedback">
							<div v-if="this.error">{{this.errorMessage}}</div>
							<div v-else>
								IP address & range is invalid.
							</div>
							
						</div>
					</div>
				</div>
				<hr>
				<div class="accordion" id="newConfigurationOptionalAccordion">
					<div class="accordion-item">
						<h2 class="accordion-header">
							<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#newConfigurationOptionalAccordionCollapse">
								Optional Settings
							</button>
						</h2>
						<div id="newConfigurationOptionalAccordionCollapse" 
						     class="accordion-collapse collapse" data-bs-parent="#newConfigurationOptionalAccordion">
							<div class="accordion-body d-flex flex-column gap-3">
								<div class="card rounded-3">
									<div class="card-header">PreUp</div>
									<div class="card-body">
										<input type="text" class="form-control" id="preUp" v-model="this.newConfiguration.PreUp">
									</div>
								</div>
								<div class="card rounded-3">
									<div class="card-header">PreDown</div>
									<div class="card-body">
										<input type="text" class="form-control" id="preDown" v-model="this.newConfiguration.PreDown">
									</div>
								</div>
								<div class="card rounded-3">
									<div class="card-header">PostUp</div>
									<div class="card-body">
										<input type="text" class="form-control" id="postUp" v-model="this.newConfiguration.PostUp">
									</div>
								</div>
								<div class="card rounded-3">
									<div class="card-header">PostDown</div>
									<div class="card-body">
										<input type="text" class="form-control" id="postDown" v-model="this.newConfiguration.PostDown">
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
<!--				<RouterLink to="/new_configuration" class="btn btn-success rounded-3 shadow ms-auto rounded-3">-->
<!--					<i class="bi bi-save me-2"></i>-->
<!--					Save-->
<!--				</RouterLink>-->
				<button class="btn btn-dark btn-brand rounded-3 px-3 py-2 shadow ms-auto"
				        :disabled="!this.goodToSubmit">
					<span v-if="this.success" class="d-flex w-100">
						Success! <i class="bi bi-check-circle-fill ms-2"></i>
					</span>
					<span v-else-if="!this.loading" class="d-flex w-100">
						Save Configuration <i class="bi bi-save-fill ms-2"></i>
					</span>
					<span v-else class="d-flex w-100 align-items-center">
						Saving...
						<span class="ms-2 spinner-border spinner-border-sm" role="status">
<!--						  <span class="visually-hidden">Loading...</span>-->
						</span>
					</span>
					
				</button>
			</form>
			
			
		</div>
	</div>
</template>

<style scoped>

</style>