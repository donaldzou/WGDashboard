<script setup lang="ts">
import {computed} from "vue";
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
	PointElement,
	Filler
} from 'chart.js';
import {Line} from "vue-chartjs";
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
	PointElement,
	Filler
);
import {GetLocale} from "@/utilities/locale.js";
import LocaleText from "@/components/text/localeText.vue";

const props = defineProps([
	'historicalChartTimestamp', 'historicalNetworkSpeed',
	'interfaceName', 'interface'
])

const networkSpeedChartOption = computed(() => {
	return {
		responsive: true,
		plugins: {
			legend: {
				display: true
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
					display: false
				},
			},
			y:{
				ticks: {
					callback: (val, index) => {
						return `${Math.round(val * 10000) / 10000} MB/s`
					}
				},
				grid: {
					display: false
				},
			}
		}
	}
})

const networkSpeedHistoricalChartData = computed(() => {
	return {
		labels: [...props.historicalChartTimestamp],
		datasets: [
			{
				label: GetLocale('Real Time Received Data Usage'),
				data: [...props.historicalNetworkSpeed.bytes_recv],
				fill: 'origin',
				borderColor: '#0dcaf0',
				backgroundColor: '#0dcaf090',
				tension: 0,
				pointRadius: 2,
				borderWidth: 1,
			},
			{
				label: GetLocale('Real Time Sent Data Usage'),
				data: [...props.historicalNetworkSpeed.bytes_sent],
				fill: 'origin',
				backgroundColor: '#ffc10790',
				borderColor: '#ffc107',
				tension: 0,
				pointRadius: 2,
				borderWidth: 1,
			}
		]
	}
})
</script>

<template>
	<div
		 class="col-sm-6 fadeIn d-flex gap-2 flex-column">
		<div>
			<div class="d-flex mb-2">
				<h6 class="mb-0">
					<samp>{{interfaceName}}</samp>
				</h6>
				<h6 class="mb-0 ms-auto d-flex gap-2">
				<span class="text-info">
					<i class="bi bi-arrow-down"></i>
					{{ Math.round((interface.bytes_recv / 1024000000 + Number.EPSILON) * 10000) / 10000}} GB
				</span>
					<span class="text-warning">
					<i class="bi bi-arrow-up"></i>
					{{ Math.round((interface.bytes_sent / 1024000000 + Number.EPSILON) * 10000) / 10000}} GB
				</span>
				</h6>
			</div>
			<div class="progress" role="progressbar" style="height: 10px">
				<div class="progress-bar bg-info"
					 v-if="interface.bytes_recv > 0"
					 :style="{width: `${(interface.bytes_recv / (interface.bytes_sent + interface.bytes_recv)) * 100}%` }"></div>
				<div class="progress-bar bg-warning"
					 v-if="interface.bytes_sent > 0"
					 :style="{width: `${(interface.bytes_sent / (interface.bytes_sent + interface.bytes_recv)) * 100}%` }"></div>
			</div>
		</div>
		<div class="card rounded-3">
			<div class="card-header d-flex align-items-center gap-3">
				<small>
					<LocaleText t="Realtime Speed"></LocaleText>
				</small>
				<small class="text-info ms-auto">
					<i class="bi bi-arrow-down-circle me-2"></i>
					{{ historicalNetworkSpeed.bytes_recv[historicalNetworkSpeed.bytes_recv.length - 1] }} MB/s
				</small>
				<small class="text-warning">
					<i class="bi bi-arrow-up-circle me-2"></i>
					{{ historicalNetworkSpeed.bytes_sent[historicalNetworkSpeed.bytes_sent.length - 1] }} MB/s
				</small>
			</div>
			<div class="card-body">
				<Line
					:options="networkSpeedChartOption"
					:data="networkSpeedHistoricalChartData"
					style="width: 100%; height: 300px; max-height: 300px"
				></Line>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>