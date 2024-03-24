<script>
import {fetchPost} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "peerSettings",
	props: {
		selectedPeer: Object
	},
	data(){
		return {
			data: undefined,
			dataChanged: false,
			showKey: false,
			saving: false
		}
	},
	setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore();
		return {dashboardConfigurationStore}
	},
	methods: {
		reset(){
			if (this.selectedPeer){
				this.data = JSON.parse(JSON.stringify(this.selectedPeer))
				this.dataChanged = false;
			}
		},
		savePeer(){
			this.saving = true;
			fetchPost(`/api/updatePeerSettings/${this.$route.params.id}`, this.data, (res) => {
				this.saving = false;
				if (res.status){
					this.dashboardConfigurationStore.newMessage("Server", "Peer Updated!", "success")
				}else{
					this.dashboardConfigurationStore.newMessage("Server", res.message, "danger")
				}
				this.$emit("refresh")
			})
		}
	},
	beforeMount() {
		this.reset();
	},
	mounted() {
		this.$el.querySelectorAll("input").forEach(x => {
			x.addEventListener("keyup", () => {
				this.dataChanged = true;
			});
		})
	}
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0">
		<div class="container d-flex h-100 w-100">
			<div class="card m-auto rounded-3 shadow" style="width: 700px">
				<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4">
					<h4 class="mb-0">Peer Settings</h4>
					<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
				</div>
				<div class="card-body px-4 pb-4" v-if="this.data">
					<div class="d-flex flex-column gap-2 mb-4">
						<div>
							<small class="text-muted">Public Key</small><br>
							<small><samp>{{this.data.id}}</samp></small>
						</div>
						<div>
							<label for="peer_name_textbox" class="form-label">
								<small class="text-muted">Name</small>
							</label>
							<input type="text" class="form-control form-control-sm rounded-3"
							       :disabled="this.saving"
							       v-model="this.data.name"
							       id="peer_name_textbox" placeholder="">
						</div>
						<div>
							<div class="d-flex position-relative">
								<label for="peer_private_key_textbox" class="form-label">
									<small class="text-muted">Private Key <code>(Required for QR Code and Download)</code></small>
								</label>
								<a role="button" class="ms-auto text-decoration-none toggleShowKey"
									@click="this.showKey = !this.showKey"
								>
									<i class="bi" :class="[this.showKey ? 'bi-eye-slash-fill':'bi-eye-fill']"></i>
								</a>
							</div>
							<input :type="[this.showKey ? 'text':'password']" class="form-control form-control-sm rounded-3"
							       :disabled="this.saving"
							       v-model="this.data.private_key"
							       id="peer_private_key_textbox"
							       style="padding-right: 40px">
						</div>
						<div>
							<label for="peer_allowed_ip_textbox" class="form-label">
								<small class="text-muted">Allowed IPs <code>(Required)</code></small>
							</label>
							<input type="text" class="form-control form-control-sm rounded-3"
							       :disabled="this.saving"
							       v-model="this.data.allowed_ip"
							       id="peer_allowed_ip_textbox">
						</div>
						<div>
							<label for="peer_DNS_textbox" class="form-label">
								<small class="text-muted">DNS <code>(Required)</code></small>
							</label>
							<input type="text" class="form-control form-control-sm rounded-3"
							       :disabled="this.saving"
							       v-model="this.data.DNS"
							       id="peer_DNS_textbox">
						</div>
						<div>
							<label for="peer_endpoint_allowed_ips" class="form-label">
								<small class="text-muted">Endpoint Allowed IPs <code>(Required)</code></small>
							</label>
							<input type="text" class="form-control form-control-sm rounded-3"
							       :disabled="this.saving"
							       v-model="this.data.endpoint_allowed_ip"
							       id="peer_endpoint_allowed_ips">
						</div>
						<hr>
						<div class="accordion mt-2" id="peerSettingsAccordion">
							<div class="accordion-item">
								<h2 class="accordion-header">
									<button class="accordion-button rounded-3 collapsed" type="button" 
									        data-bs-toggle="collapse" data-bs-target="#peerSettingsAccordionOptional">
										Optional Settings
									</button>
								</h2>
								<div id="peerSettingsAccordionOptional" class="accordion-collapse collapse" 
								     data-bs-parent="#peerSettingsAccordion">
									<div class="accordion-body d-flex flex-column gap-2 mb-2">
										<div>
											<label for="peer_preshared_key_textbox" class="form-label">
												<small class="text-muted">Pre-Shared Key</small>
											</label>
											<input type="text" class="form-control form-control-sm rounded-3"
											       :disabled="this.saving"
											       v-model="this.data.preshared_key"
											       id="peer_preshared_key_textbox">
										</div>
										<div>
											<label for="peer_mtu" class="form-label"><small class="text-muted">MTU</small></label>
											<input type="number" class="form-control form-control-sm rounded-3"
											       :disabled="this.saving"
											       v-model="this.data.mtu"
											       id="peer_mtu">
										</div>
										<div>
											<label for="peer_keep_alive" class="form-label">
												<small class="text-muted">Persistent Keepalive</small>
											</label>
											<input type="number" class="form-control form-control-sm rounded-3"
											       :disabled="this.saving"
											       v-model="this.data.keepalive"
											       id="peer_keep_alive">
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<div class="d-flex align-items-center gap-2">
						<button class="btn btn-secondary rounded-3 shadow" 
						        @click="this.reset()"
						        :disabled="!this.dataChanged || this.saving">
							Reset <i class="bi bi-arrow-clockwise ms-2"></i>
						</button>
						
						<button class="ms-auto btn btn-dark btn-brand rounded-3 px-3 py-2 shadow"
						        :disabled="!this.dataChanged || this.saving"
						        @click="this.savePeer()"
						>
							Save Peer<i class="bi bi-save-fill ms-2"></i></button>
					</div>
					
					
					
					
				</div>
			</div>
		</div>

	</div>
</template>

<style scoped>
.peerSettingContainer {
	background-color: #00000060;
	z-index: 1000;
}
.toggleShowKey{
	position: absolute;
	top: 35px;
	right: 12px;
}
</style>