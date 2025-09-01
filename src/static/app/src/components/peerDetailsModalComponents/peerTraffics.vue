<script setup lang="ts">

import LocaleText from "@/components/text/localeText.vue";
import {Line} from "vue-chartjs";
import {GetLocale} from "@/utilities/locale.js"
import { fetchGet } from "@/utilities/fetch.js"
import {computed, onBeforeUnmount, ref, watch} from "vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js"
import dayjs from "dayjs";
const props = defineProps(['selectedDate', 'selectedPeer'])
const store = DashboardConfigurationStore()

const date = computed(() => props.selectedDate ? props.selectedDate : dayjs())
const traffics = ref([])
const getTraffic = async () => {
	await fetchGet("/api/getPeerTraffics", {
		configurationName: props.selectedPeer.configuration.Name,
		id: props.selectedPeer.id,
		startDate: date.value.format("YYYY-MM-DD"),
		endDate: date.value.format("YYYY-MM-DD")
	}, (res) => {
		traffics.value = res.data
		console.log(traffics.value)
	})
}
const interval = ref(undefined)
getTraffic()
interval.value = setInterval(async () => {
	await getTraffic()
}, 60000)

onBeforeUnmount(() => {
	clearInterval(interval.value)
})
watch(() => date.value, () => {getTraffic()})


const dataUsageChartOption = computed(() => {
	return {
		responsive: true,
		plugins: {
			legend: {
				display: false
			},
			tooltip: {
				callbacks: {
					label: (tooltipItem) => {
						return `${tooltipItem.formattedValue} MB`
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
					callback: (val) => {
						return `${val.toFixed(4)} MB`
					}
				},
				grid: {
					display: true
				},
			}
		}
	}
})

const historicalSent = computed(() => {
	let h = traffics.value.map(x => x.cumu_sent + x.total_sent)
	let r = [0]
	if (h.length > 1){
		for (let i = 1; i < h.length; i++){
			if (h[i] >= h[i - 1]){
				r.push((h[i] - h[i - 1]) * 1024)
			}else{
				r.push(h[i] * 1024)
			}
		}
	}
	return r
})

const historicalReceive = computed(() => {
	let h = traffics.value.map(x => x.cumu_receive + x.total_receive)
	let r = [0]
	if (h.length > 1){
		for (let i = 1; i < h.length; i++){
			if (h[i] >= h[i - 1]){
				r.push((h[i] - h[i - 1]) * 1024)
			}else{
				r.push(h[i] * 1024)
			}
		}
	}
	return r
})

const historicalSentData = computed(() => {
	return {
		labels: traffics.value.map(x => x.time),
		datasets: [
			{
				label: GetLocale('Data Sent'),
				data: historicalSent.value,
				fill: 'start',
				borderColor: '#198754',
				backgroundColor: '#19875490',
				tension: 0,
				pointRadius: 2,
				borderWidth: 1,
			},
		],
	}
})

const historicalReceivedData = computed(() => {
	return {
		labels:  traffics.value.map(x => x.time),
		datasets: [
			{
				label: GetLocale('Data Received'),
				data: historicalReceive.value,
				fill: 'start',
				borderColor: '#0d6efd',
				backgroundColor: '#0d6efd90',
				tension: 0.3,
				pointRadius: 2,
				borderWidth: 1,
			},
		],
	}
})
</script>

<template>
	<div class="card rounded-3 bg-transparent">
		<div class="card-body">
			<h6 class="text-muted">
				<LocaleText :t="'Peer Historical Data Usage of ' + date.format('YYYY-MM-DD')"></LocaleText>
			</h6>

			<div class="d-flex flex-column gap-3">
				<div>
					<p>
						<LocaleText t="Data Received"></LocaleText>
					</p>
					<Line
						:options="dataUsageChartOption"
						:data="historicalReceivedData"
						style="width: 100%; height: 300px; max-height: 300px"
					></Line>
				</div>
				<div>
					<p>
						<LocaleText t="Data Sent"></LocaleText>
					</p>
					<Line
						:options="dataUsageChartOption"
						:data="historicalSentData"
						style="width: 100%; height: 300px; max-height: 300px"
					></Line>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>