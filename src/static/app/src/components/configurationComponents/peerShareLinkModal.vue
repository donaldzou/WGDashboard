<script>
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {fetchPost} from "@/utilities/fetch.js";
import dayjs from "dayjs";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import VueDatePicker from '@vuepic/vue-datepicker';


export default {
	name: "peerShareLinkModal",
	props: {
		peer: Object
	},
	components: {
		VueDatePicker
	},
	data(){
		return {
			dataCopy: undefined,
			loading: false
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		return {store}
	},
	mounted() {
		this.dataCopy = JSON.parse(JSON.stringify(this.peer.ShareLink)).at(0);
	},
	methods: {
		startSharing(){
			this.loading = true;
			fetchPost("/api/sharePeer/create", {
				Configuration: this.peer.configuration.Name,
				Peer: this.peer.id,
				ExpireDate: dayjs().add(30, 'd').format("YYYY-MM-DD hh:mm:ss")
			}, (res) => {
				if (res.status){
					this.peer.ShareLink = res.data;
					this.dataCopy = res.data;
					this.store.newMessage("Server", "Share link created successfully", "success")
				}else{
					this.store.newMessage("Server", 
						"Share link failed to create. Reason: " + res.message, "danger")

				}
				this.loading = false;
			})
		},
		updateLinkExpireDate(){
			fetchPost("/api/sharePeer/update", this.dataCopy, (res) => {
				console.log(res)
			})
		}
	},
	computed: {
		getUrl(){
			return window.location.origin 
				+ window.location.pathname 
				+ this.$router.resolve(
					{path: "/share", query: {"ShareID": this.dataCopy.ShareID}}).href;
		}
	},
	watch: {
		'dataCopy.ExpireDate'(){
			this.updateLinkExpireDate()
		}
	}
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal" style="width: 500px">
				<div class="card rounded-3 shadow flex-grow-1">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4">
						<h4 class="mb-0">Share Peer</h4>
						<button type="button" class="btn-close ms-auto" @click="this.$emit('close')"></button>
					</div>
					<div class="card-body px-4 pb-4" v-if="this.peer.ShareLink">
						<div v-if="!this.dataCopy">
							<h6 class="mb-3 text-muted">
								Currently the peer is not sharing
							</h6>
							<button 
								@click="this.startSharing()"
								:disabled="this.loading"
								class="w-100 btn bg-success-subtle text-success-emphasis border-1 border-success-subtle rounded-3 shadow-sm">
								<span :class="{'animate__animated animate__flash animate__infinite animate__slower': this.loading}">
									<i class="bi bi-send-fill me-2" ></i>
								</span>
								{{this.loading ? "Sharing...":"Start Sharing"}}
							</button>
						</div>
						<div v-else>
							<div class="d-flex gap-2 mb-4">
								<i class="bi bi-link-45deg"></i>
								<a :href="this.getUrl" 
								   class="text-decoration-none" target="_blank">
									{{ getUrl }}
								</a>
							</div>
							<div class="d-flex flex-column gap-2">
								<small>
									<i class="bi bi-calendar me-2"></i>
									Expire Date
								</small>
								<VueDatePicker v-model="this.dataCopy.ExpireDate" time-picker-inline
								               format="yyyy-MM-dd HH:mm:ss"
								               :dark="this.store.Configuration.Server.dashboard_theme === 'dark'"
								/>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>