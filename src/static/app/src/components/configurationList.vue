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
			<div class="d-flex mb-4 configurationListTitle">
				<h3 class="text-body d-flex">
					<i class="bi bi-body-text me-2"></i>
					<span>
						<LocaleText t="WireGuard Configurations"></LocaleText>
					</span></h3>
				<RouterLink to="/new_configuration" class="btn btn-dark btn-brand rounded-3 px-3 py-2 shadow ms-auto rounded-3">
					<i class="bi bi-plus-circle-fill me-2"></i>
					<LocaleText t="Configuration"></LocaleText>
				</RouterLink>
			</div>
			<Transition name="fade" mode="out-in">
				<div v-if="this.configurationLoaded">
					<p class="text-muted" v-if="this.wireguardConfigurationsStore.Configurations.length === 0">
						<LocaleText t="You don't have any WireGuard configurations yet. Please check the configuration folder or change it in Settings. By default the folder is /etc/wireguard."></LocaleText>
					</p>
					<div class="d-flex gap-3 flex-column mb-3" v-else>
						<ConfigurationCard v-for="c in this.wireguardConfigurationsStore.Configurations" :key="c.Name" :c="c"></ConfigurationCard>
					</div>
				</div>
			</Transition>
			
		</div>
	</div>
	
</template>

<style scoped>
@media screen and (max-width: 768px) {
	.configurationListTitle{
		flex-direction: column;
		gap: 0.5rem;
		
		h3 span{
			margin-left: auto !important;
		}
		
		.btn{
			width: 100%;
		}
	}
}
</style>