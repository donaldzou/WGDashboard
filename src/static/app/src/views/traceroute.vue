<script>
import {fetchGet} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";

export default {
	name: "traceroute",
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
	<div class="mt-5 text-body">
		<div class="container">
			<h3 class="mb-3 text-body">Traceroute</h3>
			<div class="row">
				<div class="col-sm-4 d-flex gap-2 flex-column">
					<div>
						<label class="mb-1 text-muted" for="ipAddress">
							<small>IP Address</small></label>
						<input 
							id="ipAddress"
							class="form-control"
							v-model="this.ipAddress"
							type="text" placeholder="Enter an IP Address you want to trace :)">
					</div>
					<button class="btn btn-primary rounded-3 mt-3"
					        :disabled="!this.store.regexCheckIP(this.ipAddress) || this.tracing"
					        @click="this.execute()">
						<i class="bi bi-bullseye me-2"></i> {{this.tracing ? "Tracing...":"Trace It!"}}
					</button>
				</div>
				<div class="col-sm-8 position-relative">
					<TransitionGroup name="ping">
						<div v-if="!this.tracerouteResult" key="pingPlaceholder">
							<div class="pingPlaceholder bg-body-secondary rounded-3 mb-3"
							     :class="{'animate__animated animate__flash animate__slower animate__infinite': this.tracing}"
							     :style="{'animation-delay': `${x*0.05}s`}"
							     v-for="x in 10" ></div>
						</div>
						<div v-else key="table" class="w-100">
							<table class="table table-borderless rounded-3 w-100">
								<thead>
								<tr>
									<th scope="col">Hop</th>
									<th scope="col">IP Address</th>
									<th scope="col">Average / Min / Max Round Trip Time</th>
								</tr>
								</thead>
								<tbody>
									<tr v-for="(hop, key) in this.tracerouteResult"
										class="animate__fadeInUp animate__animated"
									    :style="{'animation-delay': `${key * 0.05}s`}"
									>
										<td>{{hop.hop}}</td>
										<td>{{hop.ip}}</td>
										<td>{{hop.avg_rtt}} / {{hop.min_rtt}} / {{hop.max_rtt}}</td>
									</tr>
								</tbody>
								
							</table>
						</div>
					</TransitionGroup>
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
	padding: 0.9rem;
}

table tbody{
	border-top: 1em solid transparent;
}

.table > :not(caption) > * > *{
	background-color: transparent !important;
}
</style>