<script>
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import Map from "@/components/map/map.vue";

export default {
	name: "traceroute",
	components: {Map},
	data(){
		return {
			tracing: false,
			ipAddress: undefined,
			tracerouteResult: undefined
		}
	},
	setup(){
		const store = WireguardConfigurationsStore();
		return {store}
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
		}
	},
	
}
</script>

<template>
	<div class="mt-md-5 mt-3 text-body">
		<div class="container-md">
			<h3 class="mb-3 text-body">Traceroute</h3>
			<div class="d-flex gap-2 flex-column mb-5">
				<div>
					<label class="mb-1 text-muted" for="ipAddress">
						<small>IP Address</small></label>
					<input
						id="ipAddress"
						class="form-control"
						v-model="this.ipAddress"
						@keyup.enter="this.execute()"
						type="text" placeholder="Enter an IP Address you want to trace :)">
				</div>
				<button class="btn btn-primary rounded-3 mt-3"
				        :disabled="this.tracing"
				        @click="this.execute()">
					<i class="bi bi-bullseye me-2"></i> {{this.tracing ? "Tracing...":"Trace It!"}}
				</button>
			</div>
			<div class="position-relative">
				<TransitionGroup name="ping">
					<div v-if="!this.tracerouteResult" key="pingPlaceholder">
						<div class="pingPlaceholder bg-body-secondary rounded-3 mb-3"
						     :class="{'animate__animated animate__flash animate__slower animate__infinite': this.tracing}"
						     :style="{'animation-delay': `${x*0.05}s`}"
						     v-for="x in 5" ></div>
					</div>
					<div v-else>
						<Map :d="this.tracerouteResult" type="traceroute"></Map>
						
						<div key="table" class="w-100 mt-2">
							<table class="table table-sm rounded-3 w-100">
								<thead>
								<tr>
									<th scope="col">Hop</th>
									<th scope="col">IP Address</th>
									<th scope="col">Average RTT (ms)</th>
									<th scope="col">Min RTT (ms)</th>
									<th scope="col">Max RTT (ms)</th>
									<th scope="col">Geolocation</th>
								</tr>
								</thead>
								<tbody>
								<tr v-for="(hop, key) in this.tracerouteResult">
									<td>
										<small>{{hop.hop}}</small>
									</td>
									<td>
										<small>{{hop.ip}}</small>
									</td>
									<td>
										<small>{{hop.avg_rtt}}</small>
									</td>
									<td>
										<small>{{hop.min_rtt}}</small>
									</td>
									<td>
										<small>{{hop.max_rtt}}</small>
									</td>
									<td>
									<span v-if="hop.geo.city && hop.geo.country">
										<small>{{hop.geo.city}}, {{hop.geo.country}}</small>
									</span>
									</td>
								</tr>
								</tbody>

							</table>
						</div>
					</div>
				</TransitionGroup>
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
}

.ping-enter-from,
.ping-leave-to {
	opacity: 0;
	//transform: scale(0.9);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
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