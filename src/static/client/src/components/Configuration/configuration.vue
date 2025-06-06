<script setup>
import {ref} from "vue";
import ConfigurationQRCode from "@/components/Configuration/configurationQRCode.vue";

const props = defineProps([
	'config'
])

const showQRCode = ref(false)
</script>

<template>
	<div class="card shadow rounded-3">
		<div class="card-header d-flex align-items-center">
			<div>
				<small v-if="props.config.status === 'stopped'">
					<i class="bi bi-lightbulb text-secondary me-2"></i>
				</small>
				<small v-else>
					<i class="bi bi-lightbulb-fill text-success me-2"></i>
				</small>
				<small style="word-break: break-all">
					{{ props.config.name }}
				</small>
			</div>
			<div class="ms-auto d-flex gap-2 button-group">
				<a role="button" class="px-2 py-1 text-white rounded-3" aria-label="Download Configuration">
					<i class="bi bi-download"></i>
				</a>
				<a role="button"
				   @click="showQRCode = true"
				   class="px-2 py-1 text-white rounded-3" aria-label="Display QR Code">
					<i class="bi bi-qr-code"></i>
				</a>
				<Transition name="app">
					<ConfigurationQRCode
						v-if="showQRCode"
						@back="showQRCode = false"
						:qrcode-data="config.peer_configuration_data.file"></ConfigurationQRCode>
				</Transition>
			</div>
		</div>
		<div class="card-body">
			<div>
				<small class="d-block text-muted" style="font-size: 0.8rem">Public Key</small>
				<small>
					<samp style="word-break: break-word">{{ props.config.id }}</samp>
				</small>
			</div>
			<hr>
			<div>
				<h6 class="text-center">Data Usage</h6>
				<div class="row text-center">
					<div class="col-4">
						<small class="d-block text-muted">
							Total
						</small>
						<small>3.20 GB / 4GB</small>
					</div>
					<div class="col-4">
						<small class="d-block text-muted">
							Received
						</small>
						<small>3.20 GB</small>
					</div>
					<div class="col-4">
						<small class="d-block text-muted">
							Sent
						</small>
						<small>3.20 GB</small>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.button-group a:hover{
	background-color: #ffffff20;
}
</style>