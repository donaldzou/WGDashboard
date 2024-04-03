<script>
import QRCode from "qrcode";
export default {
	name: "peerQRCode",
	props: {
		peerConfigData: String
	},
	mounted() {
		QRCode.toCanvas(document.querySelector("#qrcode"), this.peerConfigData , function (error) {
			if (error) console.error(error)
		})
	}
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0">
		<div class="container d-flex h-100 w-100">
			<div class="card m-auto rounded-3 shadow">
				<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0">
					<h4 class="mb-0">QR Code</h4>
					<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
				</div>
				<div class="card-body">
					<canvas id="qrcode" class="rounded-3 shadow" ref="qrcode"></canvas>
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
</style>