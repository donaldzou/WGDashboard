<script>
import {fetchGet} from "@/utilities/fetch.js";
import Peer from "@/components/configurationComponents/peer.vue";
import { Line, Bar } from 'vue-chartjs'
import {
	Chart,
	ArcElement,
	LineElement,
	BarElement,
	PointElement,
	BarController,
	BubbleController,
	DoughnutController,
	LineController,
	PieController,
	PolarAreaController,
	RadarController,
	ScatterController,
	CategoryScale,
	LinearScale,
	LogarithmicScale,
	RadialLinearScale,
	TimeScale,
	TimeSeriesScale,
	Decimation,
	Filler,
	Legend,
	Title,
	Tooltip
} from 'chart.js';

Chart.register(
	ArcElement,
	LineElement,
	BarElement,
	PointElement,
	BarController,
	BubbleController,
	DoughnutController,
	LineController,
	PieController,
	PolarAreaController,
	RadarController,
	ScatterController,
	CategoryScale,
	LinearScale,
	LogarithmicScale,
	RadialLinearScale,
	TimeScale,
	TimeSeriesScale,
	Decimation,
	Filler,
	Legend,
	Title,
	Tooltip
);

import dayjs from "dayjs";

export default {
	name: "configuration",
	components: {Peer, Line, Bar},
	data(){
		return {
			loading: false,
			error: null,
			configurationInfo: [],
			configurationPeers: [],
			historyDataSentDifference: [],
			historyDataReceivedDifference: [],
			
			historySentData: {
				labels: [],
				datasets: [
					{
						label: 'Data Sent',
						data: [],
						fill: false,
						borderColor: '#198754',
						tension: 0
					},
				],
			},
			historyReceiveData: {
				labels: [],
				datasets: [
					{
						label: 'Data Received',
						data: [],
						fill: false,
						borderColor: '#0d6efd',
						tension: 0
					},
				],
			},
		}
	},
	watch: {
		'$route.params': {
			immediate: true,
			handler(){
				clearInterval(this.interval)
				this.loading = true;
				let id = this.$route.params.id;
				this.configurationInfo = [];
				this.configurationPeers = [];
				if (id){
					this.getPeers(id)
					this.interval = setInterval(() => {
						this.getPeers(id)
					}, 2000)
				}
			}
		}
	},
	beforeRouteLeave(){
		clearInterval(this.interval)	
	},
	methods:{
		getPeers(id){
			fetchGet("/api/getWireguardConfigurationInfo",
				{
					configurationName: id
				}, (res) => {
					this.configurationInfo = res.data.configurationInfo;
					this.configurationPeers = res.data.configurationPeers;
					this.loading = false;
					if (this.configurationPeers.length > 0){
						const sent = this.configurationPeers.map(x => x.total_sent + x.cumu_sent).reduce((x,y) => x + y).toFixed(4);
						const receive = this.configurationPeers.map(x => x.total_receive + x.cumu_receive).reduce((x,y) => x + y).toFixed(4);
						if (
							this.historyDataSentDifference[this.historyDataSentDifference.length - 1] !== sent
						){
							if (this.historyDataSentDifference.length > 0){
								this.historySentData = {
									labels: [...this.historySentData.labels, dayjs().format("HH:mm:ss A")],
									datasets: [
										{
											label: 'Data Sent',
											data: [...this.historySentData.datasets[0].data,
												((sent - this.historyDataSentDifference[this.historyDataSentDifference.length - 1])*1000).toFixed(4)],
											fill: false,
											borderColor: ' #198754',
											tension: 0
										}
									],
								}
							}
							this.historyDataSentDifference.push(sent)
						}
						if (
							this.historyDataReceivedDifference[this.historyDataReceivedDifference.length - 1] !== receive
						){
							if (this.historyDataReceivedDifference.length > 0){
								this.historyReceiveData = {
									labels: [...this.historyReceiveData.labels, dayjs().format("HH:mm:ss A")],
									datasets: [
										{
											label: 'Data Received',
											data: [...this.historyReceiveData.datasets[0].data,
												((receive - this.historyDataReceivedDifference[this.historyDataReceivedDifference.length - 1])*1000).toFixed(4)],
											fill: false,
											borderColor: '#0d6efd',
											tension: 0
										}
									],
								}
							}
							this.historyDataReceivedDifference.push(receive)
						}
					}
				});
		}	
	},
	computed: {
		configurationSummary(){
			return {
				connectedPeers: this.configurationPeers.filter(x => x.status === "running").length,
				totalUsage: this.configurationPeers.length > 0 ? this.configurationPeers.map(x => x.total_data + x.cumu_data).reduce((a, b) => a + b) : 0,
				totalReceive: this.configurationPeers.length > 0 ? this.configurationPeers.map(x => x.total_receive + x.cumu_receive).reduce((a, b) => a + b) : 0,
				totalSent: this.configurationPeers.length > 0 ? this.configurationPeers.map(x => x.total_sent + x.cumu_sent).reduce((a, b) => a + b) : 0
			}
		},
		receiveData(){
			return this.historyReceiveData
		},
		sentData(){
			return this.historySentData
		},
		individualDataUsage(){
			return {
				labels: this.configurationPeers.map(x => {
					if (x.name) return x.name
					return `Untitled Peer - ${x.id}`
				}),
				datasets: [{
					label: 'Total Data Usage',
					data: this.configurationPeers.map(x => x.cumu_data + x.total_data),
					backgroundColor: this.configurationPeers.map(x => `#0dcaf0`),
					tooltip: {
						callbacks: {
							label: (tooltipItem) => {
								console.log(tooltipItem)
								return `${tooltipItem.formattedValue} GB`
							}
						}
					}
				}]
			}	
		},
		individualDataUsageChartOption(){
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
								return `${val} GB`
							}
						},
						grid: {
							display: false
						},
					}
				}
			}	
		},
		chartOptions() {
			return {
				responsive: true,
				plugins: {
					legend: {
						display: false
					},
					tooltip: {
						callbacks: {
							label: (tooltipItem) => {
								console.log(tooltipItem)
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
								return `${val} MB/s`
							}
						},
						grid: {
							display: false
						},
					}
				}
			}
		}
	}
}
</script>

<template>
	<div class="mt-5 text-body" v-if="!loading">
		<div>
			<small CLASS="text-muted">CONFIGURATION</small>
			<div class="d-flex align-items-center gap-3">
				<h1 class="mb-0"><samp>{{this.configurationInfo.Name}}</samp></h1>
				<div class="dot active ms-0"></div>
			</div>
		</div>
		<div class="row mt-3 gy-2">
			<div class="col-sm-3">
				<p class="mb-0 text-muted"><small>Address</small></p>
				{{this.configurationInfo.Address}}
			</div>
			<div class="col-sm-3">
				<p class="mb-0 text-muted"><small>Listen Port</small></p>
				{{this.configurationInfo.ListenPort}}
			</div>
			<div style="word-break: break-all" class="col-sm-6">
				<p class="mb-0 text-muted"><small>Public Key</small></p>
				<samp>{{this.configurationInfo.PublicKey}}</samp>
			</div>
			<div class="col-sm-3">
				<p class="mb-1 text-muted"><small>Connected Peers</small></p>
				<i class="bi bi-ethernet me-2"></i><strong>{{configurationSummary.connectedPeers}}</strong>
			</div>
			<div class="col-sm-3">
				<p class="mb-0 text-muted"><small>Total Usage</small></p>
				<i class="bi bi-arrow-down-up me-2"></i><strong>{{configurationSummary.totalUsage.toFixed(4)}}</strong> GB
			</div>
			<div class="col-sm-3">
				<p class="mb-0 text-muted"><small>Total Received</small></p>
				<i class="bi bi-arrow-down me-2"></i><strong>{{configurationSummary.totalReceive.toFixed(4)}}</strong> GB
			</div>
			<div class="col-sm-3">
				<p class="mb-0 text-muted"><small>Total Sent</small></p>
				<i class="bi bi-arrow-up me-2"></i><strong>{{configurationSummary.totalSent.toFixed(4)}}</strong> GB
			</div>
		</div>
		<div class="row mt-3 gx-2 gy-2 mb-2">
			<div class="col-sm ">
				<div class="card rounded-3 bg-transparent">
					<div class="card-header bg-transparent border-0"><small>Peers Total Data Usage</small></div>
					<div class="card-body pt-1">
						<Bar
							:data="individualDataUsage"
							:options="individualDataUsageChartOption"
							style="height: 150px; width: 100%"></Bar>
					</div>
				</div>
				
			</div>
			<div class="col-sm">
				<div class="card rounded-3 bg-transparent">
					<div class="card-header bg-transparent border-0"><small>Real Time Received Data Usage</small></div>
					<div class="card-body pt-1">
						<Line
							:options="chartOptions"
							:data="receiveData"
							style="width: 100%; height: 150px"
						></Line>
					</div>
				</div>
			</div>
			<div class="col-sm">
				<div class="card rounded-3 bg-transparent">
					<div class="card-header bg-transparent border-0"><small>Real Time Sent Data Usage</small></div>
					<div class="card-body  pt-1">
						<Line
							:options="chartOptions"
							:data="sentData"
							style="width: 100%; height: 150px"
						></Line>
					</div>
				</div>
			</div>
		</div>
		<hr>
		<div class="row gx-2 gy-2">
			<div class="col-12 col-lg-6 col-xl-4" v-for="peer in this.configurationPeers">
				<Peer :Peer="peer"></Peer>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>