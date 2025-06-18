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
			<div class="row gy-3">
				<div class="col-sm-6 d-flex flex-column gap-3">
					<h6 class="fw-bold mb-0">
						{{ props.config.name }}
					</h6>
					<div class="mt-auto">
						<button class="btn btn-outline-body rounded-3 flex-grow-1 fw-bold w-100" @click="showQRCode = true">
							<i class="bi bi-link-45deg me-2"></i><small>Connect</small>
						</button>
					</div>
				</div>
				<div class="col-sm-6 d-flex flex-column gap-3">
					<div class="d-flex gap-2">
						<small class="text-muted">
							<i class="bi bi-bar-chart-fill me-1"></i> Protocol
						</small>
						<span class="badge rounded-3 shadow ms-auto"
						      :class="[props.config.protocol === 'wg' ? 'wireguardBg' : 'amneziawgBg' ]"
						      v-if="props.config.protocol === 'wg'">
							{{ props.config.protocol === 'wg' ? 'WireGuard': 'AmneziaWG' }}
						</span>
					</div>
					<div class="d-flex gap-2">
						<small class="text-muted">
							<i class="bi bi-bar-chart-fill me-1"></i> Data Usage
						</small>
						<small class="fw-bold flex-grow-1 text-end">
							3.42 / 4.00 GB
						</small>
					</div>
					<div class="d-flex gap-2">
						<small class="text-muted">
							<i class="bi bi-calendar me-1"></i> Valid Until
						</small>
						<small class="fw-bold flex-grow-1 text-end">
							2025-08-31 00:00:00
						</small>
					</div>
				</div>
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