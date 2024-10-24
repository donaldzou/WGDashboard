<script>
import {parse} from "cidr-tools";
import '@/utilities/wireguard.js'
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {fetchPost} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "newConfiguration",
	components: {LocaleText},
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
						this.$router.push(`/configuration/${this.newConfiguration.ConfigurationName}/peers`)
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
	<div class="mt-5 text-body">
		<div class="container mb-4">
			<div class="mb-4 d-flex align-items-center gap-4">
				<RouterLink to="/"
				            class="btn btn-dark btn-brand p-2 shadow" style="border-radius: 100%">
					<h2 class="mb-0" style="line-height: 0">
						<i class="bi bi-arrow-left-circle"></i>
					</h2>
				</RouterLink>
				<h2 class="mb-0">
					<LocaleText t="New Configuration"></LocaleText>
				</h2>
				<RouterLink to="/restore_configuration"
				            class="btn btn-dark btn-brand p-2 shadow ms-auto" style="border-radius: 100%">
					<h2 class="mb-0" style="line-height: 0">
						<i class="bi bi-clock-history"></i>
					</h2>
				</RouterLink>
			</div>
			
			<form class="text-body d-flex flex-column gap-3"
				@submit="(e) => {e.preventDefault(); this.saveNewConfiguration();}"
			>
				<div class="card rounded-3 shadow">
					<div class="card-header">
						<LocaleText t="Configuration Name"></LocaleText>
					</div>
					<div class="card-body">
						<input type="text" class="form-control" placeholder="ex. wg1" id="ConfigurationName" 
						       v-model="this.newConfiguration.ConfigurationName"
						       :disabled="this.loading"
						       required>
						<div class="invalid-feedback">
							<div v-if="this.error">{{this.errorMessage}}</div>
							<div v-else>
								<LocaleText t="Configuration name is invalid. Possible reasons:"></LocaleText>
								<ul class="mb-0">
									<li>
										<LocaleText t="Configuration name already exist."></LocaleText>
									</li>
									<li>
										<LocaleText t="Configuration name can only contain 15 lower/uppercase alphabet, numbers, underscore, equal sign, plus sign, period and hyphen."></LocaleText>
									</li>
								</ul>
							</div>
							
						</div>
					</div>
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header">
						<LocaleText t="Private Key"></LocaleText> & <LocaleText t="Public Key"></LocaleText>
					</div>
					<div class="card-body" style="font-family: var(--bs-font-monospace)">
						<div class="mb-2">
							<label class="text-muted fw-bold mb-1"><small>
								<LocaleText t="Private Key"></LocaleText>
							</small></label>
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
							<label class="text-muted fw-bold mb-1"><small>
								<LocaleText t="Public Key"></LocaleText>
							</small></label>
							<input type="text" class="form-control" id="PublicKey"
							       v-model="this.newConfiguration.PublicKey" disabled
							>
						</div>
						
					</div>
					
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header">
						<LocaleText t="Listen Port"></LocaleText>
					</div>
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
								<LocaleText t="Invalid port"></LocaleText>
							</div>
						</div>
					</div>
				</div>
				<div class="card rounded-3 shadow">
					<div class="card-header d-flex align-items-center">
						<LocaleText t="IP Address/CIDR"></LocaleText>
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
								IP Address/CIDR is invalid
							</div>
							
						</div>
					</div>
				</div>
				<hr>
				<div class="accordion" id="newConfigurationOptionalAccordion">
					<div class="accordion-item">
						<h2 class="accordion-header">
							<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#newConfigurationOptionalAccordionCollapse">
								<LocaleText t="Optional Settings"></LocaleText>
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
				<button class="btn btn-dark btn-brand rounded-3 px-3 py-2 shadow ms-auto"
				        :disabled="!this.goodToSubmit || this.loading || this.success">
					<span v-if="this.success" class="d-flex w-100">
						<LocaleText t="Success"></LocaleText>!
						 <i class="bi bi-check-circle-fill ms-2"></i>
					</span>
					<span v-else-if="!this.loading" class="d-flex w-100">
						<i class="bi bi-save-fill me-2"></i>
						<LocaleText t="Save"></LocaleText>
					</span>
					<span v-else class="d-flex w-100 align-items-center">
						<LocaleText t="Saving..."></LocaleText>
						<span class="ms-2 spinner-border spinner-border-sm" role="status">
						</span>
					</span>
					
				</button>
			</form>
			
			
		</div>
	</div>
</template>

<style scoped>

</style>