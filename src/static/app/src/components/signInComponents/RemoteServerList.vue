<script>
import RemoteServer from "@/components/signInComponents/RemoteServer.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "RemoteServerList",
	setup(){
		const store = DashboardConfigurationStore();
		return {store}
	},
	components: {RemoteServer}
}
</script>

<template>
<div class="w-100 mt-3">
	<div class="d-flex align-items-center">
		<h5 class="mb-0">Server List</h5>
		<button 
			@click="this.store.addCrossServerConfiguration()"
			class="btn bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle shadow-sm ms-auto">
			<i class="bi bi-plus-circle-fill me-2"></i>Server
		</button>
	</div>
	<div class="w-100 py-3 d-flex gap-3 flex-column" style="height: 400px">
		<RemoteServer v-for="(server, index) in this.store.CrossServerConfiguration.ServerList" 
		              @delete="this.store.CrossServerConfiguration.ServerList.splice(index, 1)"
		              :server="server"></RemoteServer>
	</div>
</div>
</template>

<style scoped>

</style>