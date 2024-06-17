<script>
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "peerSettingsDropdown",
	setup(){
		const dashboardStore = DashboardConfigurationStore()
		return {dashboardStore}
	},
	props: {
		Peer: Object
	},
	data(){
		return{
			deleteBtnDisabled: false,
			restrictBtnDisabled: false,
			allowAccessBtnDisabled: false,
		}
	},
	methods: {
		downloadPeer(){
			fetchGet("/api/downloadPeer/"+this.$route.params.id, {
				id: this.Peer.id
			}, (res) => {
				if (res.status){
					const blob = new Blob([res.data.file], { type: "text/plain" });
					const jsonObjectUrl = URL.createObjectURL(blob);
					const filename = `${res.data.fileName}.conf`;
					const anchorEl = document.createElement("a");
					anchorEl.href = jsonObjectUrl;
					anchorEl.download = filename;
					anchorEl.click();
					this.dashboardStore.newMessage("WGDashboard", "Peer download started", "success")
				}else{
					this.dashboardStore.newMessage("Server", res.message, "danger")
				}
			})
		},
		downloadQRCode(){
			fetchGet("/api/downloadPeer/"+this.$route.params.id, {
				id: this.Peer.id
			}, (res) => {
				if (res.status){
					this.$emit("qrcode", res.data.file)					
				}else{
					this.dashboardStore.newMessage("Server", res.message, "danger")
				}
			})
		},
		deletePeer(){
			this.deleteBtnDisabled = true
			fetchPost(`/api/deletePeers/${this.$route.params.id}`, {
				peers: [this.Peer.id]
			}, (res) => {
				this.dashboardStore.newMessage("Server", res.message, res.status ? "success":"danger")
				this.$emit("refresh")
				this.deleteBtnDisabled = false
			})
		},
		restrictPeer(){
			this.restrictBtnDisabled = true
			fetchPost(`/api/restrictPeers/${this.$route.params.id}`, {
				peers: [this.Peer.id]
			}, (res) => {
				this.dashboardStore.newMessage("Server", res.message, res.status ? "success":"danger")
				this.$emit("refresh")
				this.restrictBtnDisabled = false
			})
		},
		allowAccessPeer(){
			this.allowAccessBtnDisabled = true
			fetchPost(`/api/allowAccessPeers/${this.$route.params.id}`, {
				peers: [this.Peer.id]
			}, (res) => {
				this.dashboardStore.newMessage("Server", res.message, res.status ? "success":"danger")
				this.$emit("refresh")
				this.allowAccessBtnDisabled = false
			})
		}
	}
}
</script>

<template>
	<ul class="dropdown-menu mt-2 shadow-lg d-block rounded-3" style="max-width: 200px">
		<template v-if="!this.Peer.restricted">
			<template v-if="!this.Peer.private_key">
				<li>
					<small class="w-100 dropdown-item text-muted"
					       style="white-space: break-spaces; font-size: 0.7rem"
					>Download & QR Code is not available due to no <code>private key</code>
						set for this peer
					</small>
				</li>
				<li><hr class="dropdown-divider"></li>
			</template>
			<li>
				<a class="dropdown-item d-flex" role="button"
				   @click="this.$emit('setting')"
				>
					<i class="me-auto bi bi-pen"></i> Edit
				</a>
			</li>
			<li>
				<a class="dropdown-item d-flex" role="button"
				   @click="this.$emit('jobs')"
				>
					<i class="me-auto bi bi-app-indicator"></i> Schedule Jobs
				</a>
			</li>
			<template v-if="this.Peer.private_key">
				<li>
					<a class="dropdown-item d-flex" role="button" @click="this.downloadPeer()">
						<i class="me-auto bi bi-download"></i> Download
					</a>
				</li>
				<li>
					<a class="dropdown-item d-flex" role="button"
					   @click="this.downloadQRCode()"
					>
						<i class="me-auto bi bi-qr-code"></i> QR Code
					</a>
				</li>
			</template>

			<li><hr class="dropdown-divider"></li>
			<li>
				<a class="dropdown-item d-flex text-warning"
				   @click="this.restrictPeer()"
				   :class="{disabled: this.restrictBtnDisabled}"
				   role="button">
					<i class="me-auto bi bi-lock"></i> {{!this.restrictBtnDisabled ? "Restrict Access":"Restricting..."}}
				</a>
			</li>
			<li>
				<a class="dropdown-item d-flex fw-bold text-danger"
				   @click="this.deletePeer()"
				   :class="{disabled: this.deleteBtnDisabled}"
				   role="button">
					<i class="me-auto bi bi-trash"></i> {{!this.deleteBtnDisabled ? "Delete":"Deleting..."}}
				</a>
			</li>
		</template>
		<template v-else>
			<li>
				<a class="dropdown-item d-flex text-warning"
				   @click="this.allowAccessPeer()"
				   :class="{disabled: this.restrictBtnDisabled}"
				   role="button">
					<i class="me-auto bi bi-unlock"></i> 
					{{!this.allowAccessBtnDisabled ? "Allow Access":"Allowing..."}}
				</a>
			</li>
		</template>
	</ul>
</template>

<style scoped>
.dropdown-menu{
	right: 1rem;
	min-width: 200px;
}

.dropdown-item.disabled, .dropdown-item:disabled{
	opacity: 0.7;
}
</style>