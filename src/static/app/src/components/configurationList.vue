<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import ConfigurationCard from "@/components/configurationListComponents/configurationCard.vue";
import LocaleText from "@/components/text/localeText.vue";

export default {
	name: "configurationList",
	components: {LocaleText, ConfigurationCard},
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
		
		this.wireguardConfigurationsStore.ConfigurationListInterval = setInterval(() => {
			this.wireguardConfigurationsStore.getConfigurations()
		}, 10000)
	},
	beforeUnmount() {
		clearInterval(this.wireguardConfigurationsStore.ConfigurationListInterval)
	}
}
</script>

<template>
	<div class="mt-md-5 mt-3">
		<div class="container-md">
			<div class="d-flex mb-4 configurationListTitle align-items-center gap-3">
				<h2 class="text-body d-flex">
					<span>
						<LocaleText t="WireGuard Configurations"></LocaleText>
					</span>
				</h2>
				<RouterLink to="/new_configuration"
				            class="btn btn-dark btn-brand rounded-3 p-2 shadow ms-auto rounded-3">
					<h2 class="mb-0" style="line-height: 0">
						<i class="bi bi-plus-circle"></i>
					</h2>
				</RouterLink>
				<RouterLink to="/restore_configuration"
				            class="btn btn-dark btn-brand p-2 shadow ms-2" style="border-radius: 100%">
					<h2 class="mb-0" style="line-height: 0">
						<i class="bi bi-clock-history "></i>
					</h2>
				</RouterLink>
				
			</div>
			<TransitionGroup name="fade" tag="div" class="d-flex flex-column gap-3 mb-4">
				<p class="text-muted" 
				   key="noConfiguration"
				   v-if="this.configurationLoaded && this.wireguardConfigurationsStore.Configurations.length === 0">
					<LocaleText t="You don't have any WireGuard configurations yet. Please check the configuration folder or change it in Settings. By default the folder is /etc/wireguard."></LocaleText>
				</p>
				<ConfigurationCard v-for="(c, index) in this.wireguardConfigurationsStore.Configurations"
				                   :delay="index*0.05 + 's'"
				                   v-else-if="this.configurationLoaded"
				                   :key="c.Name" :c="c"></ConfigurationCard>
			</TransitionGroup>
			
		</div>
	</div>
	
</template>

<style scoped>
.configurationListTitle{
	.btn{
		border-radius: 50% !important;
	}
}
</style>