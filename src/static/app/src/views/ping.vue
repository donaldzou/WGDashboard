<script>
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "ping",
	data(){
		return {
			loading: false,
			cips: {},
			selectedConfiguration: undefined,
			selectedPeer: undefined,
			selectedIp: undefined,
			count: 4,
			pingResult: undefined,
			pinging: false
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		return {store}
	},
	mounted() {
		fetchGet("/api/ping/getAllPeersIpAddress", {}, (res)=> {
			if (res.status){
				this.loading = true;
				this.cips = res.data;
				console.log(this.cips)
			}
		});
	},
	methods: {
		execute(){
			if (this.selectedIp){
				this.pinging = true;
				this.pingResult = undefined
				fetchGet("/api/ping/execute", {
					ipAddress: this.selectedIp,
					count: this.count
				}, (res) => {
					if (res.status){
						this.pingResult = res.data
					}else{
						this.store.newMessage("Server", res.message, "danger")
					}
				})
			}
{}		}	
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
	<div class="mt-5 text-body">
		<div class="container">
			<h3 class="mb-3 text-body">Ping</h3>
			<div class="row">
				<div class="col-sm-4 d-flex gap-2 flex-column">
					<div>
						<label class="mb-1 text-muted" for="configuration">
							<small>Configuration</small></label>
						<select class="form-select" v-model="this.selectedConfiguration">
							<option disabled selected :value="undefined">Select a Configuration...</option>
							<option :value="key" v-for="(val, key) in this.cips">
								{{key}}
							</option>
						</select>
					</div>
					<div>
						<label class="mb-1 text-muted" for="peer">
							<small>Peer</small></label>
						<select id="peer" class="form-select" v-model="this.selectedPeer" :disabled="this.selectedConfiguration === undefined">
							<option disabled selected :value="undefined">Select a Peer...</option>
							<option v-if="this.selectedConfiguration !== undefined" :value="key" v-for="(peer, key) in 
								this.cips[this.selectedConfiguration]">
								{{key}}
							</option>
						</select>
					</div>
					<div>
						<label class="mb-1 text-muted" for="ip">
							<small>IP Address</small></label>
						<select id="ip" class="form-select" v-model="this.selectedIp" :disabled="this.selectedPeer === undefined">
							<option disabled selected :value="undefined">Select a IP...</option>
							<option
								v-if="this.selectedPeer !== undefined"
								v-for="ip in this.cips[this.selectedConfiguration][this.selectedPeer].allowed_ips">
								{{ip}}
							</option>
						</select>
					</div>
					<div>
						<label class="mb-1 text-muted" for="count">
							<small>Ping Count</small></label>
						<input class="form-control" type="number" 
						       v-model="this.count"
						       min="1" id="count" placeholder="How many times you want to ping?">
					</div>
					<button class="btn btn-primary rounded-3 mt-3" 
					        :disabled="!this.selectedIp"
					        @click="this.execute()">
						<i class="bi bi-person-walking me-2"></i>Go!
					</button>
				</div>
				
				<div class="col-sm-8">
					<TransitionGroup name="ping">
						<div v-if="!this.pingResult" key="pingPlaceholder">
							<div class="pingPlaceholder bg-dark rounded-3 mb-3"
							      :class="{'animate__animated animate__flash animate__slower animate__infinite': this.pinging}"
							     :style="{'animation-delay': `${x*0.15}s`}"
							     v-for="x in 4" ></div>
						</div>

						<div v-else key="pingResult" class="d-flex flex-column gap-2 w-100">
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.15s">
								<div class="card-body">
									<p class="mb-0 text-muted"><small>Address</small></p>
									{{this.pingResult.address}}
								</div>
							</div>
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.3s">
								<div class="card-body">
									<p class="mb-0 text-muted"><small>Is Alive</small></p>
									<span :class="[this.pingResult.is_alive ? 'text-success':'text-danger']">
												<i class="bi me-1"
												   :class="[this.pingResult.is_alive ? 'bi-check-circle-fill' : 'bi-x-circle-fill']"></i>
												{{this.pingResult.is_alive ? "Yes": "No"}}
									</span>
								</div>
							</div>
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.45s">
								<div class="card-body">
									<p class="mb-0 text-muted"><small>Average / Min / Max Round Trip Time</small></p>
									<samp>{{this.pingResult.avg_rtt}}ms / 
										{{this.pingResult.min_rtt}}ms / 
										{{this.pingResult.max_rtt}}ms
									</samp>
								</div>
							</div>
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.6s">
								<div class="card-body">
									<p class="mb-0 text-muted"><small>Sent / Received / Lost Package</small></p>
									<samp>{{this.pingResult.package_sent}} /
										{{this.pingResult.package_received}} /
										{{this.pingResult.package_loss}}
									</samp>
								</div>
							</div>
							
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
		height: 79.98px;
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
</style>