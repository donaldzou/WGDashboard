<script setup>
import {onMounted} from "vue";
import QRCode from "qrcode";

const props = defineProps([
	"content"
])

onMounted(() => {
	QRCode.toCanvas(document.getElementById('qrcode'), props.content, function (error) {})
})
</script>

<template>
<div>
	<canvas id="qrcode" class="rounded-3 shadow"></canvas>
</div>
</template>

<style scoped>

</style>