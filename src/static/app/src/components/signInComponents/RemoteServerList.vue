<script>
import RemoteServer from "@/components/signInComponents/RemoteServer.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "RemoteServerList",
	setup(){
		const store = DashboardConfigurationStore();
		return {store}
	},
	components: {LocaleText, RemoteServer}
}
</script>

<template>
<div class="w-100 mt-3">
	<div class="d-flex align-items-center mb-3">
		<h5 class="mb-0">
			<LocaleText t="Server List"></LocaleText>
		</h5>
		<button 
			@click="this.store.addCrossServerConfiguration()"
			class="btn bg-primary-subtle text-primary-emphasis border-1 border-primary-subtle shadow-sm ms-auto">
			<i class="bi bi-plus-circle-fill me-2"></i>
			<LocaleText t="Server"></LocaleText>
		</button>
	</div>
	<div class="w-100 d-flex gap-3 flex-column p-3 border border-1 border-secondary-subtle rounded-3" 
	     style="height: 400px; overflow-y: scroll">
		<RemoteServer v-for="(server, key) in this.store.CrossServerConfiguration.ServerList"
		              @setActiveServer="this.store.setActiveCrossServer(key)"
		              @delete="this.store.deleteCrossServerConfiguration(key)"
		              :key="key"
		              :server="server"></RemoteServer>
		<h6 class="text-muted m-auto" v-if="Object.keys(this.store.CrossServerConfiguration.ServerList).length === 0">
			<LocaleText t="Click"></LocaleText>
			<i class="bi bi-plus-circle-fill mx-1"></i>
			<LocaleText t="to add your server"></LocaleText>
		</h6>
	</div>
</div>
</template>

<style scoped>

</style>