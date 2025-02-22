<script>
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";
import OSMap from "@/components/map/osmap.vue";
import { io } from "socket.io-client"
import {v4} from "uuid";
import {ref} from "vue";
import OsmapSocket from "@/components/map/osmapSocket.vue";


export default {
	name: "ping",
	components: {OsmapSocket, OSMap, LocaleText},
	data(){
		return {
			loading: false,
			cips: {},
			selectedConfiguration: undefined,
			selectedPeer: undefined,
			selectedIp: undefined,
			pingResult: undefined,
			
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		let sio;
		const socketResult = ref({
			pingTotalSentCount: 0,
			pingReceivedSentCount: 0,
			pingLostCount: 0,
			pingResults: []
		})
		const count = ref(4)
		const pinging = ref(false)
		try{
			sio = io();
			sio.connect()
			console.info("Successfully connected to socket.io")
		}catch (e){
			console.assert("Failed to connect socket.io")
		}
		sio.on('pingResponse', (...arg) => {
			let data = arg[0].data
			data.id = v4().toString()
			socketResult.value.pingResults.push(data)
			if (socketResult.value.pingResults.length === count.value){
				pinging.value = false
			}
		})
		return {store, sio, socketResult, count, pinging}
	},
	beforeUnmount() {
		if(this.sio && this.sio.connected){
			this.sio.disconnect()
			console.info("Successfully disconnected from socket.io")
		}	
	},
	mounted() {
		fetchGet("/api/ping/getAllPeersIpAddress", {}, (res)=> {
			if (res.status){
				this.loading = true;
				this.cips = res.data;
			}
		});
	},
	methods: {
		executeSocket(){
			if (this.sio.connected){
				this.socketResult.pingResults = [];
				this.pinging = true;
				this.sio.emit('ping', {
					ipAddress: this.selectedIp,
					count: this.count
				});
			}
		}
	},
	watch: {
		selectedConfiguration(){
			this.selectedPeer = undefined;
			this.selectedIp = undefined;
		},
		selectedPeer(){
			this.selectedIp = undefined;
		}
	}
}
</script>

<template>
	<div class="mt-md-5 mt-3 text-body">
		<div class="container">
			<h3 class="mb-3 text-body">Ping</h3>
			<div class="row">
				<div class="col-sm-4 d-flex gap-2 flex-column">
					<div>
						<label class="mb-1 text-muted" for="configuration">
							<small>
								<LocaleText t="Configuration"></LocaleText>
							</small></label>
						<select class="form-select" v-model="this.selectedConfiguration" :disabled="this.pinging">
							<option disabled selected :value="undefined"></option>
							<option :value="key" v-for="(val, key) in this.cips">
								{{key}}
							</option>
						</select>
					</div>
					<div>
						<label class="mb-1 text-muted" for="peer">
							<small>
								<LocaleText t="Peer"></LocaleText>
							</small></label>
						<select id="peer" class="form-select" v-model="this.selectedPeer" :disabled="this.selectedConfiguration === undefined || this.pinging">
							<option disabled selected :value="undefined"></option>
							<option v-if="this.selectedConfiguration !== undefined" :value="key" v-for="(peer, key) in 
								this.cips[this.selectedConfiguration]">
								{{key}}
							</option>
						</select>
					</div>
					<div>
						<label class="mb-1 text-muted" for="ip">
							<small>
								<LocaleText t="IP Address"></LocaleText>
							</small></label>
						<select id="ip" class="form-select" v-model="this.selectedIp" :disabled="this.selectedPeer === undefined || this.pinging">
							<option disabled selected :value="undefined"></option>
							<option
								v-if="this.selectedPeer !== undefined"
								v-for="ip in this.cips[this.selectedConfiguration][this.selectedPeer].allowed_ips">
								{{ip}}
							</option>
						</select>
					</div>
					<div class="d-flex align-items-center gap-2">
						<div class="flex-grow-1 border-top"></div>
						<small class="text-muted">
							<LocaleText t="OR"></LocaleText>
						</small>
						<div class="flex-grow-1 border-top"></div>
					</div>
					<div>
						<label class="mb-1 text-muted" for="ipAddress">
							<small>
								<LocaleText t="Enter IP Address / Hostname"></LocaleText>
							</small></label>
						<input class="form-control" type="text"
						       id="ipAddress"
						       :disabled="this.pinging"
						       v-model="this.selectedIp">
					</div>
					<div class="w-100 border-top my-2"></div>
					<div>
						<label class="mb-1 text-muted" for="count">
							<small>
								<LocaleText t="Count"></LocaleText>
							</small></label>
						
						<div class="d-flex gap-3 align-items-center">
							<button  @click="this.count--" 
							         :disabled="this.count === 1"
							         class="btn btn-sm bg-secondary-subtle text-secondary-emphasis">
								<i class="bi bi-dash-lg"></i>
							</button>
							<strong>{{this.count}}</strong>
							<button role="button" @click="this.count++" class="btn btn-sm bg-secondary-subtle text-secondary-emphasis">
								<i class="bi bi-plus-lg"></i>
							</button>
						</div>
					</div>
					<button class="btn btn-primary rounded-3 mt-3 position-relative" 
					        :disabled="!this.selectedIp || this.pinging"
					        @click="this.executeSocket()">
						<Transition name="slide">
							<span v-if="!this.pinging" class="d-block">
								<i class="bi bi-person-walking me-2"></i>Ping!
							</span>
							<span v-else class="d-block">
								<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
								<span class="visually-hidden" role="status">Loading...</span>
							</span>
						</Transition>
					</button>
				</div>
				
				<div class="col-sm-8 position-relative d-flex flex-column gap-2 animate__fadeIn animate__animated ">
					<Suspense>
						<OsmapSocket :d="this.socketResult.pingResults"
						             key="OSMap"
						             type="traceroute"></OsmapSocket>
						<template #fallback>
							<div class="bg-body-secondary rounded-3 mb-3 d-flex"
							     key="OSMapPlaceholder"
							     style="height: 300px"
							>
								<div class="spinner-border m-auto"
								     style="animation-duration: 2s"
								     role="status">
									<span class="visually-hidden">Loading...</span>
								</div>
							</div>
						</template>
					</Suspense>
					<div key="pingResultTable">
						<div key="table" class="w-100 mt-2">
							<table class="table table-sm rounded-3 w-100">
								<thead>
								<tr>
									
									<th scope="col">
										<LocaleText t="IP Address"></LocaleText>
									</th>
									<th scope="col">
										<LocaleText t="Is Alive?"></LocaleText>
									</th>
									<th scope="col">
										<LocaleText t="Round-Trip Time (ms)"></LocaleText>
									</th>
									
									<th scope="col">
										<LocaleText t="Geolocation"></LocaleText>
									</th>
								</tr>
								</thead>
								<tbody>
									<tr v-for="(hop, key) in socketResult.pingResults">
										<td>
											<small>{{hop.address}}</small>
										</td>
										<td>
											<small>
												<i class="bi" 
												   :class="[hop.is_alive ? 'bi-check-circle-fill text-success' :
												    'bi-x-circle-fill text-danger']"></i>
											</small>
										</td>
										<td>
											<small>{{ hop.is_alive ? hop.max_rtt : ''}}</small>
										</td>
										<td>
											<small v-if="hop.geo && hop.geo.status === 'success'">
												{{ hop.geo.city }}, {{ hop.geo.country }}</small>
										</td>
									</tr>
									<tr v-if="socketResult.pingResults.length === 0">
										<td colspan="4" class="text-muted text-center">
											<small>
												<LocaleText t="Ping results will show here"></LocaleText>
											</small>
										</td>
									</tr>
									<tr class="bg-body-tertiary border-top fw-bold" style="border-top: 2px solid !important;">
										<td>
											<small>
												<LocaleText t="Sent Package(s)"></LocaleText>
											</small>
										</td>
										<td>
											<small>
												<LocaleText t="Received Package(s)"></LocaleText>
											</small>
										</td>
										<td>
											<small>
												<LocaleText t="Lost Package(s)"></LocaleText>
											</small>
										</td>
										<td colspan="2">
											<small>
												<LocaleText t="Average / Min / Max Round Trip Time"></LocaleText>
											</small>
										</td>
									</tr>
									<tr>
										<td class="">
											<small>
												{{ this.socketResult.pingResults.length }}
											</small>
										</td>
										<td class="">
											<small>
												{{ this.socketResult.pingResults.filter(x => x.is_alive).length }}
											</small>
										</td>
										<td class="">
											<small>
												{{ this.socketResult.pingResults.filter(x => !x.is_alive).length }}
											</small>
										</td>
										<td colspan="2">
											<small v-if="this.socketResult.pingResults.filter(x => x.is_alive).length > 0">
												{{ (this.socketResult.pingResults.filter(x => x.is_alive).map(x => x.max_rtt)
													.reduce((x, y) => x + y) / this.socketResult.pingResults.filter(x => x.is_alive).length ).toFixed(3)}}ms / 
												{{ Math.min(...this.socketResult.pingResults.filter(x => x.is_alive).map(x => x.max_rtt)) }}ms / 
												{{ Math.max(...this.socketResult.pingResults.filter(x => x.is_alive).map(x => x.max_rtt)) }}ms
											</small>
											<small v-else>
												0ms / 0ms / 0ms
											</small>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

</template>

<style scoped>
	.pingPlaceholder{
		width: 100%;
		height: 79.98px;
	}
	.ping-move,
	.ping-enter-active,
	.ping-leave-active {
		transition: all 0.4s cubic-bezier(0.82, 0.58, 0.17, 0.9);
	}

	.ping-leave-active{
		position: absolute;
		width: 100%;
	}
	.ping-enter-from,
	.ping-leave-to {
		opacity: 0;
		filter: blur(3px);
	}
	table th, table td{
		padding: 0.5rem;
	}

	.table > :not(caption) > * > *{
		background-color: transparent !important;
	}
</style>