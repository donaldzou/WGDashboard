<script>
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import OSMap from "@/components/map/osmap.vue";
import LocaleText from "@/components/text/localeText.vue";
import {io} from "socket.io-client";
import {ref} from "vue";
import {v4} from "uuid";
import OsmapSocket from "@/components/map/osmapSocket.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "traceroute",
	components: {OsmapSocket, LocaleText, OSMap},
	data(){
		return {
			ipAddress: undefined
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		let sio;
		let tracing = ref(false)
		const tracerouteResult = ref([])
		try{
			sio = io();
			sio.connect()
			console.info("Successfully connected to socket.io")
		}catch (e){
			console.assert("Failed to connect socket.io")
		}
		sio.on('tracerouteResponse', (...arg) => {
			let data = arg[0]
			if (data.status && tracing.value){
				console.log(data.data)
				data.data.id = v4().toString()
				tracerouteResult.value.push(data.data)
			}else{
				store.newMessage("Server", data.message, "danger")
				tracing.value = false
			}
		})
		sio.on('tracerouteResponseEnd', () => {
			tracing.value = false
		})
		
		return {store, sio, tracerouteResult, tracing}
	},
	methods: {
		execute(){
			if (this.ipAddress){
				this.tracing = true;
				this.tracerouteResult = undefined
				fetchGet("/api/traceroute/execute", {
					ipAddress: this.ipAddress,
				}, (res) => {
					if (res.status){
						this.tracerouteResult = res.data
					}else{
						this.store.newMessage("Server", res.message, "danger")
					}
					this.tracing = false
				})
			}
		},
		executeSocket(){
			if (this.ipAddress && this.sio.connected){
				this.tracerouteResult = []
				this.tracing = true;
				this.sio.emit('traceroute', {
					ipAddress: this.ipAddress
				})
			}
		}
	},
	
}
</script>

<template>
	<div class="mt-md-5 mt-3 text-body">
		<div class="container-md">
			<h3 class="mb-3 text-body">
				<LocaleText t="Traceroute"></LocaleText>
			</h3>
			<div class="d-flex gap-2 mb-3 flex-column">
				<div class="flex-grow-1">
					<label class="mb-1 text-muted" for="ipAddress">
						<small>
							<LocaleText t="Enter IP Address / Hostname"></LocaleText>
						</small></label>
					<input
						:disabled="this.tracing"
						id="ipAddress"
						class="form-control rounded-3"
						v-model="this.ipAddress"
						@keyup.enter="this.execute()"
						type="text">
				</div>
				<button class="btn btn-primary rounded-3 position-relative flex-grow-1"
				        :disabled="this.tracing || !this.ipAddress"
				        @click="this.executeSocket()">
					<Transition name="slide">
							<span v-if="!this.tracing" class="d-block">
								<i class="bi bi-person-walking me-2"></i>Trace!
							</span>
						<span v-else class="d-block">
								<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
								<span class="visually-hidden" role="status">Loading...</span>
							</span>
					</Transition>
				</button>
			</div>
			<div class="position-relative">
				<OsmapSocket :d="this.tracerouteResult" type="traceroute"></OsmapSocket>
				<div key="table" class="w-100 mt-2">
					<table class="table table-sm rounded-3 w-100">
						<thead>
						<tr>
							<th scope="col">
								<LocaleText t="Hop"></LocaleText>
							</th>
							<th scope="col">
								<LocaleText t="IP Address"></LocaleText>
							</th>
							<th scope="col">
								<LocaleText t="Average RTT (ms)"></LocaleText>
							</th>
							<th scope="col">
								<LocaleText t="Min RTT (ms)"></LocaleText>
							</th>
							<th scope="col">
								<LocaleText t="Max RTT (ms)"></LocaleText>
							</th>
							<th scope="col">
								<LocaleText t="Geolocation"></LocaleText>
							</th>
						</tr>
						</thead>
						<tbody>
						<TransitionGroup name="ping">
							<tr v-for="(hop) in this.tracerouteResult" :key="hop.id">
								<td>
									<small>{{hop.hop}}</small>
								</td>
								<td>
									<small>
										{{hop.ip}}
									</small>
								</td>
								<td>
									<small>
										{{hop.avg_rtt}}
									</small>
								</td>
								<td>
									<small>
										{{hop.min_rtt}}
									</small>
								</td>
								<td>
									<small>
										{{hop.max_rtt}}
									</small>
								</td>
								<td>
								<span v-if="hop.geo && hop.geo.status === 'success'">
									<small>{{hop.geo.city}}, {{hop.geo.country}}</small>
								</span>
								</td>
							</tr>
						</TransitionGroup>
						<tr v-if="tracerouteResult.length === 0">
							<td colspan="6" class="text-muted text-center">
								<small>
									<LocaleText t="Traceroute results will show here"></LocaleText>
								</small>
							</td>
						</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.pingPlaceholder{
	width: 100%;
	height: 40px;
}
.ping-move, /* apply transition to moving elements */
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

.ping-leave-active {
	position: absolute;
}

table th, table td{
	padding: 0.5rem;
}

.table > :not(caption) > * > *{
	background-color: transparent !important;
}
</style>