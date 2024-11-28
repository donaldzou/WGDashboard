<script setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import LocaleText from "@/components/text/localeText.vue";
import CpuCore from "@/components/systemStatusComponents/cpuCore.vue";
import StorageMount from "@/components/systemStatusComponents/storageMount.vue";
import Process from "@/components/systemStatusComponents/process.vue";

const data = ref(undefined)
let interval = null;

onMounted(() => {
	getData()
	interval = setInterval(() => {
		getData()
	}, 5000)
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
<div class="text-body row g-2">
	<div class="col-sm-6">
		<div class="card rounded-3 h-100 shadow">
			<div class="card-body p-4">
				<div class="row">
					<div class="col-sm-12 d-flex flex-column gap-3">
						<div class="d-flex align-items-center">
							<h3 class="text-muted mb-0">
								<i class="bi bi-cpu-fill me-2"></i>
								<LocaleText t="CPU"></LocaleText>
							</h3>
							<h3 class="ms-auto mb-0">
								<span v-if="data">
									{{ data.cpu.cpu_percent }}%
								</span>
								<span v-else class="spinner-border"></span>
							</h3>
						</div>
						<div class="progress" role="progressbar" style="height: 10px">
							<div class="progress-bar" :style="{width: `${data?.cpu.cpu_percent}%` }"></div>
						</div>
						<div class="d-flex gap-1">
							<CpuCore
								v-for="(cpu, count) in data?.cpu.cpu_percent_per_cpu"
								:square="true"
								:key="count"
								:align="(count + 1) > Math.round(data?.cpu.cpu_percent_per_cpu.length / 2)"
								:core_number="count" :percentage="cpu"
							></CpuCore>
						</div>
						<h5 class="mb-0">Processes</h5>
						<div class="position-relative">
							<TransitionGroup name="process">
								<Process 
									:key="p.pid"
									:cpu="true"
									:process="p" v-for="p in data?.process.cpu_top_10"></Process>
							</TransitionGroup>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="col-sm-6">
		<div class="card rounded-3 h-100 shadow">
			<div class="card-body p-4">
				<div class="row">
					<div class="col-sm-12 d-flex flex-column gap-3">
						<div class="d-flex align-items-center">
							<h3 class="text-muted">
								<i class="bi bi-memory me-2"></i>
								<LocaleText t="Memory"></LocaleText>
							</h3>
							<h3 class="ms-auto">
								<span v-if="data">
									{{ data.memory.virtual_memory.percent }}%
								</span>
								<span v-else class="spinner-border"></span>
							</h3>
						</div>
						<div class="progress" role="progressbar" style="height: 10px">
							<div class="progress-bar bg-info" :style="{width: `${data?.memory.virtual_memory.percent}%` }"></div>
						</div>
						<div class="d-flex align-items-center">
							<h6 class="mb-0">Swap Memory</h6>
							<h6 class="mb-0 ms-auto">{{data?.memory.swap_memory.percent}}%</h6>
						</div>
						<div class="progress" role="progressbar" style="height: 10px">
							<div class="progress-bar bg-info-subtle" :style="{width: `${data?.memory.swap_memory.percent}%` }"></div>
						</div>
						<h5 class="mb-0">Processes</h5>
						<div class="position-relative">
							<TransitionGroup name="process">
								<Process
									:key="p.pid"
									:process="p" v-for="p in data?.process.memory_top_10">
								</Process>
							</TransitionGroup>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="col-sm-12">
		<div class="card rounded-3 h-100 shadow">
			<div class="card-body p-4 d-flex gap-3 flex-column">
				<div class="d-flex align-items-center">
					<h3 class="text-muted mb-0">
						<i class="bi bi-ethernet me-2"></i>
						<LocaleText t="Network"></LocaleText>
					</h3>
					<h3 class="ms-auto mb-0">
						<span v-if="data">
							<LocaleText :t="Object.keys(data.network).length + ' Interface' + (Object.keys(data.network).length > 1 ? 's':'')"></LocaleText>
						</span>
						<span v-else class="spinner-border"></span>
					</h3>
				</div>
				<div v-if="data" class="row g-3">
					<div v-for="(key, index) in Object.keys(data.network).sort()"
					     class="col-sm-6 fadeIn">
						<div class="d-flex mb-2">
							<h6 class="mb-0">
								<samp>{{key}}</samp>
							</h6>
							<h6 class="mb-0 ms-auto d-flex gap-2">
								<span class="text-info">
									<i class="bi bi-arrow-down"></i>
									{{ Math.round((data.network[key].byte_recv / 1024000000 + Number.EPSILON) * 10000) / 10000}} GB
								</span>
								<span class="text-warning">
									<i class="bi bi-arrow-up"></i>
									{{ Math.round((data.network[key].byte_sent / 1024000000 + Number.EPSILON) * 10000) / 10000}} GB
								</span>

							</h6>
						</div>
						<div class="progress" role="progressbar" style="height: 10px">
							<div class="progress-bar bg-info"
							     v-if="data.network[key].byte_recv > 0"
							     :style="{width: `${(data.network[key].byte_recv / (data.network[key].byte_sent + data.network[key].byte_recv)) * 100}%` }"></div>
							<div class="progress-bar bg-warning"
							     v-if="data.network[key].byte_sent > 0"
							     :style="{width: `${(data.network[key].byte_sent / (data.network[key].byte_sent + data.network[key].byte_recv)) * 100}%` }"></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="col-sm-12">
		<div class="card rounded-3 h-100 shadow">
			<div class="card-body p-4 d-flex gap-3 flex-column">
				<div class="d-flex align-items-center">
					<h3 class="text-muted mb-0">
						<i class="bi bi-cpu-fill me-2"></i>
						<LocaleText t="Storage"></LocaleText>
					</h3>
					<h3 class="ms-auto mb-0">
							<span v-if="data">
								<LocaleText :t="Object.keys(data.disk).length + ' Partition' + (Object.keys(data.disk).length > 1 ? 's':'')"></LocaleText>
							</span>
							<span v-else class="spinner-border"></span>
					</h3>
				</div>
				<div class="row g-3">
					<div v-for="(key, index) in Object.keys(data.disk).sort()" class="col-sm-6 fadeIn"
					     v-if="data">
						<div class="d-flex mb-2">
							<h6 class="mb-0">
								<samp>{{key}}</samp>
							</h6>
							<h6 class="mb-0 ms-auto d-flex gap-2">
								<span class="text-success">
									{{ Math.round((data.disk[key].used / 1024000000 + Number.EPSILON) * 100) / 100}} / {{ Math.round((data.disk[key].total / 1024000000 + Number.EPSILON) * 100) / 100}} GB Used
								</span>
							</h6>
						</div>
						<div class="progress" role="progressbar" style="height: 20px">
							<div class="progress-bar bg-success"
							     :style="{width: `${data.disk[key].percent}%`}">
								{{ data.disk[key].percent }}%
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	
</div>
</template>

<style scoped>
.process-move, /* apply transition to moving elements */
.process-enter-active,
.process-leave-active {
	transition: all 0.5s cubic-bezier(0.42, 0, 0.22, 1.0);
}

.process-enter-from,
.process-leave-to {
	opacity: 0;
	transform: translateY(30px);
}

.process-leave-active {
	position: absolute;
	width: 100%;
}

.progress-bar {
	width: 0;
	transition: all 1s cubic-bezier(0.42, 0, 0.22, 1.0);
}

.fadeIn{
	opacity: 0;
	animation: fadeIn 0.5s forwards cubic-bezier(0.42, 0, 0.22, 1.0);
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(30px);
	}
	to{
		opacity: 1;
		transform: translateY(0px);
	}
}
</style>