<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {useRoute, useRouter} from "vue-router";
import {ref} from "vue";
import {fetchPost} from "@/utilities/fetch.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
const route = useRoute()
const configurationName = route.params.id;
const input = ref("")
const router = useRouter()
const store = DashboardConfigurationStore()
const deleting = ref(false)

const deleteConfiguration = () => {
	clearInterval(store.Peers.RefreshInterval)
	deleting.value = true;
	fetchPost("/api/deleteWireguardConfiguration", {
		Name: configurationName
	}, (res) => {
		if (res.status){
			router.push('/')
			store.newMessage("Server", "Configuration deleted", "success")
		}else{
			deleting.value = false;
		}
	})
}
</script>

<template>
	<div class="peerSettingContainer w-100 h-100 position-absolute top-0 start-0 overflow-y-scroll" ref="editConfigurationContainer">
		<div class="container d-flex h-100 w-100">
			<div class="m-auto modal-dialog-centered dashboardModal" style="width: 700px">
				<div class="card rounded-3 shadow flex-grow-1 bg-danger-subtle border-danger-subtle">
					<div class="card-header bg-transparent d-flex align-items-center gap-2 border-0 p-4 pb-0">
						<h5 class="mb-0">
							Are you sure to delete this configuration?
						</h5>
						<button type="button" class="btn-close ms-auto" @click="$emit('close')"></button>
					</div>
					<div class="card-body px-4">
						
						<p class="text-muted">
							Once you deleted, all connected peers will get disconnected; Both configuration file 
							(<code>.conf</code>) and database table related to this configuration will get deleted.
						</p>
						<hr>
						<p>If you're sure, please type in the configuration name below and click Delete.</p>
						<input class="form-control rounded-3 mb-3" 
						       :placeholder="configurationName"
						       v-model="input"
						       type="text">
						<button class="btn btn-danger w-100" 
						        @click="deleteConfiguration()"
						        :disabled="input !== configurationName || deleting">
							<i class="bi bi-trash-fill me-2 rounded-3"></i>
							Delete
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>