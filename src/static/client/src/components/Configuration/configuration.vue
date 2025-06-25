<script setup>
import {ref} from "vue";
import ConfigurationQRCode from "@/components/Configuration/configurationQRCode.vue";

const props = defineProps([
	'config'
])

const showQRCode = ref(false)
</script>

<template>
	<div class="card rounded-3 border shadow">
		<div class="card-header border-0 align-items-center d-flex p-3 flex-column flex-sm-row gap-2">
			<small class="fw-bold">
				{{ props.config.name }}
			</small>
			<span class="badge rounded-3 shadow ms-sm-auto"
			      :class="[props.config.protocol === 'wg' ? 'wireguardBg' : 'amneziawgBg' ]"
			      v-if="props.config.protocol === 'wg'">
							{{ props.config.protocol === 'wg' ? 'WireGuard': 'AmneziaWG' }}
						</span>
		</div>
		<div class="card-body p-3">
			<div class="row gy-2 mb-2">
				<div class="col-sm text-center">
					<small class="text-muted mb-2">
						<i class="bi bi-bar-chart-fill me-1"></i> Data Usage
					</small>
					<h6 class="fw-bold ">
						3.42 / 4.00 GB
					</h6>
				</div>
				<div class="col-sm text-center">
					<small class="text-muted mb-2">
						<i class="bi bi-calendar me-1"></i> Valid Until
					</small>
					<h6 class="fw-bold ">
						3.42 / 4.00 GB
					</h6>
				</div>
			</div>
			<button class="btn btn-outline-body rounded-3 flex-grow-1 fw-bold w-100" @click="showQRCode = true">
				<i class="bi bi-link-45deg me-2"></i><small>Connect</small>
			</button>
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