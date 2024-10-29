<script>
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {v4} from "uuid";
import {fetchGet, fetchPost} from "@/utilities/fetch.js";
import NewDashboardAPIKey from "@/components/settingsComponent/dashboardAPIKeysComponents/newDashboardAPIKey.vue";
import DashboardAPIKey from "@/components/settingsComponent/dashboardAPIKeysComponents/dashboardAPIKey.vue";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "dashboardAPIKeys",
	components: {LocaleText, DashboardAPIKey, NewDashboardAPIKey},
	setup(){
		const store = DashboardConfigurationStore();
		return {store};
	},
	data(){
		return {
			value: this.store.Configuration.Server.dashboard_api_key,
			apiKeys: [],
			newDashboardAPIKey: false
		}
	},
	methods: {
		async toggleDashboardAPIKeys(){
			await fetchPost("/api/updateDashboardConfigurationItem", {
				section: "Server",
				key: "dashboard_api_key",
				value: this.value
			}, (res) => {
				if (res.status){
					this.store.Configuration.Peers[this.targetData] = this.value;
					this.store.newMessage("Server", 
						`API Keys function is successfully ${this.value ? 'enabled':'disabled'}`, "success")
				}else{
					this.value = this.store.Configuration.Peers[this.targetData];
					this.store.newMessage("Server",
						`API Keys function is failed to ${this.value ? 'enabled':'disabled'}`, "danger")
				}
			})
		},
	},
	watch: {
		value:{
			immediate: true,
			handler(newValue){
				if (newValue){
					fetchGet("/api/getDashboardAPIKeys", {}, (res) => {
						console.log(res)
						if(res.status){
							this.apiKeys = res.data
						}else{
							this.apiKeys = []
							this.store.newMessage("Server", res.message, "danger")
						}
					})
				}else{
					this.apiKeys = []
				}
			}
		}
	}
}
</script>

<template>
	<div class="card rounded-3">
		<div class="card-body position-relative d-flex flex-column gap-2" >
			<div class="d-flex align-items-center">
				<h5 class="mb-0">
					<LocaleText t="API Keys"></LocaleText>
				</h5>
				<div class="form-check form-switch ms-auto" v-if="!this.store.getActiveCrossServer()" >
					<input class="form-check-input" type="checkbox"
					       v-model="this.value"
					       @change="this.toggleDashboardAPIKeys()"
					       role="switch" id="allowAPIKeysSwitch">
					<label class="form-check-label" for="allowAPIKeysSwitch">
						<LocaleText t="Enabled" v-if="this.value"></LocaleText>
						<LocaleText t="Disabled" v-else></LocaleText>
					</label>
				</div>
			</div>
			<div v-if="this.value" class="d-flex flex-column gap-2">
				<button class="btn bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle rounded-3 shadow-sm"
				        @click="this.newDashboardAPIKey = true"
				        v-if="!this.store.getActiveCrossServer()"
				>
					<i class="bi bi-plus-circle-fill me-2"></i>
					<LocaleText t="API Key"></LocaleText>
				</button>
				<div class="card" style="height: 300px" v-if="this.apiKeys.length === 0">
					<div class="card-body d-flex text-muted">
						<span class="m-auto">
							<LocaleText t="No WGDashboard API Key"></LocaleText>
						</span>
					</div>
				</div>
				<div class="d-flex flex-column gap-2 position-relative" v-else style="min-height: 300px">
					<TransitionGroup name="apiKey">
						<DashboardAPIKey v-for="key in this.apiKeys" :apiKey="key"
						                 :key="key.Key"
						                 @deleted="(nkeys) => this.apiKeys = nkeys"></DashboardAPIKey>
					</TransitionGroup>
				</div>
				<Transition name="zoomReversed">
					<NewDashboardAPIKey v-if="this.newDashboardAPIKey"
					                    @created="(data) => this.apiKeys = data"
					                    @close="this.newDashboardAPIKey = false"
					></NewDashboardAPIKey>
				</Transition>
			</div>
			
		</div>
	</div>
</template>

<style scoped>
.apiKey-move, /* apply transition to moving elements */
.apiKey-enter-active,
.apiKey-leave-active {
	transition: all 0.5s ease;
}

.apiKey-enter-from,
.apiKey-leave-to {
	opacity: 0;
	
	transform: translateY(30px) scale(0.9);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.apiKey-leave-active {
	position: absolute;
	width: 100%;
}
</style>