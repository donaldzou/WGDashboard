<script setup>
import {onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";
const data = ref(undefined)
onMounted(() => {
	setInterval(() => {
		getData()
	}, 10000)
})

const getData = () => {
	fetchGet("/api/systemStatus", {}, (res) => {
		data.value = res.data
	})
}
</script>

<template>
	<div class="row text-body gx-4 gy-2 mb-5" v-if="data !== undefined">
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-cpu-fill me-2"></i>
					<LocaleText t="CPU Usage"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					{{data.cpu.cpu_percent}}%
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-primary rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data.cpu.cpu_percent}%` }">
				</span>
			</div>
			<div class="d-flex mt-2 gap-1">
				<div class="flex-grow-1 square rounded-3 border"
				     :style="{'background-color': `rgb(13 110 253 / ${cpu}%)`}"
					v-for="cpu in data.cpu.cpu_percent_per_cpu">
					
				</div>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-memory me-2"></i>
					<LocaleText t="Memory Usage"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					{{data.memory.virtual_memory.percent}}%
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-primary rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data.memory.virtual_memory.percent}%` }">
					</span>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-memory me-2"></i>
					<LocaleText t="Swap Memory Usage"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					{{data.memory.swap_memory.percent}}%
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-primary rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data.memory.swap_memory.percent}%` }">
					</span>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-device-ssd-fill me-2"></i>
					<LocaleText t="Storage"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					{{data.disk['/'].percent}}%
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-primary rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data.disk['/'].percent}%` }">
					</span>
			</div>
		</div>
	</div>
</template>

<style scoped>
.square{
	aspect-ratio: 1/1;
}
</style>