<script>
import {fetchGet} from "@/utilities/fetch.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";
import OSMap from "@/components/map/osmap.vue";

export default {
	name: "ping",
	components: {OSMap, LocaleText},
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
					this.pinging = false
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
					        @click="this.execute()">
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
				
				<div class="col-sm-8 position-relative">
					<Transition name="ping">
						<div v-if="!this.pingResult" key="pingPlaceholder">
							<div class="pingPlaceholder bg-body-secondary rounded-3 mb-3"
							     style="height: 300px"
							></div>
							<div class="pingPlaceholder bg-body-secondary rounded-3 mb-3"
							      :class="{'animate__animated animate__flash animate__slower animate__infinite': this.pinging}"
							     :style="{'animation-delay': `${x*0.15}s`}"
							     v-for="x in 4" ></div>
							
						</div>

						<div v-else key="pingResult" class="d-flex flex-column gap-2 w-100">
							<OSMap :d="this.pingResult" v-if="this.pingResult.geo && this.pingResult.geo.status === 'success'"></OSMap>
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.15s">
								<div class="card-body row">
									<div class="col-sm">
										<p class="mb-0 text-muted">
											<small>
												<LocaleText t="IP Address"></LocaleText>
											</small>
										</p>
										{{this.pingResult.address}}
									</div>
									<div class="col-sm" v-if="this.pingResult.geo && this.pingResult.geo.status === 'success'">
										<p class="mb-0 text-muted">
											<small>
												<LocaleText t="Geolocation"></LocaleText>
											</small>
										</p>
										{{this.pingResult.geo.city}}, {{this.pingResult.geo.country}}
									</div>
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
									<p class="mb-0 text-muted"><small>
										<LocaleText t="Average / Min / Max Round Trip Time"></LocaleText>
									</small></p>
									<samp>{{this.pingResult.avg_rtt}}ms / 
										{{this.pingResult.min_rtt}}ms / 
										{{this.pingResult.max_rtt}}ms
									</samp>
								</div>
							</div>
							<div class="card rounded-3 bg-transparent shadow-sm animate__animated animate__fadeIn" style="animation-delay: 0.6s">
								<div class="card-body">
									<p class="mb-0 text-muted"><small>
										<LocaleText t="Sent / Received / Lost Package"></LocaleText>
									</small></p>
									<samp>{{this.pingResult.package_sent}} /
										{{this.pingResult.package_received}} /
										{{this.pingResult.package_loss}}
									</samp>
								</div>
							</div>
						</div>
					</Transition>
					

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
		width: 100%;
	}
	.ping-enter-from,
	.ping-leave-to {
		opacity: 0;
		//transform: scale(1.1);
		filter: blur(3px);
	}
</style>