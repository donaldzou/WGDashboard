<script setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";
import CpuCore from "@/components/configurationListComponents/systemStatusComponents/cpuCore.vue";
import StorageMount from "@/components/configurationListComponents/systemStatusComponents/storageMount.vue";
const data = ref(undefined)
let interval = null;

onMounted(() => {
	getData()
	interval = setInterval(() => {
		getData()
	}, 3000)
})

onBeforeUnmount(() => {
	clearInterval(interval)
})

const getData = () => {
	fetchGet("/api/systemStatus", {}, (res) => {
		data.value = res.data
	})
}
</script>

<template>
	<div class="row text-body gx-4 gy-4 mb-5">
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-cpu-fill me-2"></i>
					<LocaleText t="CPU"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					<span v-if="data">
						{{data.cpu.cpu_percent}}%
					</span>
					<span v-else class="spinner-border spinner-border-sm"></span>
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-primary rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data?.cpu.cpu_percent}%` }">
				</span>
			</div>
			<div class="d-flex mt-2 gap-1">
				<CpuCore v-for="(cpu, count) in data?.cpu.cpu_percent_per_cpu" 
				         :key="count"
				         :align="(count + 1) > Math.round(data?.cpu.cpu_percent_per_cpu.length / 2)"
					:core_number="count" :percentage="cpu"
				></CpuCore>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-device-ssd-fill me-2"></i>
					<LocaleText t="Storage"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					<span v-if="data">
						{{data?.disk['/'].percent}}%
					</span>
					<span v-else class="spinner-border spinner-border-sm"></span>
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-success rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data?.disk['/'].percent}%` }">
				</span>
			</div>
			<div class="d-flex mt-2 gap-1">
				<StorageMount v-for="(disk, count) in Object.keys(data?.disk)"
				              v-if="data"
				              :key="count"
				              :align="(count + 1) > Math.round(Object.keys(data?.disk).length / 2)"
				              :mount="disk" :percentage="data?.disk[disk].percent"
				></StorageMount>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-memory me-2"></i>
					<LocaleText t="Memory"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					<span v-if="data">
						{{data?.memory.virtual_memory.percent}}%
					</span>
					<span v-else class="spinner-border spinner-border-sm"></span>
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-info rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data?.memory.virtual_memory.percent}%` }">
				</span>
			</div>
		</div>
		<div class="col-lg-6 col-xl-3">
			<div class="d-flex align-items-center">
				<h6 class="text-muted">
					<i class="bi bi-memory me-2"></i>
					<LocaleText t="Swap Memory"></LocaleText>
				</h6>
				<h6 class="ms-auto">
					<span v-if="data">
						{{data?.memory.swap_memory.percent}}%
					</span>
					<span v-else class="spinner-border spinner-border-sm"></span>
				</h6>
			</div>
			<div class="w-100 position-relative">
				<span class="d-block w-100 bg-body-secondary rounded-5 barBg" style="height: 6px"></span>
				<span class="d-block bg-warning rounded-5 position-absolute top-0 bar"
				      style="height: 6px;" :style="{width: `${data?.memory.swap_memory.percent}%` }">
					</span>
			</div>
		</div>
	</div>
</template>

<style scoped>
.bar{
	transition: background-color 0.5s cubic-bezier(0.42, 0, 0.22, 1.0);
}
</style>