<script>
import QRCode from "qrcode";
import LocaleText from "@/components/text/localeText.vue";
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
export default {
	name: "peerQRCode",
	components: {LocaleText},
	props: {
		selectedPeer: Object
	},
	setup(){
		const dashboardStore = DashboardConfigurationStore();
		return {dashboardStore}
	},
	data(){
		return{
			loading: true
		}
	},
	mounted() {
		fetchGet("/api/downloadPeer/"+this.$route.params.id, {
			id: this.selectedPeer.id
		}, (res) => {
			this.loading = false;
			if (res.status){
				QRCode.toCanvas(document.querySelector("#qrcode"), res.data.file,  (error) => {
					if (error) console.error(error)
				})
			}else{
				this.dashboardStore.newMessage("Server", res.message, "danger")
			}
		})
	}
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal justify-content-center">
				<div class="card rounded-3 shadow">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0">
						<h4 class="mb-0">
							<LocaleText t="QR Code"></LocaleText>
						</h4>
						<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
					</div>
					<div class="card-body p-4">
						<div style="width: 292px; height: 292px;" class="d-flex">
							<canvas id="qrcode" class="rounded-3 shadow animate__animated animate__fadeIn animate__faster" :class="{'d-none': loading}"></canvas>
							<div class="spinner-border m-auto" role="status" v-if="loading">
								<span class="visually-hidden">Loading...</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
</style>