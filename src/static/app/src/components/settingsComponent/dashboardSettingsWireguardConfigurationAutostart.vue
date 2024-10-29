<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {computed, ref} from "vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
const store = DashboardConfigurationStore()
const wireguardConfigurationStore = WireguardConfigurationsStore()
const data = ref(store.Configuration.WireGuardConfiguration.autostart)

const configurations = computed(() => {
	return wireguardConfigurationStore.Configurations.map(x => x.Name)
})
</script>

<template>
<div class="">
	<h5>
		<LocaleText t="Autostart"></LocaleText>
	</h5>
	<div class="d-flex gap-2">
		<button class="btn btn-outline-primary" v-for="c in configurations">
			<i class="bi-circle me-2"></i> {{c}}
		</button>
	</div>
</div>
</template>

<style scoped>

</style>