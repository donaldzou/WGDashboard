<script setup>
import {onMounted} from "vue";
import QRCode from "qrcode";
import * as uuid from "uuid";

const props = defineProps([
	"content"
])
const id = uuid.v4().toString()

onMounted(() => {
	QRCode.toCanvas(document.getElementById(`qrcode_${id}`), props.content, function (error) {})
})
</script>

<template>
<div class="d-flex gap-2 flex-column">
	<canvas :id="'qrcode_' + id" class="rounded-3"></canvas>
</div>
</template>

<style scoped>
canvas{
	width: 250px !important;
	height: 250px !important;
}
</style>