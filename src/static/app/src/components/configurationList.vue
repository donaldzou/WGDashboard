<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import ConfigurationCard from "@/components/configurationListComponents/configurationCard.vue";

export default {
	name: "configurationList",
	components: {ConfigurationCard},
	async setup(){
		const wireguardConfigurationsStore = WireguardConfigurationsStore();
		
		return {wireguardConfigurationsStore}
	},
	data(){
		return {
			configurationLoaded: false
		}
	},
	async mounted() {
		await this.wireguardConfigurationsStore.getConfigurations();
		this.configurationLoaded = true;
	}
}
</script>

<template>
	
	<div class="mt-4">
		<div class="container">
			<div class="d-flex mb-4 ">
				<h3 class="text-body">WireGuard Configurations</h3>
				<RouterLink to="/new_configuration" class="btn btn-dark btn-brand rounded-3 px-3 py-2 shadow ms-auto rounded-3">
					Configuration
					<i class="bi bi-plus-circle-fill ms-2"></i>
				</RouterLink>
			</div>
			<Transition name="fade" mode="out-in">
				<div v-if="this.configurationLoaded">
					<p class="text-muted" v-if="this.wireguardConfigurationsStore.Configurations.length === 0">
						You don't have any WireGuard configurations yet. Please check the configuration folder or change it in "Settings". By default the folder is "/etc/wireguard".
					</p>

					<div class="d-flex gap-3 flex-column" v-else>
						<ConfigurationCard  v-for="c in this.wireguardConfigurationsStore.Configurations" :key="c.Name" :c="c"></ConfigurationCard>
					</div>
				</div>
			</Transition>
			
		</div>
	</div>
	
</template>

<style scoped>

</style>