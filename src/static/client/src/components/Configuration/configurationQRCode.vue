<script setup>
import * as uuid from "uuid";
import {onMounted} from "vue";
import QRCode from "qrcode";
import Qrcode from "@/components/SignIn/qrcode.vue";

const props = defineProps([
	'qrcodeData'
])

const emits = defineEmits([
	'back'
])

</script>

<template>
<div class="p-2 position-fixed top-0 start-0 vw-100 vh-100 d-flex qrcodeContainer">
	<div class="m-auto d-flex gap-3 flex-column">
		<a role="button" @click="emits('back')">
			<i class="me-2 bi bi-chevron-left"></i> Back
		</a>
		<Qrcode :content="props.qrcodeData" ></Qrcode>
	</div>
</div>
</template>

<style scoped>
.qrcodeContainer{
	background-color: #00000050;
	backdrop-filter: blur(8px);
}
</style>