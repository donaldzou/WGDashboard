<script setup>
import {ref} from "vue";
import ConfigurationQRCode from "@/components/Configuration/configurationQRCode.vue";

const props = defineProps([
	'config'
])

const showQRCode = ref(false)
</script>

<template>
	<div class="card rounded-3 border-0">
		<div class="card-body p-3">
			<div class="row g-2">
				<div class="d-flex gap-2 col-12">
					<small class="text-muted">
						<i class="bi bi-tag me-1"></i> Name
					</small>
					<small class="fw-bold flex-grow-1 text-end">
						{{ props.config.name }}
					</small>
				</div>
				<div class="d-flex gap-2 col-12">
					<small class="text-muted">
						<i class="bi bi-bar-chart-fill me-1"></i> Data Usage
					</small>
					<small class="fw-bold flex-grow-1 text-end">
						3.42 / 4.00 GB
					</small>
				</div>
				<div class="d-flex gap-2 col-12">
					<small class="text-muted">
						<i class="bi bi-calendar me-1"></i> Valid Until
					</small>
					<small class="fw-bold flex-grow-1 text-end">
						2025-08-31 00:00:00
					</small>
				</div>
			</div>
			<div class="mt-3 d-flex">
				<button class="btn btn-body rounded-3 flex-grow-1 fw-bold" @click="showQRCode = true">
					<i class="bi bi-link-45deg me-2"></i><small>Connect</small>
				</button>
			</div>
		</div>
		<Transition name="app">
			<ConfigurationQRCode
				v-if="showQRCode"
				@back="showQRCode = false"
				:qrcode-data="config.peer_configuration_data.file"></ConfigurationQRCode>
		</Transition>
	</div>
</template>

<style scoped>
.button-group a:hover{
	background-color: #ffffff20;
}

.dot{
	width: 10px;
	height: 10px;
	border-radius: 50px;
	display: inline-block;
	margin-left: auto !important;
	background-color: #6c757d;
}

.dot.active {
	background-color: #28a745 !important;
	box-shadow: 0 0 0 .2rem #28a74545;
}
</style>