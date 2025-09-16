<script setup>
import Qrcode from "@/components/SignIn/qrcode.vue";
import {computed} from "vue";

const props = defineProps([
	'qrcodeData', 'protocol'
])

const emits = defineEmits([
	'back'
])
</script>

<template>
<div class="p-2 position-fixed top-0 start-0 vw-100 vh-100 d-flex qrcodeContainer p-3 overflow-scroll flex-column">
	<div>
		<a role="button" @click="emits('back')" class="btn btn-outline-body rounded-3 btn-sm">
			<i class="me-2 bi bi-chevron-left"></i> Back
		</a>
	</div>
	<div class="m-auto d-flex gap-3 flex-column p-3" style="width: 400px">

		<div class="d-flex flex-column gap-2 align-items-center">
			<Qrcode :content="props.qrcodeData.file"></Qrcode>
			<small>
				Scan with {{ protocol === "wg" ? 'WireGuard':'AmneziaWG'}} App
			</small>

			<div v-if="props.qrcodeData.amneziaVPN" class="d-flex flex-column gap-2 align-items-center">
				<Qrcode :content="btoa(props.qrcodeData.amneziaVPN)"></Qrcode>
				<small>
					Scan with AmneziaVPN App
				</small>
			</div>

			<hr class="border-white w-100 my-2">
			<button class="btn bg-primary-subtle border-primary-subtle rounded-3">
				<i class="bi bi-download me-2"></i>Download
			</button>

		</div>
	</div>

</div>
</template>

<style scoped>

.qrcodeContainer{
	background-color: #00000050;
	backdrop-filter: blur(8px) brightness(0.8);
	z-index: 9999;
}
</style>