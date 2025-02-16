<script setup>
import {computed, defineComponent, onBeforeUnmount, onMounted, reactive, ref, useTemplateRef, watch} from "vue";
import {fetchGet} from "@/utilities/fetch.js";
import { Line, Bar } from 'vue-chartjs'
import {
	Chart,
	LineElement,
	BarElement,
	BarController,
	LineController,
	LinearScale,
	Legend,
	Title,
	Tooltip,
	CategoryScale,
	PointElement
} from 'chart.js';
Chart.register(
	LineElement,
	BarElement,
	BarController,
	LineController,
	LinearScale,
	Legend,
	Title,
	Tooltip,
	CategoryScale,
	PointElement
);

import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import dayjs from "dayjs";
import {useRoute, useRouter} from "vue-router";
const props = defineProps({
	configurationPeers: Array,
	configurationInfo: Object
})

const historySentData = ref({
	timestamp: [],
	data: []
})

const historyReceivedData = ref({
	timestamp: [],
	data: []
})
const route = useRoute()
const dashboardStore = DashboardConfigurationStore()
const fetchRealtimeTrafficInterval = ref(undefined)
const fetchRealtimeTraffic = async () => {
	await fetchGet("/api/getWireguardConfigurationRealtimeTraffic", {
		configurationName: route.params.id
	}, (res) => {
		let timestamp = dayjs().format("hh:mm:ss A")
		if (res.data.sent !== 0 && res.data.recv !== 0){
			historySentData.value.timestamp.push(timestamp)
			historySentData.value.data.push(res.data.sent)

			historyReceivedData.value.timestamp.push(timestamp)
			historyReceivedData.value.data.push(res.data.recv)
		}else{
			if (historySentData.value.data.length > 0 && historyReceivedData.value.data.length > 0){
				historySentData.value.timestamp.push(timestamp)
				historySentData.value.data.push(res.data.sent)

				historyReceivedData.value.timestamp.push(timestamp)
				historyReceivedData.value.data.push(res.data.recv)
			}
		}
	})
}
const toggleFetchRealtimeTraffic = () => {
	clearInterval(fetchRealtimeTrafficInterval.value)
	fetchRealtimeTrafficInterval.value = undefined;
	if (props.configurationInfo.Status){
		fetchRealtimeTrafficInterval.value = setInterval(() => {
			fetchRealtimeTraffic()
		}, parseInt(dashboardStore.Configuration.Server.dashboard_refresh_interval))
	}
}

onMounted(() => {
	toggleFetchRealtimeTraffic()
})

watch(() => props.configurationInfo.Status, () => {
	toggleFetchRealtimeTraffic()
})

watch(() => dashboardStore.Configuration.Server.dashboard_refresh_interval, () => {
	toggleFetchRealtimeTraffic()
})

onBeforeUnmount(() => {
	clearInterval(fetchRealtimeTrafficInterval.value)
	fetchRealtimeTrafficInterval.value = undefined;
})
const peersDataUsageChartData = computed(() => {
	let data = props.configurationPeers.filter(x => (x.cumu_data + x.total_data) > 0)
	
	return {
		labels: data.map(x => {
			if (x.name) return x.name
			return `Untitled Peer - ${x.id}`
		}),
		datasets: [{
			label: 'Total Data Usage',
			data: data.map(x => x.cumu_data + x.total_data),
			backgroundColor: data.map(x => `#ffc107`),
			tooltip: {
				callbacks: {
					label: (tooltipItem) => {
						return `${tooltipItem.formattedValue} GB`
					}
				}
			}
		}]
	}
})
const peersRealtimeSentData = computed(() => {
	return {
		labels: [...historySentData.value.timestamp],
		datasets: [
			{
				label: 'Data Sent',
				data: [...historySentData.value.data],
				fill: false,
				borderColor: '#198754',
				backgroundColor: '#198754',
				tension: 0
			},
		],
	}
})
const peersRealtimeReceivedData = computed(() => {
	return {
		labels: [...historyReceivedData.value.timestamp],
		datasets: [
			{
				label: 'Data Received',
				data: [...historyReceivedData.value.data],
				fill: false,
				borderColor: '#0d6efd',
				backgroundColor: '#0d6efd',
				tension: 0
			},
		],
	}
})


const peersDataUsageChartOption = computed(() => {
	return {
		responsive: true,
		plugins: {
			legend: {
				display: false
			}
		},
		scales: {
			x: {
				ticks: {
					display: false,
				},
				grid: {
					display: false
				},
			},
			y:{
				ticks: {
					callback: (val, index) => {
						return `${Math.round((val + Number.EPSILON) * 1000) / 1000} GB`
					}
				},
				grid: {
					display: false
				},
			}
		}
	}
})
const realtimePeersChartOption = computed(() => {
	return {
		responsive: true,
		plugins: {
			legend: {
				display: false
			},
			tooltip: {
				callbacks: {
					label: (tooltipItem) => {
						return `${tooltipItem.formattedValue} MB/s`
					}
				}
			}
		},
		scales: {
			x: {
				ticks: {
					display: false,
				},
				grid: {
					display: true
				},
			},
			y:{
				ticks: {
					callback: (val, index) => {
						return `${Math.round((val + Number.EPSILON) * 1000) / 1000} MB/s`
					}
				},
				grid: {
					display: true
				},
			}
		}
	}
})
</script>

<template>
	<div class="row gx-2 gy-2 mb-3">
		<div class="col-12">
			<div class="card rounded-3 bg-transparent " style="height: 270px">
				<div class="card-header bg-transparent border-0">
					<small class="text-muted">
						<LocaleText t="Peers Data Usage"></LocaleText>
					</small></div>
				<div class="card-body pt-1">
					<Bar
						:data="peersDataUsageChartData"
						:options="peersDataUsageChartOption"
						style="width: 100%; height: 200px;  max-height: 200px"></Bar>
				</div>
			</div>
		</div>
		<div class="col-sm col-lg-6">
			<div class="card rounded-3 bg-transparent " style="height: 270px">
				<div class="card-header bg-transparent border-0 d-flex align-items-center">
					<small class="text-muted">
						<LocaleText t="Real Time Received Data Usage"></LocaleText>
					</small>
					<small class="text-primary fw-bold ms-auto" v-if="historyReceivedData.data.length > 0">
						{{historyReceivedData.data[historyReceivedData.data.length - 1]}} MB/s
					</small>
				</div>
				<div class="card-body pt-1">
					<Line
						:options="realtimePeersChartOption"
						:data="peersRealtimeReceivedData"
						style="width: 100%; height: 200px; max-height: 200px"
					></Line>
				</div>
			</div>
		</div>
		<div class="col-sm col-lg-6">
			<div class="card rounded-3 bg-transparent " style="height: 270px">
				<div class="card-header bg-transparent border-0 d-flex align-items-center">
					<small class="text-muted">
						<LocaleText t="Real Time Sent Data Usage"></LocaleText>
					</small>
					<small class="text-success fw-bold ms-auto"  v-if="historySentData.data.length > 0">
						{{historySentData.data[historySentData.data.length - 1]}} MB/s
					</small>
				</div>
				<div class="card-body  pt-1">
					<Line
						:options="realtimePeersChartOption"
						:data="peersRealtimeSentData"
						style="width: 100%; height: 200px; max-height: 200px"
					></Line>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>